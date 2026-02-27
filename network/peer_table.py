"""
Peer table: maintains a list of known peers on the network.
"""

import time
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class Peer:
    """Represents a peer on the network."""
    node_id: str
    host: str
    port: int
    last_seen: float = None
    
    def __post_init__(self):
        if self.last_seen is None:
            self.last_seen = time.time()
    
    def update_last_seen(self):
        """Update the last time this peer was seen."""
        self.last_seen = time.time()
    
    def is_stale(self, timeout: int = 30) -> bool:
        """Check if peer is stale (not seen for timeout seconds)."""
        return time.time() - self.last_seen > timeout


class PeerTable:
    """Manages a table of known peers."""
    
    def __init__(self, stale_timeout: int = 30):
        """
        Initialize peer table.
        
        Args:
            stale_timeout: Remove peers not seen for this many seconds
        """
        self.peers: Dict[str, Peer] = {}
        self.stale_timeout = stale_timeout
    
    def add_or_update_peer(self, node_id: str, host: str, port: int):
        """
        Add a new peer or update an existing one.
        
        Args:
            node_id: Peer's unique identifier
            host: Peer's IP address
            port: Peer's TCP port
        """
        if node_id in self.peers:
            self.peers[node_id].update_last_seen()
        else:
            self.peers[node_id] = Peer(node_id, host, port)
            print(f"[PeerTable] New peer discovered: {node_id[:8]}... at {host}:{port}")
    
    def get_peer(self, node_id: str) -> Optional[Peer]:
        """
        Get a peer by node ID.
        
        Args:
            node_id: The peer's node ID
            
        Returns:
            Peer object or None if not found
        """
        return self.peers.get(node_id)
    
    def get_all_peers(self) -> List[Peer]:
        """Get all active peers, removing stale ones."""
        # Remove stale peers
        stale_ids = [
            node_id for node_id, peer in self.peers.items()
            if peer.is_stale(self.stale_timeout)
        ]
        for node_id in stale_ids:
            del self.peers[node_id]
            print(f"[PeerTable] Peer {node_id[:8]}... removed (stale)")
        
        return list(self.peers.values())
    
    def remove_peer(self, node_id: str):
        """Remove a peer from the table."""
        if node_id in self.peers:
            del self.peers[node_id]
            print(f"[PeerTable] Peer {node_id[:8]}... removed")
    
    def count_active_peers(self) -> int:
        """Get the number of active peers."""
        return len(self.get_all_peers())
    
    def list_peers(self) -> str:
        """Return a formatted string of all active peers."""
        peers = self.get_all_peers()
        if not peers:
            return "No peers found"
        
        lines = []
        for peer in peers:
            lines.append(f"  {peer.node_id[:8]}... | {peer.host}:{peer.port}")
        return "\n".join(lines)
