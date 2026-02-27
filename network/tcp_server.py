"""
TCP server for receiving packets (messages, file chunks, etc.) from peers.
"""

import socket
import threading
import json
from typing import Callable, Optional


class TCPServer:
    """Simple TCP server for receiving packets from peers."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 0, on_packet: Optional[Callable] = None):
        """
        Initialize TCP server.
        
        Args:
            host: Bind address
            port: Bind port (0 = auto-assign)
            on_packet: Callback when a packet is received
        """
        self.host = host
        self.port = port
        self.on_packet = on_packet
        self.running = False
        self.socket = None
        self.actual_port = None
    
    def start(self):
        """Start the TCP server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        
        # Get actual port if it was auto-assigned
        self.actual_port = self.socket.getsockname()[1]
        print(f"[TCPServer] Listening on {self.host if self.host else 'all interfaces'}:{self.actual_port}")
        
        self.running = True
        
        # Start accept loop in background thread
        accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        accept_thread.start()
    
    def stop(self):
        """Stop the TCP server."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
    
    def get_port(self) -> int:
        """Get the actual port the server is listening on."""
        return self.actual_port
    
    def _accept_loop(self):
        """Accept incoming connections."""
        while self.running:
            try:
                client_socket, client_addr = self.socket.accept()
                
                # Handle connection in a separate thread
                handler_thread = threading.Thread(
                    target=self._handle_connection,
                    args=(client_socket, client_addr),
                    daemon=True
                )
                handler_thread.start()
            
            except Exception as e:
                if self.running:
                    print(f"[TCPServer] Accept error: {e}")
    
    def _handle_connection(self, client_socket: socket.socket, client_addr):
        """Handle a single client connection."""
        try:
            # Read packet size (4 bytes, big-endian int)
            size_data = client_socket.recv(4)
            if len(size_data) < 4:
                return
            
            packet_size = int.from_bytes(size_data, byteorder='big')
            
            # Read packet data
            packet_data = b''
            while len(packet_data) < packet_size:
                chunk = client_socket.recv(min(4096, packet_size - len(packet_data)))
                if not chunk:
                    break
                packet_data += chunk
            
            # Parse and handle packet
            if len(packet_data) == packet_size:
                try:
                    packet = json.loads(packet_data.decode('utf-8'))
                    if self.on_packet:
                        self.on_packet(
                            packet=packet,
                            remote_addr=client_addr
                        )
                except json.JSONDecodeError:
                    print(f"[TCPServer] Invalid JSON from {client_addr}")
        
        except Exception as e:
            print(f"[TCPServer] Connection error from {client_addr}: {e}")
        
        finally:
            try:
                client_socket.close()
            except:
                pass


class TCPClient:
    """Simple TCP client for sending packets to peers."""
    
    @staticmethod
    def send_packet(host: str, port: int, packet: dict, timeout: int = 5) -> bool:
        """
        Send a packet to a peer.
        
        Args:
            host: Peer's IP address
            port: Peer's port
            packet: Dictionary to send (will be JSON-encoded)
            timeout: Connection timeout in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            
            # Encode packet as JSON
            packet_data = json.dumps(packet).encode('utf-8')
            
            # Send size (4 bytes, big-endian)
            packet_size = len(packet_data)
            sock.sendall(packet_size.to_bytes(4, byteorder='big'))
            
            # Send packet data
            sock.sendall(packet_data)
            
            sock.close()
            return True
        
        except Exception as e:
            print(f"[TCPClient] Failed to send packet to {host}:{port}: {e}")
            return False
