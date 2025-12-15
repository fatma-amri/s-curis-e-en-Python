"""
Cryptography manager for message encryption and decryption.
Uses ChaCha20-Poly1305 AEAD for secure message encryption.
"""

import secrets
import struct
import time
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import gc

from utils.logger import SecureLogger

logger = SecureLogger('crypto_manager')


class CryptoManager:
    """Manages encryption and decryption of messages."""
    
    # Message format constants
    VERSION = 1
    TYPE_TEXT = 1
    TYPE_FILE = 2
    TYPE_HANDSHAKE = 3
    
    def __init__(self):
        """Initialize crypto manager."""
        self.session_key = None
        self.cipher = None
        self.nonce_counter = 0
        self.used_nonces = set()
    
    def set_session_key(self, session_key):
        """
        Set the session key for encryption/decryption.
        
        Args:
            session_key: 32-byte session key
        """
        self.session_key = session_key
        self.cipher = ChaCha20Poly1305(session_key)
        self.nonce_counter = 0
        self.used_nonces.clear()
        logger.info("Session key set", event="session_key_set")
    
    def generate_nonce(self):
        """
        Generate a unique nonce for encryption.
        
        Returns:
            bytes: 12-byte nonce
        """
        while True:
            nonce = secrets.token_bytes(12)
            if nonce not in self.used_nonces:
                self.used_nonces.add(nonce)
                self.nonce_counter += 1
                return nonce
    
    def encrypt_message(self, plaintext, message_type=TYPE_TEXT, sender_id=b"self"):
        """
        Encrypt a message using ChaCha20-Poly1305.
        
        Format: [VERSION:1][TYPE:1][NONCE:12][CIPHERTEXT:variable][TAG:16]
        
        Args:
            plaintext: Message to encrypt (bytes or string)
            message_type: Type of message (TYPE_TEXT or TYPE_FILE)
            sender_id: Sender identifier for AAD
            
        Returns:
            bytes: Encrypted message with header
        """
        if self.cipher is None:
            raise ValueError("Session key not set")
        
        # Convert string to bytes if necessary
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Generate unique nonce
        nonce = self.generate_nonce()
        
        # Create associated data (AAD) with timestamp and sender
        timestamp = struct.pack('>Q', int(time.time()))
        aad = timestamp + sender_id
        
        # Encrypt
        ciphertext = self.cipher.encrypt(nonce, plaintext, aad)
        
        # Build message: [VERSION][TYPE][NONCE][CIPHERTEXT+TAG]
        message = struct.pack('BB', self.VERSION, message_type) + nonce + ciphertext
        
        logger.debug(f"Encrypted message of {len(plaintext)} bytes", event="encrypt")
        return message
    
    def decrypt_message(self, encrypted_message, sender_id=b"peer"):
        """
        Decrypt a message using ChaCha20-Poly1305.
        
        Args:
            encrypted_message: Encrypted message bytes
            sender_id: Sender identifier for AAD verification
            
        Returns:
            tuple: (plaintext bytes, message_type, timestamp)
        """
        if self.cipher is None:
            raise ValueError("Session key not set")
        
        if len(encrypted_message) < 30:  # VERSION(1) + TYPE(1) + NONCE(12) + TAG(16)
            raise ValueError("Message too short")
        
        # Parse message header
        version = encrypted_message[0]
        message_type = encrypted_message[1]
        nonce = encrypted_message[2:14]
        ciphertext = encrypted_message[14:]
        
        if version != self.VERSION:
            raise ValueError(f"Unsupported message version: {version}")
        
        # Check for nonce reuse (replay attack protection)
        if nonce in self.used_nonces:
            logger.warning("Nonce reuse detected - possible replay attack", event="security")
            raise ValueError("Nonce reuse detected")
        
        # Extract timestamp from ciphertext (first 8 bytes of AAD are in the tag verification)
        # We need to try decryption with different timestamp values
        # For simplicity, we'll use current time range
        current_time = int(time.time())
        
        # Try timestamps within a reasonable window (±5 minutes)
        plaintext = None
        actual_timestamp = None
        
        for time_offset in range(-300, 301, 60):
            try:
                test_timestamp = current_time + time_offset
                timestamp_bytes = struct.pack('>Q', test_timestamp)
                aad = timestamp_bytes + sender_id
                
                plaintext = self.cipher.decrypt(nonce, ciphertext, aad)
                actual_timestamp = test_timestamp
                break
            except Exception:
                continue
        
        if plaintext is None:
            raise ValueError("Decryption failed - invalid message or key")
        
        self.used_nonces.add(nonce)
        
        logger.debug(f"Decrypted message of {len(plaintext)} bytes", event="decrypt")
        return plaintext, message_type, actual_timestamp
    
    def encrypt_file_chunk(self, chunk, chunk_number):
        """
        Encrypt a file chunk.
        
        Args:
            chunk: File chunk bytes
            chunk_number: Chunk sequence number
            
        Returns:
            bytes: Encrypted chunk
        """
        # Use chunk number in AAD for ordering
        chunk_id = struct.pack('>I', chunk_number)
        return self.encrypt_message(chunk, self.TYPE_FILE, sender_id=chunk_id)
    
    def decrypt_file_chunk(self, encrypted_chunk, chunk_number):
        """
        Decrypt a file chunk.
        
        Args:
            encrypted_chunk: Encrypted chunk bytes
            chunk_number: Expected chunk sequence number
            
        Returns:
            bytes: Decrypted chunk
        """
        chunk_id = struct.pack('>I', chunk_number)
        plaintext, msg_type, _ = self.decrypt_message(encrypted_chunk, sender_id=chunk_id)
        
        if msg_type != self.TYPE_FILE:
            raise ValueError("Invalid message type for file chunk")
        
        return plaintext
    
    def clear_session(self):
        """Clear session key and cipher from memory."""
        if self.session_key:
            self.session_key = bytearray(self.session_key)
            for i in range(len(self.session_key)):
                self.session_key[i] = 0
            self.session_key = None
        
        self.cipher = None
        self.nonce_counter = 0
        self.used_nonces.clear()
        gc.collect()
        logger.info("Session cleared", event="session_clear")
