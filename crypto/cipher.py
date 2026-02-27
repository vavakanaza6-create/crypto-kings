"""
Encryption/decryption using AES-256-GCM for authenticated encryption.
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class Cipher:
    """AES-256-GCM encryption/decryption."""
    
    # AES key size (256-bit = 32 bytes)
    KEY_SIZE = 32
    # Nonce size for GCM (96-bit / 12 bytes is standard)
    NONCE_SIZE = 12
    
    @staticmethod
    def derive_key(password: str, salt: bytes = None) -> tuple:
        """
        Derive AES key from password using PBKDF2.
        
        Args:
            password: The password to derive from
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=Cipher.KEY_SIZE,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        return key, salt
    
    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> bytes:
        """
        Encrypt plaintext using AES-256-GCM.
        
        Args:
            plaintext: Data to encrypt
            key: 32-byte AES key
            
        Returns:
            nonce + tag + ciphertext (all concatenated)
        """
        nonce = os.urandom(Cipher.NONCE_SIZE)
        cipher = AESGCM(key)
        
        # GCM returns ciphertext + authentication tag
        ciphertext = cipher.encrypt(nonce, plaintext, None)
        
        # Return nonce + ciphertext (which includes the tag)
        return nonce + ciphertext
    
    @staticmethod
    def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
        """
        Decrypt data encrypted with encrypt().
        
        Args:
            encrypted_data: nonce + ciphertext (from encrypt)
            key: 32-byte AES key
            
        Returns:
            Decrypted plaintext
            
        Raises:
            cryptography.exceptions.InvalidTag: If authentication fails
        """
        nonce = encrypted_data[:Cipher.NONCE_SIZE]
        ciphertext = encrypted_data[Cipher.NONCE_SIZE:]
        
        cipher = AESGCM(key)
        plaintext = cipher.decrypt(nonce, ciphertext, None)
        
        return plaintext
    
    @staticmethod
    def encrypt_message(message: str, key: bytes) -> str:
        """
        Encrypt a text message and return as hex string.
        
        Args:
            message: Text message
            key: 32-byte AES key
            
        Returns:
            Hex-encoded encrypted data
        """
        encrypted = Cipher.encrypt(message.encode('utf-8'), key)
        return encrypted.hex()
    
    @staticmethod
    def decrypt_message(encrypted_hex: str, key: bytes) -> str:
        """
        Decrypt a hex-encoded encrypted message.
        
        Args:
            encrypted_hex: Hex-encoded ciphertext from encrypt_message
            key: 32-byte AES key
            
        Returns:
            Decrypted text message
        """
        encrypted_data = bytes.fromhex(encrypted_hex)
        plaintext = Cipher.decrypt(encrypted_data, key)
        return plaintext.decode('utf-8')
