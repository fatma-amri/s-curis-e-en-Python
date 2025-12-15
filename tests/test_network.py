"""
Unit tests for network functionality.
"""

import unittest
import time
import threading
from core.key_manager import KeyManager
from core.crypto_manager import CryptoManager
from core.message_handler import MessageHandler
from core.network_manager import NetworkManager


class TestNetwork(unittest.TestCase):
    """Test network operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create managers for server
        self.server_key_manager = KeyManager()
        self.server_key_manager.generate_identity_keys()
        self.server_key_manager.generate_signing_keys()
        
        self.server_crypto = CryptoManager()
        self.server_handler = MessageHandler(self.server_crypto, self.server_key_manager)
        
        # Create managers for client
        self.client_key_manager = KeyManager()
        self.client_key_manager.generate_identity_keys()
        self.client_key_manager.generate_signing_keys()
        
        self.client_crypto = CryptoManager()
        self.client_handler = MessageHandler(self.client_crypto, self.client_key_manager)
    
    def test_socket_creation(self):
        """Test socket creation."""
        network = NetworkManager(
            self.server_key_manager,
            self.server_crypto,
            self.server_handler
        )
        
        success = network.start_server(port=5556)
        self.assertTrue(success)
        
        network.disconnect()
    
    def test_connection_establishment(self):
        """Test connection establishment."""
        # Start server
        server_network = NetworkManager(
            self.server_key_manager,
            self.server_crypto,
            self.server_handler
        )
        
        server_network.start_server(port=5557)
        
        # Give server time to start
        time.sleep(0.5)
        
        # Connect client
        client_network = NetworkManager(
            self.client_key_manager,
            self.client_crypto,
            self.client_handler
        )
        
        success = client_network.connect_to_peer('127.0.0.1', 5557)
        self.assertTrue(success)
        
        # Give time for handshake
        time.sleep(2)
        
        # Check connection status
        self.assertTrue(client_network.is_connected)
        
        # Cleanup
        client_network.disconnect()
        server_network.disconnect()
    
    def test_message_send_receive(self):
        """Test sending and receiving messages."""
        received_messages = []
        
        def on_message(text):
            received_messages.append(text)
        
        # Start server
        server_network = NetworkManager(
            self.server_key_manager,
            self.server_crypto,
            self.server_handler
        )
        
        server_network.register_callback('text_message', on_message)
        server_network.start_server(port=5558)
        
        time.sleep(0.5)
        
        # Connect client
        client_network = NetworkManager(
            self.client_key_manager,
            self.client_crypto,
            self.client_handler
        )
        
        client_network.connect_to_peer('127.0.0.1', 5558)
        
        # Wait for handshake
        time.sleep(2)
        
        # Send message
        test_message = "Hello from test!"
        client_network.send_text_message(test_message)
        
        # Wait for message to be received
        time.sleep(1)
        
        # Check if message was received
        self.assertGreater(len(received_messages), 0)
        self.assertEqual(received_messages[0], test_message)
        
        # Cleanup
        client_network.disconnect()
        server_network.disconnect()
    
    def test_connection_timeout(self):
        """Test connection timeout."""
        client_network = NetworkManager(
            self.client_key_manager,
            self.client_crypto,
            self.client_handler
        )
        
        # Try to connect to non-existent server
        success = client_network.connect_to_peer('127.0.0.1', 9999)
        
        # Should fail
        self.assertFalse(success)
    
    def test_disconnection_handling(self):
        """Test disconnection handling."""
        # Start server
        server_network = NetworkManager(
            self.server_key_manager,
            self.server_crypto,
            self.server_handler
        )
        
        server_network.start_server(port=5559)
        time.sleep(0.5)
        
        # Connect client
        client_network = NetworkManager(
            self.client_key_manager,
            self.client_crypto,
            self.client_handler
        )
        
        client_network.connect_to_peer('127.0.0.1', 5559)
        time.sleep(2)
        
        self.assertTrue(client_network.is_connected)
        
        # Disconnect
        client_network.disconnect()
        time.sleep(0.5)
        
        self.assertFalse(client_network.is_connected)
        
        # Cleanup
        server_network.disconnect()


if __name__ == '__main__':
    unittest.main()
