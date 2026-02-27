"""
Encrypted messaging between peers.
Sends encrypted text messages via TCP to peers.
"""

from typing import Optional, Callable
from crypto.cipher import Cipher


class ChatManager:
    """Manages encrypted text messages."""
    
    def __init__(self, tcp_client_class, cipher_key: bytes, peer_table):
        """
        Initialize chat manager.
        
        Args:
            tcp_client_class: TCPClient class for sending
            cipher_key: AES key for encryption
            peer_table: PeerTable instance for peer lookup
        """
        self.tcp_client = tcp_client_class
        self.cipher_key = cipher_key
        self.peer_table = peer_table
        self.on_message = None
    
    def send_message(self, recipient_id: str, message: str) -> bool:
        """
        Send an encrypted message to a peer.
        
        Args:
            recipient_id: Node ID of recipient
            message: Text message to send
            
        Returns:
            True if sent successfully
        """
        # Look up recipient in peer table
        peer = self.peer_table.get_peer(recipient_id)
        if not peer:
            print(f"[Chat] Peer {recipient_id[:8]}... not found")
            return False
        
        # Encrypt message
        encrypted = Cipher.encrypt_message(message, self.cipher_key)
        
        # Build packet
        packet = {
            "type": "message",
            "content": encrypted,
            "subject": "encrypted_text"
        }
        
        # Send via TCP
        success = self.tcp_client.send_packet(peer.host, peer.port, packet)
        
        if success:
            print(f"[Chat] Message sent to {recipient_id[:8]}...")
        
        return success
    
    def handle_incoming_message(self, packet: dict, sender_addr: tuple):
        """
        Handle an incoming encrypted message.
        
        Args:
            packet: Received packet
            sender_addr: Sender's address (IP, port)
        """
        if packet.get("type") != "message":
            return
        
        if packet.get("subject") != "encrypted_text":
            return
        
        try:
            encrypted_content = packet.get("content")
            plaintext = Cipher.decrypt_message(encrypted_content, self.cipher_key)
            
            print(f"\n[Chat] Message from {sender_addr[0]}:{sender_addr[1]}")
            print(f"> {plaintext}")
            print("> ", end="", flush=True)
            
            if self.on_message:
                self.on_message(plaintext, sender_addr)
        
        except Exception as e:
            print(f"[Chat] Failed to decrypt message: {e}")


class MessageBuffer:
    """Buffer for storing received messages."""
    
    def __init__(self):
        self.messages = []
    
    def add(self, message: str, sender: str, timestamp: float):
        """Add a message to the buffer."""
        self.messages.append({
            "message": message,
            "sender": sender,
            "timestamp": timestamp
        })
    
    def get_all(self) -> list:
        """Get all messages."""
        return self.messages
    
    def clear(self):
        """Clear all messages."""
        self.messages = []
