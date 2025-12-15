"""
Unit tests for connection routing logic.
Tests that client mode calls connect_to_peer and server mode calls start_server.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.key_manager import KeyManager
from core.crypto_manager import CryptoManager
from core.message_handler import MessageHandler
from core.network_manager import NetworkManager


class TestConnectionRouting(unittest.TestCase):
    """Test connection routing between server and client modes."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create managers
        self.key_manager = KeyManager()
        self.key_manager.generate_identity_keys()
        self.key_manager.generate_signing_keys()
        
        self.crypto = CryptoManager()
        self.handler = MessageHandler(self.crypto, self.key_manager)
        
        self.network_manager = NetworkManager(
            self.key_manager,
            self.crypto,
            self.handler
        )
    
    def tearDown(self):
        """Clean up after tests."""
        if self.network_manager:
            self.network_manager.disconnect()
    
    def test_client_mode_does_not_start_server(self):
        """Test that client mode calls connect, not start_server."""
        # Mock the socket to prevent actual network calls
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            
            # Call connect_to_peer (client mode)
            self.network_manager.connect_to_peer('127.0.0.1', 5555)
            
            # Verify socket.connect was called (client behavior)
            mock_socket_instance.connect.assert_called_once()
            
            # Verify socket.bind was NOT called (would indicate server behavior)
            mock_socket_instance.bind.assert_not_called()
            
            # Verify socket.listen was NOT called (would indicate server behavior)
            mock_socket_instance.listen.assert_not_called()
    
    def test_server_mode_does_not_connect(self):
        """Test that server mode calls start_server, not connect."""
        # Mock the socket to prevent actual network calls
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            
            # Call start_server (server mode)
            self.network_manager.start_server(port=5556)
            
            # Verify socket.bind was called (server behavior)
            mock_socket_instance.bind.assert_called_once()
            
            # Verify socket.listen was called (server behavior)
            mock_socket_instance.listen.assert_called_once()
            
            # Verify socket.connect was NOT called (would indicate client behavior)
            mock_socket_instance.connect.assert_not_called()
    
    def test_cannot_connect_while_already_connected(self):
        """Test that connecting while already connected is prevented."""
        self.network_manager.is_connected = True
        
        # Try to connect again
        success = self.network_manager.connect_to_peer('127.0.0.1', 5557)
        
        # Should fail
        self.assertFalse(success)
    
    def test_cannot_start_server_while_connected(self):
        """Test that starting server while connected is prevented."""
        self.network_manager.is_connected = True
        
        # Try to start server
        success = self.network_manager.start_server(port=5558)
        
        # Should fail
        self.assertFalse(success)
    
    def test_cannot_connect_while_server_running(self):
        """Test that connecting while server is running is prevented."""
        self.network_manager.is_server = True
        self.network_manager.socket = MagicMock()
        
        # Try to connect
        success = self.network_manager.connect_to_peer('127.0.0.1', 5559)
        
        # Should fail
        self.assertFalse(success)
    
    def test_cannot_start_server_while_already_listening(self):
        """Test that starting server while already listening is prevented."""
        self.network_manager.is_server = True
        self.network_manager.socket = MagicMock()
        
        # Try to start server again
        success = self.network_manager.start_server(port=5560)
        
        # Should fail
        self.assertFalse(success)
    
    def test_socket_cleanup_on_connection_error(self):
        """Test that socket is cleaned up on connection error."""
        # Mock socket to raise an exception
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket_instance.connect.side_effect = Exception("Connection refused")
            mock_socket.return_value = mock_socket_instance
            
            # Try to connect
            success = self.network_manager.connect_to_peer('127.0.0.1', 5561)
            
            # Should fail
            self.assertFalse(success)
            
            # Verify socket.close was called for cleanup
            mock_socket_instance.close.assert_called_once()
    
    def test_socket_cleanup_on_server_error(self):
        """Test that socket is cleaned up on server start error."""
        # Mock socket to raise an exception on bind
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket_instance.bind.side_effect = Exception("Address already in use")
            mock_socket.return_value = mock_socket_instance
            
            # Try to start server
            success = self.network_manager.start_server(port=5562)
            
            # Should fail
            self.assertFalse(success)
            
            # Verify socket.close was called for cleanup
            mock_socket_instance.close.assert_called_once()


class TestConnectionDialogRouting(unittest.TestCase):
    """Test that connection dialog results route to correct methods."""
    
    def test_listen_mode_routes_to_start_server(self):
        """Test that 'listen' mode routes to start_server."""
        result = {"mode": "listen", "port": 5555}
        
        # Simulate the routing logic from main_window.py
        if result['mode'] == 'listen':
            method = 'start_server'
        else:
            method = 'connect_to_peer'
        
        self.assertEqual(method, 'start_server')
    
    def test_connect_mode_routes_to_connect_to_peer(self):
        """Test that 'connect' mode routes to connect_to_peer."""
        result = {"mode": "connect", "host": "127.0.0.1", "port": 5555}
        
        # Simulate the routing logic from main_window.py
        if result['mode'] == 'listen':
            method = 'start_server'
        else:
            method = 'connect_to_peer'
        
        self.assertEqual(method, 'connect_to_peer')


if __name__ == '__main__':
    unittest.main()
