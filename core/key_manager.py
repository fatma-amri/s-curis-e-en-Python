"""
Key manager for generating, storing and managing cryptographic keys.
Handles Ed25519 signing keys and X25519 key exchange keys.
"""

import os
import secrets
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
import gc

from utils.logger import SecureLogger

logger = SecureLogger('key_manager')


class KeyManager:
    """Manages cryptographic keys for the messenger."""
    
    def __init__(self, keys_directory='data/keys'):
        """Initialize key manager."""
        self.keys_directory = keys_directory
        Path(keys_directory).mkdir(parents=True, exist_ok=True)
        self._set_directory_permissions()
        
        self.identity_private = None
        self.identity_public = None
        self.signing_private = None
        self.signing_public = None
        
    def _set_directory_permissions(self):
        """Set secure permissions on keys directory (Unix only)."""
        try:
            os.chmod(self.keys_directory, 0o700)
        except Exception as e:
            logger.warning(f"Could not set directory permissions: {e}")
    
    def generate_identity_keys(self):
        """Generate X25519 key pair for key exchange."""
        self.identity_private = X25519PrivateKey.generate()
        self.identity_public = self.identity_private.public_key()
        logger.info("Generated X25519 identity keys", event="key_generation")
        return self.identity_public
    
    def generate_signing_keys(self):
        """Generate Ed25519 key pair for signatures."""
        self.signing_private = Ed25519PrivateKey.generate()
        self.signing_public = self.signing_private.public_key()
        logger.info("Generated Ed25519 signing keys", event="key_generation")
        return self.signing_public
    
    def save_keys(self, password):
        """
        Save keys to disk, encrypted with password.
        
        Args:
            password: Password for key encryption
        """
        # Derive encryption key from password using Argon2id
        salt = secrets.token_bytes(32)
        encryption_key = hash_secret_raw(
            secret=password.encode(),
            salt=salt,
            time_cost=2,
            memory_cost=102400,
            parallelism=8,
            hash_len=32,
            type=Type.ID
        )
        
        try:
            # Serialize and encrypt identity private key
            identity_private_bytes = self.identity_private.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            identity_encrypted = self._encrypt_key(identity_private_bytes, encryption_key)
            
            # Serialize and encrypt signing private key
            signing_private_bytes = self.signing_private.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            signing_encrypted = self._encrypt_key(signing_private_bytes, encryption_key)
            
            # Save encrypted keys with salt
            identity_path = os.path.join(self.keys_directory, 'identity.key')
            signing_path = os.path.join(self.keys_directory, 'signing.key')
            
            with open(identity_path, 'wb') as f:
                f.write(salt + identity_encrypted)
            
            with open(signing_path, 'wb') as f:
                f.write(salt + signing_encrypted)
            
            # Set file permissions (Unix only)
            try:
                os.chmod(identity_path, 0o600)
                os.chmod(signing_path, 0o600)
            except Exception:
                pass
            
            logger.info("Keys saved to disk", event="key_save")
            
        finally:
            # Clear sensitive data from memory
            if 'encryption_key' in locals():
                encryption_key = bytearray(encryption_key)
                for i in range(len(encryption_key)):
                    encryption_key[i] = 0
            gc.collect()
    
    def load_keys(self, password):
        """
        Load keys from disk, decrypting with password.
        
        Args:
            password: Password for key decryption
            
        Returns:
            bool: True if successful
        """
        try:
            identity_path = os.path.join(self.keys_directory, 'identity.key')
            signing_path = os.path.join(self.keys_directory, 'signing.key')
            
            if not os.path.exists(identity_path) or not os.path.exists(signing_path):
                return False
            
            # Load identity key
            with open(identity_path, 'rb') as f:
                data = f.read()
            salt = data[:32]
            identity_encrypted = data[32:]
            
            # Derive encryption key
            encryption_key = hash_secret_raw(
                secret=password.encode(),
                salt=salt,
                time_cost=2,
                memory_cost=102400,
                parallelism=8,
                hash_len=32,
                type=Type.ID
            )
            
            identity_private_bytes = self._decrypt_key(identity_encrypted, encryption_key)
            self.identity_private = X25519PrivateKey.from_private_bytes(identity_private_bytes)
            self.identity_public = self.identity_private.public_key()
            
            # Load signing key
            with open(signing_path, 'rb') as f:
                data = f.read()
            salt = data[:32]
            signing_encrypted = data[32:]
            
            signing_private_bytes = self._decrypt_key(signing_encrypted, encryption_key)
            self.signing_private = Ed25519PrivateKey.from_private_bytes(signing_private_bytes)
            self.signing_public = self.signing_private.public_key()
            
            logger.info("Keys loaded from disk", event="key_load")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load keys: {e}", event="key_load_error")
            return False
        finally:
            if 'encryption_key' in locals():
                encryption_key = bytearray(encryption_key)
                for i in range(len(encryption_key)):
                    encryption_key[i] = 0
            gc.collect()
    
    def _encrypt_key(self, key_bytes, encryption_key):
        """Encrypt key bytes using ChaCha20-Poly1305."""
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        
        cipher = ChaCha20Poly1305(encryption_key)
        nonce = secrets.token_bytes(12)
        ciphertext = cipher.encrypt(nonce, key_bytes, None)
        return nonce + ciphertext
    
    def _decrypt_key(self, encrypted_data, encryption_key):
        """Decrypt key bytes using ChaCha20-Poly1305."""
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        
        cipher = ChaCha20Poly1305(encryption_key)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return cipher.decrypt(nonce, ciphertext, None)
    
    def perform_key_exchange(self, peer_public_key_bytes):
        """
        Perform ECDH key exchange with peer's public key.
        
        Args:
            peer_public_key_bytes: Peer's X25519 public key bytes
            
        Returns:
            bytes: Shared secret
        """
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
        
        peer_public_key = X25519PublicKey.from_public_bytes(peer_public_key_bytes)
        shared_secret = self.identity_private.exchange(peer_public_key)
        return shared_secret
    
    def derive_session_key(self, shared_secret, salt, info=b"session_key"):
        """
        Derive session key from shared secret using HKDF.
        
        Args:
            shared_secret: Shared secret from key exchange
            salt: Random salt
            info: Context information
            
        Returns:
            bytes: Derived session key (32 bytes)
        """
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=info,
        )
        session_key = hkdf.derive(shared_secret)
        return session_key
    
    def sign_data(self, data):
        """
        Sign data with Ed25519 private key.
        
        Args:
            data: Data to sign
            
        Returns:
            bytes: Signature
        """
        return self.signing_private.sign(data)
    
    def verify_signature(self, data, signature, public_key_bytes):
        """
        Verify Ed25519 signature.
        
        Args:
            data: Original data
            signature: Signature to verify
            public_key_bytes: Signer's public key bytes
            
        Returns:
            bool: True if signature is valid
        """
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        
        try:
            public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
            public_key.verify(signature, data)
            return True
        except Exception:
            return False
    
    def get_fingerprint(self, public_key_bytes=None):
        """
        Get SHA256 fingerprint of public key.
        
        Args:
            public_key_bytes: Public key bytes (uses own if None)
            
        Returns:
            str: Hex-encoded fingerprint
        """
        if public_key_bytes is None:
            public_key_bytes = self.signing_public.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        
        fingerprint = hashlib.sha256(public_key_bytes).hexdigest()
        # Format as XX:XX:XX:...
        return ':'.join(fingerprint[i:i+2] for i in range(0, len(fingerprint), 2))
    
    def get_identity_public_bytes(self):
        """Get identity public key as bytes."""
        return self.identity_public.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    def get_signing_public_bytes(self):
        """Get signing public key as bytes."""
        return self.signing_public.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
