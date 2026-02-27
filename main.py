#!/usr/bin/env python3
"""
Archipel: Decentralized P2P Communication Protocol
Main entry point for running an Archipel node.
"""

import time
import sys
from pathlib import Path

# Import our modules
from crypto.keys import KeyManager
from crypto.cipher import Cipher
from network.discovery import PeerDiscovery
from network.peer_table import PeerTable
from network.tcp_server import TCPServer, TCPClient
from messaging.chat import ChatManager
from transfer.chunker import FileChunker
from transfer.downloader import FileDownloader
from cli.commands import CLICommands


class ArchipelNode:
    """Main Archipel node that coordinates all subsystems."""
    
    def __init__(self, keys_dir: str = "./keys", listen_port: int = 0):
        """
        Initialize the Archipel node.
        
        Args:
            keys_dir: Directory for key storage
            listen_port: TCP port to listen on (0 = auto-assign)
        """
        print("=" * 60)
        print("Archipel - Decentralized P2P Communication")
        print("=" * 60)
        
        self.start_time = time.time()
        self.running = False
        
        # Initialize cryptography
        print("\n[Init] Setting up encryption...")
        self.key_manager = KeyManager(keys_dir)
        self.node_id = self.key_manager.generate_or_load_keys()
        
        # Derive shared encryption key for messages (in real scenario, would exchange keys)
        # For demo purposes, use a simple password-derived key
        self.cipher_key, _ = Cipher.derive_key("archipel_demo_key_123")
        
        # Initialize network components
        print("[Init] Starting TCP server...")
        self.tcp_server = TCPServer(host="0.0.0.0", port=listen_port)
        self.tcp_server.on_packet = self._handle_packet
        self.tcp_server.start()
        self.tcp_port = self.tcp_server.get_port()
        
        print("[Init] Setting up peer discovery...")
        self.peer_table = PeerTable()
        self.discovery = PeerDiscovery(
            node_id=self.node_id,
            node_port=self.tcp_port,
            on_peer_found=self._on_peer_discovered
        )
        self.discovery.start()
        
        # Initialize application components
        print("[Init] Initializing messaging system...")
        self.tcp_client = TCPClient
        self.chat_manager = ChatManager(
            tcp_client_class=TCPClient,
            cipher_key=self.cipher_key,
            peer_table=self.peer_table
        )
        
        print("[Init] Setting up file transfer...")
        self.file_chunker = FileChunker()
        self.file_downloader = FileDownloader()
        
        # Initialize CLI
        self.cli = CLICommands(self)
        
        print(f"\n[Ready] Node {self.node_id[:16]}... is online on port {self.tcp_port}")
        print("[Ready] Type 'help' for available commands\n")
        
        self.running = True
    
    def _on_peer_discovered(self, node_id: str, host: str, port: int):
        """Callback when a peer is discovered."""
        self.peer_table.add_or_update_peer(node_id, host, port)
    
    def _handle_packet(self, packet: dict, remote_addr: tuple):
        """Handle incoming packet from any peer."""
        packet_type = packet.get("type")
        
        if packet_type == "message":
            self.chat_manager.handle_incoming_message(packet, remote_addr)
        elif packet_type == "file_chunk":
            self.file_downloader.handle_chunk_packet(packet)
        else:
            print(f"[Node] Unknown packet type: {packet_type}")
    
    def run_interactive(self):
        """Run interactive CLI."""
        try:
            while self.running:
                try:
                    # Show prompt
                    user_input = input("> ").strip()
                    if user_input:
                        self.cli.handle_command(user_input)
                except KeyboardInterrupt:
                    print("\n")
                    self.cli.cmd_exit()
                    break
        except EOFError:
            self.cli.cmd_exit()
    
    def stop(self):
        """Stop all node operations."""
        print("\n[Stop] Shutting down...")
        self.running = False
        
        if self.discovery:
            self.discovery.stop()
        if self.tcp_server:
            self.tcp_server.stop()
        
        print("[Stop] Goodbye!")
        sys.exit(0)


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Archipel P2P Node")
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="TCP port to listen on (0 = auto-assign)"
    )
    parser.add_argument(
        "--keys",
        type=str,
        default="./keys",
        help="Directory for key storage"
    )
    
    args = parser.parse_args()
    
    # Create and run node
    node = ArchipelNode(keys_dir=args.keys, listen_port=args.port)
    node.run_interactive()


if __name__ == "__main__":
    main()
