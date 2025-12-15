"""
Secure P2P Messenger - Main Application Entry Point

A peer-to-peer encrypted messaging application with end-to-end encryption.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog

from core.key_manager import KeyManager
from core.crypto_manager import CryptoManager
from core.network_manager import NetworkManager
from core.message_handler import MessageHandler
from storage.database_manager import DatabaseManager
from storage.conversation_storage import ConversationStorage
from storage.file_storage import FileStorage
from gui.main_window import MainWindow
from utils.config import config
from utils.logger import SecureLogger

logger = SecureLogger('main')


class SecureMessengerApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize application."""
        logger.info("Starting Secure P2P Messenger", event="app_start")
        
        # Initialize configuration
        self.config = config
        
        # Initialize key manager
        self.key_manager = KeyManager(
            self.config.get('storage', 'keys_directory')
        )
        
        # Check if keys exist or create new ones
        self._initialize_keys()
        
        # Initialize crypto manager
        self.crypto_manager = CryptoManager()
        
        # Initialize message handler
        self.message_handler = MessageHandler(
            self.crypto_manager,
            self.key_manager
        )
        
        # Initialize network manager
        self.network_manager = None
        
        # Initialize storage
        self._initialize_storage()
        
        # Initialize file storage
        self.file_storage = FileStorage(
            self.config.get('storage', 'files_directory')
        )
        
        # Initialize GUI
        self.main_window = MainWindow(self)
        
        logger.info("Application initialized", event="app_init")
    
    def _initialize_keys(self):
        """Initialize or load cryptographic keys."""
        keys_dir = self.config.get('storage', 'keys_directory')
        identity_path = os.path.join(keys_dir, 'identity.key')
        signing_path = os.path.join(keys_dir, 'signing.key')
        
        if os.path.exists(identity_path) and os.path.exists(signing_path):
            # Keys exist, prompt for password
            root = tk.Tk()
            root.withdraw()
            
            password = simpledialog.askstring(
                "Unlock Keys",
                "Enter your password to unlock keys:",
                show='*'
            )
            
            if not password:
                messagebox.showerror("Error", "Password required to start application.")
                sys.exit(1)
            
            success = self.key_manager.load_keys(password)
            
            if not success:
                messagebox.showerror("Error", "Failed to load keys. Incorrect password?")
                sys.exit(1)
            
            logger.info("Keys loaded successfully", event="key_load")
        else:
            # Generate new keys
            root = tk.Tk()
            root.withdraw()
            
            messagebox.showinfo(
                "First Time Setup",
                "Welcome! This is your first time running the application.\n\n"
                "We'll generate your cryptographic keys and secure them with a password."
            )
            
            password = simpledialog.askstring(
                "Create Password",
                "Create a password to protect your keys:",
                show='*'
            )
            
            if not password:
                messagebox.showerror("Error", "Password required to create keys.")
                sys.exit(1)
            
            password_confirm = simpledialog.askstring(
                "Confirm Password",
                "Confirm your password:",
                show='*'
            )
            
            if password != password_confirm:
                messagebox.showerror("Error", "Passwords do not match.")
                sys.exit(1)
            
            # Generate keys
            self.key_manager.generate_identity_keys()
            self.key_manager.generate_signing_keys()
            self.key_manager.save_keys(password)
            
            fingerprint = self.key_manager.get_fingerprint()
            
            messagebox.showinfo(
                "Keys Generated",
                f"Your keys have been generated and saved.\n\n"
                f"Your fingerprint:\n{fingerprint}\n\n"
                f"Share this with your contacts for verification."
            )
            
            logger.info("New keys generated", event="key_generation")
    
    def _initialize_storage(self):
        """Initialize database storage."""
        # For simplicity, use a default password for DB encryption
        # In production, this should be derived from user password
        db_password = "default_db_password"
        
        self.db_manager = DatabaseManager(
            self.config.get('storage', 'database_path'),
            db_password
        )
        
        self.conversation_storage = ConversationStorage(self.db_manager)
    
    def start_server(self, port=None):
        """
        Start server mode.
        
        Args:
            port: Port to listen on (uses config default if None)
        """
        if not port:
            port = self.config.get('network', 'default_port')
        
        # Check if already connected
        if self.network_manager and self.network_manager.is_connected:
            messagebox.showerror("Error", "Already connected to a peer. Disconnect first.")
            return
        
        # Check if already listening
        if self.network_manager and self.network_manager.is_server:
            messagebox.showerror("Error", "Server is already listening.")
            return
        
        # Create network manager if not exists
        if not self.network_manager:
            self.network_manager = NetworkManager(
                self.key_manager,
                self.crypto_manager,
                self.message_handler
            )
            self._setup_network_callbacks()
        
        success = self.network_manager.start_server(port=port)
        
        if success:
            self.main_window.update_status(
                "Listening",
                f"Port: {port}"
            )
            logger.info(f"Server started on port {port}", event="server_start")
        else:
            messagebox.showerror(
                "Error", 
                f"Failed to start server on port {port}.\n"
                f"The port may already be in use or you may not have permission.\n"
                f"Try a different port or check if another instance is running."
            )
    
    def connect_to_peer(self, host, port):
        """
        Connect to a peer.
        
        Args:
            host: Peer host address
            port: Peer port
        """
        # Check if already connected
        if self.network_manager and self.network_manager.is_connected:
            messagebox.showerror("Error", "Already connected to a peer. Disconnect first.")
            return
        
        # Check if already listening
        if self.network_manager and self.network_manager.is_server:
            messagebox.showerror("Error", "Server is listening. Disconnect first.")
            return
        
        # Create network manager if not exists
        if not self.network_manager:
            self.network_manager = NetworkManager(
                self.key_manager,
                self.crypto_manager,
                self.message_handler
            )
            self._setup_network_callbacks()
        
        success = self.network_manager.connect_to_peer(host, port)
        
        if success:
            self.main_window.update_status(
                "Connecting...",
                f"{host}:{port}"
            )
            logger.info(f"Connected to {host}:{port}", event="connection")
        else:
            messagebox.showerror(
                "Error", 
                f"Failed to connect to peer at {host}:{port}.\n"
                f"Make sure the peer is listening and reachable.\n"
                f"Check your network connection and firewall settings."
            )
    
    def _setup_network_callbacks(self):
        """Setup callbacks for network events."""
        self.network_manager.register_callback(
            'handshake_complete',
            self._on_handshake_complete
        )
        
        self.network_manager.register_callback(
            'text_message',
            self._on_text_message
        )
    
    def _on_handshake_complete(self):
        """Handle handshake completion."""
        peer_fingerprint = self.network_manager.get_peer_fingerprint()
        
        # Start conversation in storage
        if peer_fingerprint:
            self.conversation_storage.start_conversation(peer_fingerprint)
            
            # Store peer key
            peer_key = self.network_manager.peer_signing_key
            self.db_manager.store_contact_key(peer_fingerprint, peer_key)
        
        # Update UI
        conn_info = self.network_manager.connection_info
        self.main_window.update_status(
            "Connected",
            f"{conn_info.get('host', '')}:{conn_info.get('port', '')}"
        )
        self.main_window.enable_chat(True)
        
        logger.info("Handshake complete", event="handshake")
        
        # Show peer fingerprint
        if peer_fingerprint:
            messagebox.showinfo(
                "Connected",
                f"Secure connection established!\n\n"
                f"Peer fingerprint:\n{peer_fingerprint}\n\n"
                f"Verify this fingerprint with your contact."
            )
    
    def _on_text_message(self, message_text):
        """
        Handle received text message.
        
        Args:
            message_text: Received message text
        """
        logger.info("Message received", event="message_received")
        self.main_window.display_received_message(message_text)
    
    def shutdown(self):
        """Shutdown application."""
        logger.info("Shutting down application", event="app_shutdown")
        
        # Disconnect network
        if self.network_manager:
            self.network_manager.disconnect()
        
        # Close database
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        
        # Clear crypto manager
        self.crypto_manager.clear_session()
    
    def run(self):
        """Run the application."""
        self.main_window.run()


def main():
    """Main entry point."""
    try:
        app = SecureMessengerApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted", event="app_interrupt")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}", event="app_error")
        messagebox.showerror("Error", f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
