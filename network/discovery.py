"""
Peer discovery using UDP multicast on local network.
Nodes broadcast their presence and listen for other nodes.
"""

import socket
import json
import threading
import time
from typing import Callable, Optional


class PeerDiscovery:
    """UDP multicast-based peer discovery."""
    
    # Multicast group and port
    MULTICAST_GROUP = "224.0.0.1"
    MULTICAST_PORT = 5555
    
    def __init__(self, node_id: str, node_port: int, on_peer_found: Optional[Callable] = None):
        """
        Initialize peer discovery.
        
        Args:
            node_id: This node's unique identifier
            node_port: TCP port this node listens on
            on_peer_found: Callback when a peer is discovered
        """
        self.node_id = node_id
        self.node_port = node_port
        self.on_peer_found = on_peer_found
        self.running = False
        self.socket = None
        self.discovery_thread = None
    
    def start(self):
        """Start broadcasting and listening for peers."""
        self.running = True
        
        # Start broadcast thread
        self.discovery_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self.discovery_thread.start()
        
        # Start listen thread
        listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        listen_thread.start()
        
        print(f"[Discovery] Node {self.node_id[:8]}... started broadcasting on {self.MULTICAST_GROUP}:{self.MULTICAST_PORT}")
    
    def stop(self):
        """Stop discovery."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
    
    def _broadcast_loop(self):
        """Periodically broadcast this node's presence."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        
        while self.running:
            try:
                # Build announcement packet
                announcement = {
                    "type": "peer_announcement",
                    "node_id": self.node_id,
                    "port": self.node_port,
                    "timestamp": time.time()
                }
                
                packet = json.dumps(announcement).encode('utf-8')
                sock.sendto(packet, (self.MULTICAST_GROUP, self.MULTICAST_PORT))
                
            except Exception as e:
                print(f"[Discovery] Broadcast error: {e}")
            
            # Broadcast every 5 seconds
            time.sleep(5)
        
        sock.close()
    
    def _listen_loop(self):
        """Listen for peer announcements on multicast group."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind to multicast port
        sock.bind(('', self.MULTICAST_PORT))
        
        # Join multicast group
        mreq = socket.inet_aton(self.MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        sock.settimeout(2)
        self.socket = sock
        
        while self.running:
            try:
                packet, addr = sock.recvfrom(1024)
                announcement = json.loads(packet.decode('utf-8'))
                
                # Ignore our own announcements
                if announcement.get("node_id") != self.node_id:
                    if self.on_peer_found:
                        self.on_peer_found(
                            node_id=announcement.get("node_id"),
                            host=addr[0],
                            port=announcement.get("port")
                        )
            
            except socket.timeout:
                pass
            except json.JSONDecodeError:
                pass
            except Exception as e:
                if self.running:
                    print(f"[Discovery] Listen error: {e}")
        
        sock.close()
