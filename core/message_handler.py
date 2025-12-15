"""
Message handler for processing incoming messages.
"""

import time
from utils.logger import SecureLogger

logger = SecureLogger('message_handler')


class MessageHandler:
    """Handles processing of different message types."""
    
    def __init__(self, crypto_manager, key_manager):
        """
        Initialize message handler.
        
        Args:
            crypto_manager: CryptoManager instance
            key_manager: KeyManager instance
        """
        self.crypto_manager = crypto_manager
        self.key_manager = key_manager
        self.message_callbacks = {}
        self.message_count = 0
        self.session_start_time = time.time()
    
    def register_callback(self, message_type, callback):
        """
        Register a callback for a message type.
        
        Args:
            message_type: Message type to handle
            callback: Function to call when message is received
        """
        self.message_callbacks[message_type] = callback
    
    def handle_text_message(self, encrypted_message, peer_id="peer"):
        """
        Handle incoming text message.
        
        Args:
            encrypted_message: Encrypted message bytes
            peer_id: Peer identifier
            
        Returns:
            str: Decrypted message text
        """
        try:
            plaintext, msg_type, timestamp = self.crypto_manager.decrypt_message(
                encrypted_message,
                sender_id=peer_id.encode() if isinstance(peer_id, str) else peer_id
            )
            
            self.message_count += 1
            
            # Check if rekeying is needed
            if self.should_rekey():
                logger.info("Rekeying threshold reached", event="rekey")
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to decrypt message: {e}", event="decrypt_error")
            raise
    
    def handle_file_chunk(self, encrypted_chunk, chunk_number):
        """
        Handle incoming file chunk.
        
        Args:
            encrypted_chunk: Encrypted chunk bytes
            chunk_number: Chunk sequence number
            
        Returns:
            bytes: Decrypted chunk data
        """
        try:
            chunk_data = self.crypto_manager.decrypt_file_chunk(
                encrypted_chunk,
                chunk_number
            )
            return chunk_data
        except Exception as e:
            logger.error(f"Failed to decrypt file chunk: {e}", event="decrypt_error")
            raise
    
    def prepare_text_message(self, text, sender_id="self"):
        """
        Prepare text message for sending.
        
        Args:
            text: Message text
            sender_id: Sender identifier
            
        Returns:
            bytes: Encrypted message
        """
        try:
            encrypted = self.crypto_manager.encrypt_message(
                text,
                self.crypto_manager.TYPE_TEXT,
                sender_id=sender_id.encode() if isinstance(sender_id, str) else sender_id
            )
            self.message_count += 1
            return encrypted
        except Exception as e:
            logger.error(f"Failed to encrypt message: {e}", event="encrypt_error")
            raise
    
    def prepare_file_chunk(self, chunk, chunk_number):
        """
        Prepare file chunk for sending.
        
        Args:
            chunk: File chunk bytes
            chunk_number: Chunk sequence number
            
        Returns:
            bytes: Encrypted chunk
        """
        try:
            return self.crypto_manager.encrypt_file_chunk(chunk, chunk_number)
        except Exception as e:
            logger.error(f"Failed to encrypt file chunk: {e}", event="encrypt_error")
            raise
    
    def should_rekey(self):
        """
        Check if session should be rekeyed.
        
        Returns:
            bool: True if rekeying is needed
        """
        # Check message count threshold
        if self.message_count >= 1000:
            return True
        
        # Check time threshold (24 hours)
        if time.time() - self.session_start_time >= 86400:
            return True
        
        return False
    
    def reset_session_counters(self):
        """Reset session counters after rekeying."""
        self.message_count = 0
        self.session_start_time = time.time()
