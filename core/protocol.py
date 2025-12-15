"""
Protocol definitions for P2P communication.
Defines message types and handshake protocol.
"""

import json
import struct
from enum import IntEnum


class MessageType(IntEnum):
    """Protocol message types."""
    HELLO = 1
    HELLO_ACK = 2
    CHALLENGE_RESPONSE = 3
    READY = 4
    TEXT_MESSAGE = 5
    FILE_TRANSFER = 6
    FILE_CHUNK = 7
    FILE_COMPLETE = 8
    HEARTBEAT = 9
    DISCONNECT = 10
    REKEY_REQUEST = 11


class Protocol:
    """Handles protocol message encoding and decoding."""
    
    @staticmethod
    def encode_message(message_type, payload):
        """
        Encode a protocol message.
        
        Format: [LENGTH:4][TYPE:1][PAYLOAD:variable]
        
        Args:
            message_type: MessageType enum value
            payload: Message payload (dict or bytes)
            
        Returns:
            bytes: Encoded message
        """
        # Convert payload to bytes
        if isinstance(payload, dict):
            payload_bytes = json.dumps(payload).encode('utf-8')
        elif isinstance(payload, str):
            payload_bytes = payload.encode('utf-8')
        else:
            payload_bytes = payload
        
        # Build message
        message_body = struct.pack('B', message_type) + payload_bytes
        length = len(message_body)
        
        # Prepend length (4 bytes, big-endian)
        message = struct.pack('>I', length) + message_body
        
        return message
    
    @staticmethod
    def decode_message(data):
        """
        Decode a protocol message.
        
        Args:
            data: Raw message bytes (with length prefix)
            
        Returns:
            tuple: (message_type, payload, remaining_data)
        """
        if len(data) < 4:
            return None, None, data
        
        # Read length
        length = struct.unpack('>I', data[:4])[0]
        
        # Check if we have the full message
        if len(data) < 4 + length:
            return None, None, data
        
        # Extract message
        message_data = data[4:4+length]
        remaining = data[4+length:]
        
        # Parse message type
        message_type = message_data[0]
        payload_bytes = message_data[1:]
        
        # Try to decode as JSON
        try:
            payload = json.loads(payload_bytes.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            payload = payload_bytes
        
        return message_type, payload, remaining
    
    @staticmethod
    def create_hello(identity_public_key, signing_public_key, signature):
        """
        Create HELLO message for handshake.
        
        Args:
            identity_public_key: X25519 public key bytes
            signing_public_key: Ed25519 public key bytes
            signature: Signature of identity key
            
        Returns:
            bytes: HELLO message
        """
        payload = {
            'identity_key': identity_public_key.hex(),
            'signing_key': signing_public_key.hex(),
            'signature': signature.hex()
        }
        return Protocol.encode_message(MessageType.HELLO, payload)
    
    @staticmethod
    def create_hello_ack(identity_public_key, signing_public_key, signature, challenge):
        """
        Create HELLO_ACK message for handshake.
        
        Args:
            identity_public_key: X25519 public key bytes
            signing_public_key: Ed25519 public key bytes
            signature: Signature of identity key
            challenge: Random challenge for authentication
            
        Returns:
            bytes: HELLO_ACK message
        """
        payload = {
            'identity_key': identity_public_key.hex(),
            'signing_key': signing_public_key.hex(),
            'signature': signature.hex(),
            'challenge': challenge.hex()
        }
        return Protocol.encode_message(MessageType.HELLO_ACK, payload)
    
    @staticmethod
    def create_challenge_response(response, signature):
        """
        Create CHALLENGE_RESPONSE message.
        
        Args:
            response: Challenge response bytes
            signature: Signature of response
            
        Returns:
            bytes: CHALLENGE_RESPONSE message
        """
        payload = {
            'response': response.hex(),
            'signature': signature.hex()
        }
        return Protocol.encode_message(MessageType.CHALLENGE_RESPONSE, payload)
    
    @staticmethod
    def create_ready():
        """
        Create READY message to complete handshake.
        
        Returns:
            bytes: READY message
        """
        payload = {'status': 'ready'}
        return Protocol.encode_message(MessageType.READY, payload)
    
    @staticmethod
    def create_text_message(encrypted_message):
        """
        Create TEXT_MESSAGE.
        
        Args:
            encrypted_message: Encrypted message bytes
            
        Returns:
            bytes: TEXT_MESSAGE protocol message
        """
        return Protocol.encode_message(MessageType.TEXT_MESSAGE, encrypted_message)
    
    @staticmethod
    def create_file_transfer(filename, file_size, file_hash):
        """
        Create FILE_TRANSFER initiation message.
        
        Args:
            filename: Name of file
            file_size: Size in bytes
            file_hash: SHA256 hash of file
            
        Returns:
            bytes: FILE_TRANSFER message
        """
        payload = {
            'filename': filename,
            'size': file_size,
            'hash': file_hash
        }
        return Protocol.encode_message(MessageType.FILE_TRANSFER, payload)
    
    @staticmethod
    def create_file_chunk(chunk_number, encrypted_chunk):
        """
        Create FILE_CHUNK message.
        
        Args:
            chunk_number: Chunk sequence number
            encrypted_chunk: Encrypted chunk bytes
            
        Returns:
            bytes: FILE_CHUNK message
        """
        # Chunk number as 4 bytes + encrypted data
        payload = struct.pack('>I', chunk_number) + encrypted_chunk
        return Protocol.encode_message(MessageType.FILE_CHUNK, payload)
    
    @staticmethod
    def create_heartbeat():
        """
        Create HEARTBEAT message.
        
        Returns:
            bytes: HEARTBEAT message
        """
        payload = {'timestamp': struct.pack('>Q', int(time.time())).hex()}
        return Protocol.encode_message(MessageType.HEARTBEAT, payload)
    
    @staticmethod
    def create_disconnect(reason="user_disconnect"):
        """
        Create DISCONNECT message.
        
        Args:
            reason: Reason for disconnection
            
        Returns:
            bytes: DISCONNECT message
        """
        payload = {'reason': reason}
        return Protocol.encode_message(MessageType.DISCONNECT, payload)


import time
