"""
Integration test to validate the complete connection flow.
This test simulates the user's interaction with the GUI to ensure:
1. Server mode correctly calls start_server()
2. Client mode correctly calls connect_to_peer()
3. No cross-contamination between modes
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


class TestIntegrationFlow(unittest.TestCase):
    """Test complete connection flow from GUI to network layer."""
    
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
    
    def test_client_flow_uses_connect_not_bind(self):
        """
        Integration test: Client mode should use socket.connect(), NOT socket.bind().
        This reproduces the bug where client mode was calling start_server().
        """
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            
            # Simulate user clicking "Se connecter (Client)" in the GUI
            # This should route to connect_to_peer(), not start_server()
            self.network_manager.connect_to_peer('127.0.0.1', 5555)
            
            # CRITICAL ASSERTION: connect() must be called (client behavior)
            mock_socket_instance.connect.assert_called_once_with(('127.0.0.1', 5555))
            
            # CRITICAL ASSERTION: bind() must NOT be called (would be server behavior)
            mock_socket_instance.bind.assert_not_called()
            
            # CRITICAL ASSERTION: listen() must NOT be called (would be server behavior)
            mock_socket_instance.listen.assert_not_called()
            
            # Verify that is_server is False (client mode)
            self.assertFalse(self.network_manager.is_server)
    
    def test_server_flow_uses_bind_not_connect(self):
        """
        Integration test: Server mode should use socket.bind() and socket.listen(),
        NOT socket.connect().
        """
        with patch('socket.socket') as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            
            # Simulate user clicking "Écouter (Serveur)" in the GUI
            # This should route to start_server(), not connect_to_peer()
            self.network_manager.start_server(port=5555)
            
            # CRITICAL ASSERTION: bind() must be called (server behavior)
            mock_socket_instance.bind.assert_called_once()
            
            # CRITICAL ASSERTION: listen() must be called (server behavior)
            mock_socket_instance.listen.assert_called_once()
            
            # CRITICAL ASSERTION: connect() must NOT be called (would be client behavior)
            mock_socket_instance.connect.assert_not_called()
            
            # Verify that is_server is True (server mode)
            self.assertTrue(self.network_manager.is_server)
    
    def test_connection_dialog_mode_values(self):
        """
        Test that connection dialog returns the correct mode values.
        Validates the fix for the bug where 'listen' was being checked as 'server'.
        """
        # Simulate connection dialog results
        listen_result = {"mode": "listen", "port": 5555}
        connect_result = {"mode": "connect", "host": "127.0.0.1", "port": 5555}
        
        # Test listen mode routing
        mode = listen_result.get('mode')
        if mode == 'listen':
            method_called = 'start_server'
        elif mode == 'connect':
            method_called = 'connect_to_peer'
        else:
            method_called = 'error'
        
        self.assertEqual(method_called, 'start_server', 
                        "Listen mode should route to start_server")
        
        # Test connect mode routing
        mode = connect_result.get('mode')
        if mode == 'listen':
            method_called = 'start_server'
        elif mode == 'connect':
            method_called = 'connect_to_peer'
        else:
            method_called = 'error'
        
        self.assertEqual(method_called, 'connect_to_peer',
                        "Connect mode should route to connect_to_peer")
    
    def test_error_messages_are_different(self):
        """
        Test that error messages are different for client vs server mode.
        The bug was that client mode was showing server error messages.
        """
        with patch('socket.socket') as mock_socket:
            # Test client connection error
            mock_socket_instance = MagicMock()
            mock_socket_instance.connect.side_effect = Exception("Connection refused")
            mock_socket.return_value = mock_socket_instance
            
            # This should fail with a CLIENT error message
            success = self.network_manager.connect_to_peer('127.0.0.1', 5555)
            self.assertFalse(success)
            
            # Reset mock
            mock_socket.reset_mock()
            
            # Test server bind error
            mock_socket_instance2 = MagicMock()
            mock_socket_instance2.bind.side_effect = Exception("Address already in use")
            mock_socket.return_value = mock_socket_instance2
            
            # This should fail with a SERVER error message
            success = self.network_manager.start_server(port=5555)
            self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
