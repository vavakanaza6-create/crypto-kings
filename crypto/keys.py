"""
Key generation and management for Archipel nodes.
Uses RSA for asymmetric encryption and AES key derivation.
"""

import os
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class KeyManager:
    """Manages RSA keys for a node."""

    def __init__(self, keys_dir: str = "./keys"):
        """
        Initialize key manager.
        
        Args:
            keys_dir: Directory to store keys
        """
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_path = self.keys_dir / "private_key.pem"
        self.public_key_path = self.keys_dir / "public_key.pem"
        self.node_id_path = self.keys_dir / "node_id.txt"
        
        self.private_key = None
        self.public_key = None
        self.node_id = None
        
    def generate_or_load_keys(self) -> str:
        """
        Generate new RSA keys or load existing ones.
        Returns the node ID (based on public key hash).
        """
        if self.private_key_path.exists() and self.public_key_path.exists():
            self._load_keys()
            print(f"[Keys] Loaded existing keys for node {self.node_id[:8]}...")
        else:
            self._generate_keys()
            print(f"[Keys] Generated new keys for node {self.node_id[:8]}...")
        
        return self.node_id
    
    def _generate_keys(self):
        """Generate new RSA key pair."""
        # Generate 2048-bit RSA key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Save keys to disk
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        self.private_key_path.write_bytes(private_pem)
        
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.public_key_path.write_bytes(public_pem)
        
        # Generate node ID from public key hash
        import hashlib
        self.node_id = hashlib.sha256(public_pem).hexdigest()
        self.node_id_path.write_text(self.node_id)
    
    def _load_keys(self):
        """Load RSA keys from disk."""
        private_pem = self.private_key_path.read_bytes()
        public_pem = self.public_key_path.read_bytes()
        
        self.private_key = serialization.load_pem_private_key(
            private_pem,
            password=None,
            backend=default_backend()
        )
        self.public_key = serialization.load_pem_public_key(
            public_pem,
            backend=default_backend()
        )
        
        self.node_id = self.node_id_path.read_text().strip()
    
    def get_public_key_pem(self) -> str:
        """Return public key as PEM string."""
        if self.public_key is None:
            self.generate_or_load_keys()
        
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    
    def get_node_id(self) -> str:
        """Return the node's unique identifier."""
        if self.node_id is None:
            self.generate_or_load_keys()
        return self.node_id
