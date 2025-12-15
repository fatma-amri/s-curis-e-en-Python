"""
Unit tests for storage functionality.
"""

import unittest
import os
import tempfile
import shutil
from storage.database_manager import DatabaseManager
from storage.conversation_storage import ConversationStorage


class TestStorage(unittest.TestCase):
    """Test storage operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test.db')
        
        # Create database manager
        self.db_manager = DatabaseManager(self.db_path, 'test_password')
        self.conversation_storage = ConversationStorage(self.db_manager)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.db_manager.close()
        shutil.rmtree(self.test_dir)
    
    def test_database_creation(self):
        """Test database creation."""
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_conversation_creation(self):
        """Test conversation creation."""
        fingerprint = "test:fingerprint:12345"
        conv_id = self.db_manager.create_conversation(fingerprint, "Test User")
        
        self.assertIsNotNone(conv_id)
        self.assertGreater(conv_id, 0)
        
        # Test that same fingerprint returns same conversation
        conv_id2 = self.db_manager.create_conversation(fingerprint)
        self.assertEqual(conv_id, conv_id2)
    
    def test_message_insertion(self):
        """Test message insertion."""
        # Create conversation
        fingerprint = "test:fingerprint:67890"
        conv_id = self.conversation_storage.start_conversation(fingerprint)
        
        # Save sent message
        msg_id = self.conversation_storage.save_sent_message("Test message")
        self.assertIsNotNone(msg_id)
        self.assertGreater(msg_id, 0)
        
        # Save received message
        msg_id2 = self.conversation_storage.save_received_message("Received message")
        self.assertIsNotNone(msg_id2)
        self.assertGreater(msg_id2, 0)
    
    def test_message_retrieval(self):
        """Test message retrieval."""
        # Create conversation and add messages
        fingerprint = "test:fingerprint:abcdef"
        conv_id = self.conversation_storage.start_conversation(fingerprint)
        
        self.conversation_storage.save_sent_message("Message 1")
        self.conversation_storage.save_received_message("Message 2")
        self.conversation_storage.save_sent_message("Message 3")
        
        # Retrieve messages
        messages = self.conversation_storage.get_conversation_messages()
        
        self.assertEqual(len(messages), 3)
        
        # Check message order (should be newest first)
        self.assertEqual(messages[0]['content'], "Message 3")
        self.assertEqual(messages[1]['content'], "Message 2")
        self.assertEqual(messages[2]['content'], "Message 1")
    
    def test_encryption_decryption(self):
        """Test message encryption in storage."""
        # Create conversation
        fingerprint = "test:fingerprint:encrypted"
        conv_id = self.conversation_storage.start_conversation(fingerprint)
        
        # Save message with sensitive content
        sensitive_message = "This is a secret message"
        msg_id = self.conversation_storage.save_sent_message(sensitive_message)
        
        # Retrieve and verify
        messages = self.conversation_storage.get_conversation_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['content'], sensitive_message)
    
    def test_concurrent_access(self):
        """Test concurrent database access."""
        import threading
        
        results = []
        errors = []
        
        def write_message(n):
            try:
                conv_id = self.db_manager.create_conversation(f"test:user:{n}")
                msg_id = self.db_manager.save_message(
                    conv_id, 'sent', f"Message {n}"
                )
                results.append(msg_id)
            except Exception as e:
                errors.append(str(e))
                results.append(None)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=write_message, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Check that most messages were saved (some may fail due to SQLite locking)
        successful = sum(1 for r in results if r is not None)
        self.assertGreaterEqual(successful, 5)  # At least half should succeed
    
    def test_contact_key_storage(self):
        """Test contact key storage and retrieval."""
        fingerprint = "aa:bb:cc:dd:ee:ff"
        public_key = b"test_public_key_data"
        
        # Store key
        self.db_manager.store_contact_key(fingerprint, public_key, "Test Contact")
        
        # Retrieve key
        retrieved_key = self.db_manager.get_contact_key(fingerprint)
        
        self.assertIsNotNone(retrieved_key)
        self.assertEqual(retrieved_key, public_key)


if __name__ == '__main__':
    unittest.main()
