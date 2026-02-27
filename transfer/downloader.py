"""
File download management.
Receives chunks and reassembles files.
"""

import os
from pathlib import Path
from typing import Dict, Optional
import base64
import hashlib


class DownloadSession:
    """Manages a single file download session."""
    
    def __init__(self, file_id: str, filename: str, total_chunks: int):
        """
        Initialize download session.
        
        Args:
            file_id: Unique file identifier
            filename: Name of file being downloaded
            total_chunks: Total number of chunks expected
        """
        self.file_id = file_id
        self.filename = filename
        self.total_chunks = total_chunks
        self.chunks: Dict[int, bytes] = {}
        self.hash = hashlib.sha256()
    
    def add_chunk(self, chunk_num: int, chunk_data: bytes) -> bool:
        """
        Add a received chunk.
        
        Args:
            chunk_num: Chunk number
            chunk_data: Chunk data
            
        Returns:
            True if chunk was added (new), False if already received
        """
        if chunk_num in self.chunks:
            return False
        
        self.chunks[chunk_num] = chunk_data
        return True
    
    def is_complete(self) -> bool:
        """Check if all chunks have been received."""
        return len(self.chunks) == self.total_chunks
    
    def get_progress(self) -> float:
        """Get download progress as percentage."""
        if self.total_chunks == 0:
            return 0.0
        return (len(self.chunks) / self.total_chunks) * 100
    
    def assemble(self, output_dir: str = ".") -> str:
        """
        Assemble all chunks into a file.
        
        Args:
            output_dir: Directory to save file
            
        Returns:
            Path to the saved file
            
        Raises:
            ValueError: If download is not complete
        """
        if not self.is_complete():
            raise ValueError(f"Download incomplete: {len(self.chunks)}/{self.total_chunks} chunks")
        
        output_path = Path(output_dir) / self.filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write chunks in order
        with open(output_path, 'wb') as f:
            for i in range(self.total_chunks):
                f.write(self.chunks[i])
        
        return str(output_path)


class FileDownloader:
    """Manages multiple file download sessions."""
    
    def __init__(self, download_dir: str = "./downloads"):
        """
        Initialize downloader.
        
        Args:
            download_dir: Directory to save downloaded files
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, DownloadSession] = {}
    
    def start_download(self, file_id: str, filename: str, total_chunks: int) -> DownloadSession:
        """
        Start a new download session.
        
        Args:
            file_id: Unique file identifier
            filename: Name of file
            total_chunks: Total number of chunks
            
        Returns:
            DownloadSession object
        """
        session = DownloadSession(file_id, filename, total_chunks)
        self.sessions[file_id] = session
        print(f"[Download] Starting download: {filename} ({total_chunks} chunks)")
        return session
    
    def receive_chunk(self, file_id: str, chunk_num: int, chunk_data: bytes) -> bool:
        """
        Receive a chunk for an active download.
        
        Args:
            file_id: File identifier
            chunk_num: Chunk number
            chunk_data: Chunk data
            
        Returns:
            True if chunk was new, False if duplicate or unknown file
        """
        if file_id not in self.sessions:
            return False
        
        session = self.sessions[file_id]
        result = session.add_chunk(chunk_num, chunk_data)
        
        if result:
            progress = session.get_progress()
            print(f"[Download] {session.filename}: {progress:.1f}% ({len(session.chunks)}/{session.total_chunks})")
            
            # Check if download is complete
            if session.is_complete():
                self._complete_download(file_id)
        
        return result
    
    def _complete_download(self, file_id: str):
        """Finalize a completed download."""
        session = self.sessions[file_id]
        
        try:
            output_file = session.assemble(str(self.download_dir))
            print(f"[Download] Completed: {output_file}")
        except Exception as e:
            print(f"[Download] Failed to assemble {session.filename}: {e}")
    
    def get_session(self, file_id: str) -> Optional[DownloadSession]:
        """Get a download session by ID."""
        return self.sessions.get(file_id)
    
    def handle_chunk_packet(self, packet: dict) -> bool:
        """
        Handle an incoming file chunk packet.
        
        Args:
            packet: Received packet dictionary
            
        Returns:
            True if chunk was processed
        """
        if packet.get("type") != "file_chunk":
            return False
        
        try:
            file_id = packet.get("file_id")
            chunk_num = packet.get("chunk_num")
            total_chunks = packet.get("total_chunks")
            data_b64 = packet.get("data")
            
            # Decode base64 data
            chunk_data = base64.b64decode(data_b64)
            
            # Start session if needed
            if file_id not in self.sessions:
                # Try to guess filename from packet or use generic name
                filename = packet.get("filename", f"file_{file_id[:8]}")
                self.start_download(file_id, filename, total_chunks)
            
            # Receive the chunk
            return self.receive_chunk(file_id, chunk_num, chunk_data)
        
        except Exception as e:
            print(f"[Download] Error processing chunk packet: {e}")
            return False
