"""
File chunking for transfers.
Splits large files into smaller chunks for transmission.
"""

from pathlib import Path
from typing import Iterator, Tuple


class FileChunker:
    """Splits files into chunks for transmission."""
    
    # Default chunk size: 64 KB
    DEFAULT_CHUNK_SIZE = 64 * 1024
    
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Size of each chunk in bytes
        """
        self.chunk_size = chunk_size
    
    def chunk_file(self, file_path: str) -> Iterator[Tuple[int, bytes]]:
        """
        Read file and yield chunks.
        
        Args:
            file_path: Path to file
            
        Yields:
            Tuple of (chunk_number, chunk_data)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        chunk_num = 0
        with open(file_path, 'rb') as f:
            while True:
                chunk_data = f.read(self.chunk_size)
                if not chunk_data:
                    break
                
                yield chunk_num, chunk_data
                chunk_num += 1
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = file_path.stat().st_size
        num_chunks = (file_size + self.chunk_size - 1) // self.chunk_size
        
        return {
            "filename": file_path.name,
            "file_size": file_size,
            "num_chunks": num_chunks,
            "chunk_size": self.chunk_size
        }
    
    @staticmethod
    def create_chunk_packet(file_id: str, chunk_num: int, chunk_data: bytes, total_chunks: int) -> dict:
        """
        Create a file transfer packet for a chunk.
        
        Args:
            file_id: Unique file identifier
            chunk_num: Chunk number (0-indexed)
            chunk_data: Raw chunk data
            total_chunks: Total number of chunks
            
        Returns:
            Dictionary packet ready to send
        """
        import base64
        
        return {
            "type": "file_chunk",
            "file_id": file_id,
            "chunk_num": chunk_num,
            "total_chunks": total_chunks,
            "data": base64.b64encode(chunk_data).decode('utf-8')
        }
