"""
Network manager for P2P connections.
Handles TCP connections, threading, and message sending/receiving.
"""

import socket
import threading
import time
import queue
import secrets
import sys
import os
from core.protocol import Protocol, MessageType
from utils.logger import SecureLogger

logger = SecureLogger('network_manager')

# Enable DEBUG level logging for detailed network diagnostics
# Set NETWORK_DEBUG=0 environment variable to disable in production
if os.environ.get('NETWORK_DEBUG', '1') == '1':
    logger.logger.setLevel('DEBUG')


class NetworkManager:
    """Manages P2P network connections."""
    
    def __init__(self, key_manager, crypto_manager, message_handler):
        """
        Initialize network manager.
        
        Args:
            key_manager: KeyManager instance
            crypto_manager: CryptoManager instance
            message_handler: MessageHandler instance
        """
        self.key_manager = key_manager
        self.crypto_manager = crypto_manager
        self.message_handler = message_handler
        
        self.socket = None
        self.peer_socket = None
        self.is_server = False
        self.is_connected = False
        self.connection_info = {}
        
        # Threading
        self.receive_thread = None
        self.send_thread = None
        self.heartbeat_thread = None
        self.stop_event = threading.Event()
        
        # Message queues
        self.send_queue = queue.Queue()
        self.receive_callbacks = {}
        
        # Handshake state
        self.handshake_complete = False
        self.peer_identity_key = None
        self.peer_signing_key = None
        self.challenge = None
    
    def start_server(self, host='0.0.0.0', port=5555):
        """
        Start server mode (listening for connections).
        
        Args:
            host: Host address to bind to
            port: Port number to listen on
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if already listening
        if self.is_server and self.socket:
            logger.warning("Server already running", event="server_error")
            return False
        
        # Check if already connected
        if self.is_connected:
            logger.warning("Already connected to a peer", event="server_error")
            return False
        
        try:
            logger.info(f"Attempting to create server socket on {host}:{port}", event="server_start")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug(f"Socket created: {self.socket}", event="server_start")
            
            # Enable address reuse - CRUCIAL for avoiding "Address already in use"
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logger.debug("SO_REUSEADDR option enabled", event="server_start")
            
            # On macOS, also enable SO_REUSEPORT
            if sys.platform == 'darwin':
                try:
                    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                    logger.debug("SO_REUSEPORT option enabled (macOS)", event="server_start")
                except (AttributeError, OSError) as e:
                    # SO_REUSEPORT may not be available on all systems
                    logger.debug(f"SO_REUSEPORT not available: {e}", event="server_start")
            
            self.socket.bind((host, port))
            logger.info(f"Socket bound to {host}:{port}", event="server_start")
            
            self.socket.listen(1)
            logger.info(f"Socket listening with backlog=1", event="server_start")
            
            self.is_server = True
            
            logger.info(f"Server started successfully on {host}:{port}", event="server_start")
            
            # Start accept thread
            accept_thread = threading.Thread(target=self._accept_connection)
            accept_thread.daemon = True
            accept_thread.start()
            logger.debug("Accept thread started", event="server_start")
            
            return True
            
        except OSError as e:
            if e.errno == 48 or e.errno == 98:  # Address already in use
                logger.error(f"Port {port} already in use. Try a different port.", event="server_error")
                logger.info(f"Suggestion: Use port {port + 1} or check for processes using port {port}", event="server_error")
            elif e.errno == 13:  # Permission denied
                logger.error(f"Permission denied to bind to port {port}. Try a port > 1024 or run with elevated privileges.", event="server_error")
            else:
                logger.error(f"OS Error creating server socket: {e}", event="server_error")
                logger.debug(f"Errno: {e.errno}, Strerror: {e.strerror}", event="server_error")
            
            # Clean up socket on error
            if self.socket:
                try:
                    self.socket.close()
                except Exception as close_error:
                    logger.debug(f"Error closing socket during cleanup: {close_error}")
                self.socket = None
            self.is_server = False
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error starting server: {type(e).__name__}: {e}", event="server_error")
            # Clean up socket on error
            if self.socket:
                try:
                    self.socket.close()
                except Exception:
                    pass
                self.socket = None
            self.is_server = False
            return False
    
    def connect_to_peer(self, host, port, timeout=10):
        """
        Connect to a peer in client mode.
        
        Args:
            host: Peer host address
            port: Peer port number
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if already connected
        if self.is_connected:
            logger.warning("Already connected to a peer", event="connection_error")
            return False
        
        # Check if already listening
        if self.is_server and self.socket:
            logger.warning("Cannot connect while server is running", event="connection_error")
            return False
        
        try:
            logger.info(f"Attempting to connect to {host}:{port}", event="connection")
            
            # Validate IP address
            try:
                socket.inet_aton(host)
                logger.debug(f"IP address is valid: {host}", event="connection")
            except socket.error:
                logger.error(f"Invalid IP address format: {host}", event="connection_error")
                return False
            
            self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug(f"Client socket created: {self.peer_socket}", event="connection")
            
            self.peer_socket.settimeout(timeout)
            logger.debug(f"Socket timeout set to {timeout} seconds", event="connection")
            
            logger.info(f"Connecting to {host}:{port}...", event="connection")
            self.peer_socket.connect((host, port))
            
            # Remove timeout for normal operations
            self.peer_socket.settimeout(None)
            
            self.is_connected = True
            self.connection_info = {'host': host, 'port': port}
            
            logger.info(f"✓ CONNECTED to {host}:{port}", event="connection")
            
            # Start threads
            self._start_communication_threads()
            
            # Initiate handshake
            self._initiate_handshake()
            
            return True
            
        except socket.timeout:
            logger.error(f"TIMEOUT: Could not connect to {host}:{port} after {timeout} seconds", event="connection_error")
            logger.info("Verify that the server is running and accepting connections", event="connection_error")
            # Clean up socket on error
            if self.peer_socket:
                try:
                    self.peer_socket.close()
                except Exception:
                    pass
                self.peer_socket = None
            return False
            
        except ConnectionRefusedError:
            logger.error(f"CONNECTION REFUSED: Server at {host}:{port} refused the connection", event="connection_error")
            logger.info("Check that:", event="connection_error")
            logger.info("  1. Server is started in server mode", event="connection_error")
            logger.info("  2. Port number is correct", event="connection_error")
            logger.info("  3. Firewall allows connections", event="connection_error")
            # Clean up socket on error
            if self.peer_socket:
                try:
                    self.peer_socket.close()
                except Exception:
                    pass
                self.peer_socket = None
            return False
            
        except socket.gaierror as e:
            logger.error(f"DNS/ADDRESS ERROR: {e}", event="connection_error")
            logger.info("Verify that the IP address is correct", event="connection_error")
            # Clean up socket on error
            if self.peer_socket:
                try:
                    self.peer_socket.close()
                except Exception:
                    pass
                self.peer_socket = None
            return False
            
        except OSError as e:
            logger.error(f"OS ERROR: {e}", event="connection_error")
            logger.debug(f"Errno: {e.errno}", event="connection_error")
            # Clean up socket on error
            if self.peer_socket:
                try:
                    self.peer_socket.close()
                except Exception:
                    pass
                self.peer_socket = None
            return False
            
        except Exception as e:
            logger.error(f"UNEXPECTED ERROR: {type(e).__name__}: {e}", event="connection_error")
            # Clean up socket on error
            if self.peer_socket:
                try:
                    self.peer_socket.close()
                except OSError as close_error:
                    logger.debug(f"Error closing socket during cleanup: {close_error}")
                except Exception:
                    pass
                self.peer_socket = None
            return False
    
    def _accept_connection(self):
        """Accept incoming connection (server mode)."""
        try:
            logger.info("Waiting for incoming connection...", event="server")
            logger.debug("Accept thread running, socket ready to accept", event="server")
            
            # Set a timeout to allow periodic checking of stop_event
            self.socket.settimeout(1.0)
            
            while not self.stop_event.is_set() and self.is_server:
                try:
                    self.peer_socket, addr = self.socket.accept()
                    self.is_connected = True
                    self.connection_info = {'host': addr[0], 'port': addr[1]}
                    
                    logger.info(f"✓ CONNECTION ACCEPTED from {addr[0]}:{addr[1]}", event="connection")
                    
                    # Remove timeout for normal communication
                    self.peer_socket.settimeout(None)
                    
                    # Start threads
                    self._start_communication_threads()
                    
                    break  # Connection accepted, exit loop
                    
                except socket.timeout:
                    # Timeout is expected - continue loop to check stop_event
                    continue
                    
        except Exception as e:
            if not self.stop_event.is_set():
                logger.error(f"Error accepting connection: {e}", event="server_error")
    
    def _start_communication_threads(self):
        """Start send, receive, and heartbeat threads."""
        self.stop_event.clear()
        
        logger.debug("Starting communication threads", event="threads")
        
        self.receive_thread = threading.Thread(target=self._receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        logger.debug("Receive thread started", event="threads")
        
        self.send_thread = threading.Thread(target=self._send_loop)
        self.send_thread.daemon = True
        self.send_thread.start()
        logger.debug("Send thread started", event="threads")
        
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        logger.debug("Heartbeat thread started", event="threads")
    
    def _receive_loop(self):
        """Receive messages from peer."""
        buffer = b''
        
        while not self.stop_event.is_set() and self.is_connected:
            try:
                data = self.peer_socket.recv(4096)
                if not data:
                    logger.info("Peer disconnected", event="disconnect")
                    self.disconnect()
                    break
                
                buffer += data
                
                # Process all complete messages in buffer
                while len(buffer) >= 4:
                    msg_type, payload, buffer = Protocol.decode_message(buffer)
                    
                    if msg_type is None:
                        break
                    
                    self._handle_received_message(msg_type, payload)
                    
            except socket.timeout:
                continue
            except Exception as e:
                if not self.stop_event.is_set():
                    logger.error(f"Receive error: {e}", event="receive_error")
                break
    
    def _send_loop(self):
        """Send messages from queue."""
        while not self.stop_event.is_set() and self.is_connected:
            try:
                message = self.send_queue.get(timeout=1)
                self.peer_socket.sendall(message)
            except queue.Empty:
                continue
            except Exception as e:
                if not self.stop_event.is_set():
                    logger.error(f"Send error: {e}", event="send_error")
                break
    
    def _heartbeat_loop(self):
        """Send periodic heartbeat messages."""
        while not self.stop_event.is_set() and self.is_connected:
            try:
                time.sleep(30)
                if self.handshake_complete:
                    heartbeat = Protocol.create_heartbeat()
                    self.send_queue.put(heartbeat)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}", event="heartbeat_error")
    
    def _initiate_handshake(self):
        """Initiate handshake as client."""
        try:
            logger.info("Initiating handshake protocol", event="handshake")
            
            # Create HELLO message
            identity_key = self.key_manager.get_identity_public_bytes()
            signing_key = self.key_manager.get_signing_public_bytes()
            signature = self.key_manager.sign_data(identity_key)
            
            logger.debug("Identity and signing keys prepared", event="handshake")
            
            hello_msg = Protocol.create_hello(identity_key, signing_key, signature)
            logger.debug(f"HELLO message created, size: {len(hello_msg)} bytes", event="handshake")
            
            self.send_queue.put(hello_msg)
            
            logger.info("HELLO message queued for sending", event="handshake")
            
        except Exception as e:
            logger.error(f"Handshake initiation failed: {type(e).__name__}: {e}", event="handshake_error")
    
    def _handle_received_message(self, msg_type, payload):
        """
        Handle received protocol message.
        
        Args:
            msg_type: MessageType
            payload: Message payload
        """
        try:
            if msg_type == MessageType.HELLO:
                self._handle_hello(payload)
            elif msg_type == MessageType.HELLO_ACK:
                self._handle_hello_ack(payload)
            elif msg_type == MessageType.CHALLENGE_RESPONSE:
                self._handle_challenge_response(payload)
            elif msg_type == MessageType.READY:
                self._handle_ready(payload)
            elif msg_type == MessageType.TEXT_MESSAGE:
                self._handle_text_message(payload)
            elif msg_type == MessageType.HEARTBEAT:
                pass  # Heartbeat received, connection alive
            elif msg_type == MessageType.DISCONNECT:
                self._handle_disconnect(payload)
            else:
                logger.warning(f"Unknown message type: {msg_type}", event="unknown_message")
                
        except Exception as e:
            logger.error(f"Error handling message: {e}", event="message_error")
    
    def _handle_hello(self, payload):
        """Handle HELLO message (server receiving)."""
        try:
            logger.debug("Processing HELLO message", event="handshake")
            
            # Extract peer keys
            self.peer_identity_key = bytes.fromhex(payload['identity_key'])
            self.peer_signing_key = bytes.fromhex(payload['signing_key'])
            signature = bytes.fromhex(payload['signature'])
            
            logger.debug(f"Peer identity key extracted: {len(self.peer_identity_key)} bytes", event="handshake")
            logger.debug(f"Peer signing key extracted: {len(self.peer_signing_key)} bytes", event="handshake")
            
            # Verify signature
            if not self.key_manager.verify_signature(
                self.peer_identity_key, signature, self.peer_signing_key
            ):
                logger.error("Invalid signature in HELLO message", event="handshake_error")
                logger.warning("SECURITY: Signature verification failed - possible MITM attack", event="security")
                return
            
            logger.info("✓ Signature verified successfully", event="handshake")
            
            # Generate challenge
            self.challenge = secrets.token_bytes(32)
            logger.debug(f"Challenge generated: {len(self.challenge)} bytes", event="handshake")
            
            # Send HELLO_ACK
            identity_key = self.key_manager.get_identity_public_bytes()
            signing_key = self.key_manager.get_signing_public_bytes()
            signature = self.key_manager.sign_data(identity_key)
            
            hello_ack = Protocol.create_hello_ack(
                identity_key, signing_key, signature, self.challenge
            )
            self.send_queue.put(hello_ack)
            
            logger.info("HELLO received and verified, HELLO_ACK sent", event="handshake")
            
        except KeyError as e:
            logger.error(f"Missing field in HELLO payload: {e}", event="handshake_error")
        except ValueError as e:
            logger.error(f"Invalid data format in HELLO: {e}", event="handshake_error")
        except Exception as e:
            logger.error(f"Error handling HELLO: {type(e).__name__}: {e}", event="handshake_error")
    
    def _handle_hello_ack(self, payload):
        """Handle HELLO_ACK message (client receiving)."""
        try:
            logger.debug("Processing HELLO_ACK message", event="handshake")
            
            # Extract peer keys
            self.peer_identity_key = bytes.fromhex(payload['identity_key'])
            self.peer_signing_key = bytes.fromhex(payload['signing_key'])
            signature = bytes.fromhex(payload['signature'])
            challenge = bytes.fromhex(payload['challenge'])
            
            logger.debug(f"Peer keys and challenge extracted", event="handshake")
            
            # Verify signature
            if not self.key_manager.verify_signature(
                self.peer_identity_key, signature, self.peer_signing_key
            ):
                logger.error("Invalid signature in HELLO_ACK", event="handshake_error")
                logger.warning("SECURITY: Signature verification failed - possible MITM attack", event="security")
                return
            
            logger.info("✓ HELLO_ACK signature verified", event="handshake")
            
            # Perform key exchange
            logger.debug("Performing ECDH key exchange", event="handshake")
            shared_secret = self.key_manager.perform_key_exchange(self.peer_identity_key)
            salt = secrets.token_bytes(32)
            session_key = self.key_manager.derive_session_key(shared_secret, salt)
            self.crypto_manager.set_session_key(session_key)
            logger.info("✓ Session key derived and set", event="handshake")
            
            # Sign challenge response
            response_signature = self.key_manager.sign_data(challenge)
            logger.debug("Challenge signed", event="handshake")
            
            # Send CHALLENGE_RESPONSE
            challenge_response = Protocol.create_challenge_response(
                challenge, response_signature
            )
            self.send_queue.put(challenge_response)
            
            logger.info("HELLO_ACK verified, CHALLENGE_RESPONSE sent", event="handshake")
            
        except KeyError as e:
            logger.error(f"Missing field in HELLO_ACK payload: {e}", event="handshake_error")
        except ValueError as e:
            logger.error(f"Invalid data format in HELLO_ACK: {e}", event="handshake_error")
        except Exception as e:
            logger.error(f"Error handling HELLO_ACK: {type(e).__name__}: {e}", event="handshake_error")
    
    def _handle_challenge_response(self, payload):
        """Handle CHALLENGE_RESPONSE message (server receiving)."""
        try:
            logger.debug("Processing CHALLENGE_RESPONSE", event="handshake")
            
            response = bytes.fromhex(payload['response'])
            signature = bytes.fromhex(payload['signature'])
            
            # Verify challenge response
            if response != self.challenge:
                logger.error("Invalid challenge response - challenge mismatch", event="handshake_error")
                logger.warning("SECURITY: Challenge verification failed", event="security")
                return
            
            logger.debug("✓ Challenge response matches", event="handshake")
            
            # Verify signature
            if not self.key_manager.verify_signature(
                response, signature, self.peer_signing_key
            ):
                logger.error("Invalid signature in CHALLENGE_RESPONSE", event="handshake_error")
                logger.warning("SECURITY: Signature verification failed", event="security")
                return
            
            logger.info("✓ Challenge signature verified", event="handshake")
            
            # Perform key exchange
            logger.debug("Performing ECDH key exchange", event="handshake")
            shared_secret = self.key_manager.perform_key_exchange(self.peer_identity_key)
            salt = secrets.token_bytes(32)
            session_key = self.key_manager.derive_session_key(shared_secret, salt)
            self.crypto_manager.set_session_key(session_key)
            logger.info("✓ Session key derived and set", event="handshake")
            
            # Send READY
            ready_msg = Protocol.create_ready()
            self.send_queue.put(ready_msg)
            
            self.handshake_complete = True
            logger.info("✓✓✓ HANDSHAKE COMPLETE (server) ✓✓✓", event="handshake")
            
            # Notify UI
            if 'handshake_complete' in self.receive_callbacks:
                self.receive_callbacks['handshake_complete']()
            
        except KeyError as e:
            logger.error(f"Missing field in CHALLENGE_RESPONSE: {e}", event="handshake_error")
        except ValueError as e:
            logger.error(f"Invalid data format in CHALLENGE_RESPONSE: {e}", event="handshake_error")
        except Exception as e:
            logger.error(f"Error handling CHALLENGE_RESPONSE: {type(e).__name__}: {e}", event="handshake_error")
    
    def _handle_ready(self, payload):
        """Handle READY message (client receiving)."""
        self.handshake_complete = True
        logger.info("✓✓✓ HANDSHAKE COMPLETE (client) ✓✓✓", event="handshake")
        
        # Notify UI
        if 'handshake_complete' in self.receive_callbacks:
            self.receive_callbacks['handshake_complete']()
    
    def _handle_text_message(self, payload):
        """Handle TEXT_MESSAGE."""
        try:
            if not self.handshake_complete:
                logger.warning("Received message before handshake complete", event="security")
                return
            
            # Decrypt message
            message_text = self.message_handler.handle_text_message(payload)
            
            # Notify UI
            if 'text_message' in self.receive_callbacks:
                self.receive_callbacks['text_message'](message_text)
                
        except Exception as e:
            logger.error(f"Error handling text message: {e}", event="message_error")
    
    def _handle_disconnect(self, payload):
        """Handle DISCONNECT message."""
        reason = payload.get('reason', 'unknown')
        logger.info(f"Peer disconnected: {reason}", event="disconnect")
        self.disconnect()
    
    def send_text_message(self, text):
        """
        Send a text message to peer.
        
        Args:
            text: Message text
        """
        if not self.handshake_complete:
            logger.warning("Cannot send message before handshake", event="send_error")
            return False
        
        try:
            # Encrypt message
            encrypted = self.message_handler.prepare_text_message(text)
            
            # Create protocol message
            protocol_msg = Protocol.create_text_message(encrypted)
            
            # Queue for sending
            self.send_queue.put(protocol_msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}", event="send_error")
            return False
    
    def register_callback(self, event_type, callback):
        """
        Register a callback for network events.
        
        Args:
            event_type: Type of event ('text_message', 'handshake_complete', etc.)
            callback: Function to call
        """
        self.receive_callbacks[event_type] = callback
    
    def disconnect(self):
        """Disconnect from peer."""
        logger.info("Initiating disconnect sequence", event="disconnect")
        
        if self.is_connected:
            try:
                # Send disconnect message
                disconnect_msg = Protocol.create_disconnect()
                self.send_queue.put(disconnect_msg)
                time.sleep(0.5)  # Give time to send
                logger.debug("Disconnect message sent", event="disconnect")
            except Exception as e:
                logger.debug(f"Error sending disconnect message: {e}", event="disconnect")
        
        self.is_connected = False
        self.handshake_complete = False
        self.stop_event.set()
        logger.debug("Stop event set, threads will terminate", event="disconnect")
        
        # Close peer socket
        if self.peer_socket:
            try:
                self.peer_socket.shutdown(socket.SHUT_RDWR)
                logger.debug("Peer socket shutdown", event="disconnect")
            except Exception as e:
                logger.debug(f"Error during socket shutdown: {e}", event="disconnect")
            finally:
                try:
                    self.peer_socket.close()
                    logger.debug("Peer socket closed", event="disconnect")
                except Exception as e:
                    logger.debug(f"Error closing peer socket: {e}", event="disconnect")
                self.peer_socket = None
        
        # Close server socket if in server mode
        if self.socket and self.is_server:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                logger.debug("Server socket shutdown", event="disconnect")
            except Exception as e:
                logger.debug(f"Error during server socket shutdown: {e}", event="disconnect")
            finally:
                try:
                    self.socket.close()
                    logger.debug("Server socket closed", event="disconnect")
                except Exception as e:
                    logger.debug(f"Error closing server socket: {e}", event="disconnect")
                self.socket = None
        
        self.is_server = False
        logger.info("✓ Disconnected successfully", event="disconnect")
    
    def get_peer_fingerprint(self):
        """
        Get peer's fingerprint.
        
        Returns:
            str: Peer's fingerprint
        """
        if self.peer_signing_key:
            return self.key_manager.get_fingerprint(self.peer_signing_key)
        return None