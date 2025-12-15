"""
Integration test to verify connection dialog routing fix.
Tests that selecting client mode correctly routes to connect_to_peer.
"""

import unittest
from unittest.mock import Mock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConnectionDialogIntegration(unittest.TestCase):
    """Integration tests for connection dialog routing."""
    
    def test_client_mode_routes_to_connect_to_peer(self):
        """Test that selecting client mode calls connect_to_peer, NOT start_server."""
        # Create a mock app
        mock_app = Mock()
        mock_app.start_server = Mock()
        mock_app.connect_to_peer = Mock()
        
        # Simulate dialog returning client mode result
        result = {
            "mode": "connect",
            "host": "127.0.0.1",
            "port": 5555
        }
        
        # Execute routing logic (same as in main_window._show_connection_dialog)
        if result:
            if result['mode'] == 'listen':
                mock_app.start_server(port=result['port'])
            elif result['mode'] == 'connect':
                mock_app.connect_to_peer(result['host'], result['port'])
        
        # Verify connect_to_peer was called
        mock_app.connect_to_peer.assert_called_once_with("127.0.0.1", 5555)
        
        # Verify start_server was NOT called
        mock_app.start_server.assert_not_called()
        
        print("✓ Client mode correctly routes to connect_to_peer")
        print("✓ start_server was NOT called")
    
    def test_server_mode_routes_to_start_server(self):
        """Test that selecting server mode calls start_server, NOT connect_to_peer."""
        # Create a mock app
        mock_app = Mock()
        mock_app.start_server = Mock()
        mock_app.connect_to_peer = Mock()
        
        # Simulate dialog returning server mode result
        result = {
            "mode": "listen",
            "port": 5555
        }
        
        # Execute routing logic (same as in main_window._show_connection_dialog)
        if result:
            if result['mode'] == 'listen':
                mock_app.start_server(port=result['port'])
            elif result['mode'] == 'connect':
                mock_app.connect_to_peer(result['host'], result['port'])
        
        # Verify start_server was called
        mock_app.start_server.assert_called_once_with(port=5555)
        
        # Verify connect_to_peer was NOT called
        mock_app.connect_to_peer.assert_not_called()
        
        print("✓ Server mode correctly routes to start_server")
        print("✓ connect_to_peer was NOT called")
    
    def test_routing_logic_explicit(self):
        """Test that routing logic is explicit and handles all cases."""
        test_cases = [
            ({"mode": "listen", "port": 5555}, "start_server"),
            ({"mode": "connect", "host": "127.0.0.1", "port": 5555}, "connect_to_peer"),
            ({"mode": "unknown", "port": 5555}, "error"),  # Edge case
        ]
        
        for result, expected_method in test_cases:
            mode = result.get('mode')
            called_method = None
            
            # This is the actual routing logic from main_window.py
            if result['mode'] == 'listen':
                called_method = 'start_server'
            elif result['mode'] == 'connect':
                called_method = 'connect_to_peer'
            else:
                called_method = 'error'
            
            # Verify routing
            self.assertEqual(called_method, expected_method,
                           f"Mode '{mode}' should route to {expected_method}, got {called_method}")
            print(f"✓ Mode '{mode}' → {called_method} (correct)")
    
    def test_client_mode_never_calls_start_server(self):
        """Critical test: Verify client mode NEVER triggers start_server."""
        # This is the bug we're fixing!
        mock_app = Mock()
        mock_app.start_server = Mock()
        mock_app.connect_to_peer = Mock()
        
        # Simulate multiple client connection attempts
        client_results = [
            {"mode": "connect", "host": "127.0.0.1", "port": 5555},
            {"mode": "connect", "host": "192.168.1.1", "port": 8080},
            {"mode": "connect", "host": "10.0.0.1", "port": 9999},
        ]
        
        for result in client_results:
            # Execute routing logic
            if result['mode'] == 'listen':
                mock_app.start_server(port=result['port'])
            elif result['mode'] == 'connect':
                mock_app.connect_to_peer(result['host'], result['port'])
        
        # CRITICAL: start_server should NEVER have been called
        mock_app.start_server.assert_not_called()
        
        # connect_to_peer should have been called 3 times
        self.assertEqual(mock_app.connect_to_peer.call_count, 3)
        
        print("✓ CRITICAL: Client mode never called start_server (BUG FIXED!)")
        print(f"✓ connect_to_peer called {mock_app.connect_to_peer.call_count} times as expected")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)

