"""
Command-line interface for Archipel nodes.
"""

import time
from typing import Optional, Callable
import uuid


class CLICommands:
    """Command handler for CLI interface."""
    
    def __init__(self, node_context):
        """
        Initialize CLI with node context.
        
        Args:
            node_context: Node instance with all managers
        """
        self.node = node_context
    
    def handle_command(self, command_input: str):
        """
        Parse and execute a CLI command.
        
        Args:
            command_input: Raw command string (e.g., "msg abc123 Hello")
        """
        parts = command_input.strip().split(maxsplit=1)
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "help":
            self.cmd_help()
        elif cmd == "status":
            self.cmd_status()
        elif cmd == "peers":
            self.cmd_peers()
        elif cmd == "msg":
            self.cmd_msg(args)
        elif cmd == "send":
            self.cmd_send(args)
        elif cmd == "download":
            self.cmd_download_status(args)
        elif cmd == "exit" or cmd == "quit":
            self.cmd_exit()
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")
    
    def cmd_help(self):
        """Show help message."""
        print("""
Archipel Node Commands:
  help              Show this help message
  status            Show node status
  peers             List connected peers
  msg <id> <text>   Send encrypted message to peer (id prefix OK)
  send <id> <file>  Send file to peer
  download          Show download status
  exit              Stop node and exit
        """)
    
    def cmd_status(self):
        """Show node status."""
        if not hasattr(self.node, 'node_id'):
            print("[Status] Node not initialized")
            return
        
        print(f"\nNode Status:")
        print(f"  Node ID:      {self.node.node_id[:16]}...")
        print(f"  Listen Port:  {self.node.tcp_port}")
        print(f"  Peers:        {self.node.peer_table.count_active_peers()}")
        print(f"  Uptime:       {time.time() - self.node.start_time:.0f}s")
    
    def cmd_peers(self):
        """List all known peers."""
        print(f"\nConnected Peers ({self.node.peer_table.count_active_peers()}):")
        print(self.node.peer_table.list_peers())
    
    def cmd_msg(self, args: str):
        """Send encrypted message to a peer."""
        if not args:
            print("Usage: msg <peer_id_prefix> <message>")
            return
        
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print("Usage: msg <peer_id_prefix> <message>")
            return
        
        peer_prefix = parts[0]
        message = parts[1]
        
        # Find peer by prefix
        peer_id = self._find_peer_by_prefix(peer_prefix)
        if not peer_id:
            print(f"Peer not found: {peer_prefix}")
            return
        
        # Send message
        self.node.chat_manager.send_message(peer_id, message)
    
    def cmd_send(self, args: str):
        """Send a file to a peer."""
        if not args:
            print("Usage: send <peer_id_prefix> <file_path>")
            return
        
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print("Usage: send <peer_id_prefix> <file_path>")
            return
        
        peer_prefix = parts[0]
        file_path = parts[1]
        
        # Find peer by prefix
        peer_id = self._find_peer_by_prefix(peer_prefix)
        if not peer_id:
            print(f"Peer not found: {peer_prefix}")
            return
        
        # Send file
        self._send_file(peer_id, file_path)
    
    def cmd_download_status(self, args: str):
        """Show download status."""
        downloader = self.node.file_downloader
        
        if not downloader.sessions:
            print("No active downloads")
            return
        
        print("\nActive Downloads:")
        for file_id, session in downloader.sessions.items():
            progress = session.get_progress()
            print(f"  {session.filename}: {progress:.1f}% ({len(session.chunks)}/{session.total_chunks})")
    
    def cmd_exit(self):
        """Stop the node."""
        print("Stopping node...")
        self.node.stop()
    
    def _find_peer_by_prefix(self, prefix: str) -> Optional[str]:
        """Find a peer by ID prefix."""
        peers = self.node.peer_table.get_all_peers()
        
        matching = [p for p in peers if p.node_id.startswith(prefix)]
        
        if len(matching) == 0:
            return None
        elif len(matching) == 1:
            return matching[0].node_id
        else:
            print(f"Multiple peers match '{prefix}':")
            for p in matching:
                print(f"  {p.node_id}")
            return None
    
    def _send_file(self, peer_id: str, file_path: str):
        """Send a file to a peer."""
        import os
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        try:
            # Get file info
            file_info = self.node.file_chunker.get_file_info(file_path)
            file_id = str(uuid.uuid4())
            
            print(f"[Send] Sending {file_info['filename']} to {peer_id[:8]}...")
            print(f"        Size: {file_info['file_size']} bytes, {file_info['num_chunks']} chunks")
            
            # Send file starter packet
            peer = self.node.peer_table.get_peer(peer_id)
            if not peer:
                print(f"Peer not found: {peer_id}")
                return
            
            # Send chunks
            for chunk_num, chunk_data in self.node.file_chunker.chunk_file(file_path):
                packet = self.node.file_chunker.create_chunk_packet(
                    file_id,
                    chunk_num,
                    chunk_data,
                    file_info['num_chunks']
                )
                packet['filename'] = file_info['filename']
                
                self.node.tcp_client.send_packet(peer.host, peer.port, packet)
                
                progress = ((chunk_num + 1) / file_info['num_chunks']) * 100
                print(f"        Progress: {progress:.1f}%", end='\r')
            
            print(f"        Sent {file_info['num_chunks']} chunks successfully")
        
        except Exception as e:
            print(f"Error sending file: {e}")
