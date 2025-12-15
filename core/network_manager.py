"""
Network manager for P2P connections.
Handles TCP connections, threading, and message sending/receiving.
"""

import socket
import threading
import time
import queue
import secrets
from core.protocol import Protocol, MessageType
from utils.logger import SecureLogger

logger = SecureLogger('network_manager')


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
            bool: True if successful
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((host, port))
            self.socket.listen(1)
            self.is_server = True
            
            logger.info(f"Server started on {host}:{port}", event="server_start")
            
            # Start accept thread
            accept_thread = threading.Thread(target=self._accept_connection)
            accept_thread.daemon = True
            accept_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}", event="server_error")
            return False
    
    def connect_to_peer(self, host, port, timeout=10):
        """
        Connect to a peer in client mode.
        
        Args:
            host: Peer host address
            port: Peer port number
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peer_socket.settimeout(timeout)
            self.peer_socket.connect((host, port))
            self.peer_socket.settimeout(None)
            
            self.is_connected = True
            self.connection_info = {'host': host, 'port': port}
            
            logger.info(f"Connected to {host}:{port}", event="connection")
            
            # Start threads
            self._start_communication_threads()
            
            # Initiate handshake
            self._initiate_handshake()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}", event="connection_error")
            return False
    
    def _accept_connection(self):
        """Accept incoming connection (server mode)."""
        try:
            logger.info("Waiting for incoming connection...", event="server")
            self.peer_socket, addr = self.socket.accept()
            self.is_connected = True
            self.connection_info = {'host': addr[0], 'port': addr[1]}
            
            logger.info(f"Accepted connection from {addr}", event="connection")
            
            # Start threads
            self._start_communication_threads()
            
        except Exception as e:
            if not self.stop_event.is_set():
                logger.error(f"Error accepting connection: {e}", event="server_error")
    
    def _start_communication_threads(self):
        """Start send, receive, and heartbeat threads."""
        self.stop_event.clear()
        
        self.receive_thread = threading.Thread(target=self._receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        
        self.send_thread = threading.Thread(target=self._send_loop)
        self.send_thread.daemon = True
        self.send_thread.start()
        
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
    
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
            # Create HELLO message
            identity_key = self.key_manager.get_identity_public_bytes()
            signing_key = self.key_manager.get_signing_public_bytes()
            signature = self.key_manager.sign_data(identity_key)
            
            hello_msg = Protocol.create_hello(identity_key, signing_key, signature)
            self.send_queue.put(hello_msg)
            
            logger.info("Handshake initiated", event="handshake")
            
        except Exception as e:
            logger.error(f"Handshake initiation failed: {e}", event="handshake_error")
    
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
            # Extract peer keys
            self.peer_identity_key = bytes.fromhex(payload['identity_key'])
            self.peer_signing_key = bytes.fromhex(payload['signing_key'])
            signature = bytes.fromhex(payload['signature'])
            
            # Verify signature
            if not self.key_manager.verify_signature(
                self.peer_identity_key, signature, self.peer_signing_key
            ):
                logger.error("Invalid signature in HELLO", event="handshake_error")
                return
            
            # Generate challenge
            self.challenge = secrets.token_bytes(32)
            
            # Send HELLO_ACK
            identity_key = self.key_manager.get_identity_public_bytes()
            signing_key = self.key_manager.get_signing_public_bytes()
            signature = self.key_manager.sign_data(identity_key)
            
            hello_ack = Protocol.create_hello_ack(
                identity_key, signing_key, signature, self.challenge
            )
            self.send_queue.put(hello_ack)
            
            logger.info("HELLO received, sent HELLO_ACK", event="handshake")
            
        except Exception as e:
            logger.error(f"Error handling HELLO: {e}", event="handshake_error")
    
    def _handle_hello_ack(self, payload):
        """Handle HELLO_ACK message (client receiving)."""
        try:
            # Extract peer keys
            self.peer_identity_key = bytes.fromhex(payload['identity_key'])
            self.peer_signing_key = bytes.fromhex(payload['signing_key'])
            signature = bytes.fromhex(payload['signature'])
            challenge = bytes.fromhex(payload['challenge'])
            
            # Verify signature
            if not self.key_manager.verify_signature(
                self.peer_identity_key, signature, self.peer_signing_key
            ):
                logger.error("Invalid signature in HELLO_ACK", event="handshake_error")
                return
            
            # Perform key exchange
            shared_secret = self.key_manager.perform_key_exchange(self.peer_identity_key)
            salt = secrets.token_bytes(32)
            session_key = self.key_manager.derive_session_key(shared_secret, salt)
            self.crypto_manager.set_session_key(session_key)
            
            # Sign challenge response
            response_signature = self.key_manager.sign_data(challenge)
            
            # Send CHALLENGE_RESPONSE
            challenge_response = Protocol.create_challenge_response(
                challenge, response_signature
            )
            self.send_queue.put(challenge_response)
            
            logger.info("HELLO_ACK received, sent CHALLENGE_RESPONSE", event="handshake")
            
        except Exception as e:
            logger.error(f"Error handling HELLO_ACK: {e}", event="handshake_error")
    
    def _handle_challenge_response(self, payload):
        """Handle CHALLENGE_RESPONSE message (server receiving)."""
        try:
            response = bytes.fromhex(payload['response'])
            signature = bytes.fromhex(payload['signature'])
            
            # Verify challenge response
            if response != self.challenge:
                logger.error("Invalid challenge response", event="handshake_error")
                return
            
            # Verify signature
            if not self.key_manager.verify_signature(
                response, signature, self.peer_signing_key
            ):
                logger.error("Invalid signature in CHALLENGE_RESPONSE", event="handshake_error")
                return
            
            # Perform key exchange
            shared_secret = self.key_manager.perform_key_exchange(self.peer_identity_key)
            salt = secrets.token_bytes(32)
            session_key = self.key_manager.derive_session_key(shared_secret, salt)
            self.crypto_manager.set_session_key(session_key)
            
            # Send READY
            ready_msg = Protocol.create_ready()
            self.send_queue.put(ready_msg)
            
            self.handshake_complete = True
            logger.info("Handshake complete (server)", event="handshake")
            
            # Notify UI
            if 'handshake_complete' in self.receive_callbacks:
                self.receive_callbacks['handshake_complete']()
            
        except Exception as e:
            logger.error(f"Error handling CHALLENGE_RESPONSE: {e}", event="handshake_error")
    
    def _handle_ready(self, payload):
        """Handle READY message (client receiving)."""
        self.handshake_complete = True
        logger.info("Handshake complete (client)", event="handshake")
        
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
        if self.is_connected:
            try:
                # Send disconnect message
                disconnect_msg = Protocol.create_disconnect()
                self.send_queue.put(disconnect_msg)
                time.sleep(0.5)  # Give time to send
            except Exception:
                pass
        
        self.is_connected = False
        self.handshake_complete = False
        self.stop_event.set()
        
        if self.peer_socket:
            try:
                self.peer_socket.close()
            except Exception:
                pass
        
        if self.socket and self.is_server:
            try:
                self.socket.close()
            except Exception:
                pass
        
        logger.info("Disconnected", event="disconnect")
    
    def get_peer_fingerprint(self):
        """
        Get peer's fingerprint.
        
        Returns:
            str: Peer's fingerprint
        """
        if self.peer_signing_key:
            return self.key_manager.get_fingerprint(self.peer_signing_key)
        return None
