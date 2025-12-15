"""
Unit tests for cryptographic functions.
"""

import unittest
import secrets
from core.key_manager import KeyManager
from core.crypto_manager import CryptoManager


class TestCrypto(unittest.TestCase):
    """Test cryptographic operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.key_manager = KeyManager()
        self.crypto_manager = CryptoManager()
    
    def test_key_generation(self):
        """Test key generation."""
        # Generate identity keys
        identity_public = self.key_manager.generate_identity_keys()
        self.assertIsNotNone(identity_public)
        self.assertIsNotNone(self.key_manager.identity_private)
        
        # Generate signing keys
        signing_public = self.key_manager.generate_signing_keys()
        self.assertIsNotNone(signing_public)
        self.assertIsNotNone(self.key_manager.signing_private)
    
    def test_ecdh_key_exchange(self):
        """Test ECDH key exchange."""
        # Create two key managers (Alice and Bob)
        alice = KeyManager()
        bob = KeyManager()
        
        alice.generate_identity_keys()
        bob.generate_identity_keys()
        
        # Perform key exchange
        alice_public = alice.get_identity_public_bytes()
        bob_public = bob.get_identity_public_bytes()
        
        alice_shared = alice.perform_key_exchange(bob_public)
        bob_shared = bob.perform_key_exchange(alice_public)
        
        # Shared secrets should be equal
        self.assertEqual(alice_shared, bob_shared)
    
    def test_message_encryption_decryption(self):
        """Test message encryption and decryption."""
        # Set up session key
        session_key = secrets.token_bytes(32)
        self.crypto_manager.set_session_key(session_key)
        
        # Test message
        plaintext = "Hello, secure world!"
        
        # Encrypt
        encrypted = self.crypto_manager.encrypt_message(plaintext)
        self.assertIsNotNone(encrypted)
        self.assertNotEqual(encrypted, plaintext.encode())
        
        # Decrypt with same sender_id
        decrypted, msg_type, timestamp = self.crypto_manager.decrypt_message(
            encrypted, 
            sender_id=b"self"
        )
        self.assertEqual(decrypted.decode('utf-8'), plaintext)
        self.assertEqual(msg_type, CryptoManager.TYPE_TEXT)
    
    def test_signature_verification(self):
        """Test signature creation and verification."""
        self.key_manager.generate_signing_keys()
        
        data = b"Test data to sign"
        
        # Sign data
        signature = self.key_manager.sign_data(data)
        self.assertIsNotNone(signature)
        
        # Verify signature
        public_key = self.key_manager.get_signing_public_bytes()
        is_valid = self.key_manager.verify_signature(data, signature, public_key)
        self.assertTrue(is_valid)
        
        # Verify with wrong data should fail
        wrong_data = b"Different data"
        is_valid = self.key_manager.verify_signature(wrong_data, signature, public_key)
        self.assertFalse(is_valid)
    
    def test_nonce_uniqueness(self):
        """Test that nonces are unique."""
        session_key = secrets.token_bytes(32)
        self.crypto_manager.set_session_key(session_key)
        
        nonces = set()
        for _ in range(100):
            nonce = self.crypto_manager.generate_nonce()
            self.assertNotIn(nonce, nonces)
            nonces.add(nonce)
    
    def test_key_derivation_consistency(self):
        """Test that key derivation is consistent."""
        self.key_manager.generate_identity_keys()
        
        shared_secret = secrets.token_bytes(32)
        salt = secrets.token_bytes(32)
        
        # Derive key twice with same inputs
        key1 = self.key_manager.derive_session_key(shared_secret, salt)
        key2 = self.key_manager.derive_session_key(shared_secret, salt)
        
        self.assertEqual(key1, key2)
        
        # Different salt should give different key
        salt2 = secrets.token_bytes(32)
        key3 = self.key_manager.derive_session_key(shared_secret, salt2)
        self.assertNotEqual(key1, key3)


if __name__ == '__main__':
    unittest.main()
