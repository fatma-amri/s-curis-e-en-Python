"""
Database manager for secure storage of messages and conversations.
Uses SQLite with encryption for sensitive data.
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets
from argon2.low_level import hash_secret_raw, Type

from utils.logger import SecureLogger

logger = SecureLogger('database_manager')


class DatabaseManager:
    """Manages SQLite database for message storage."""
    
    def __init__(self, db_path='data/database/messenger.db', password=None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to database file
            password: Password for database encryption
        """
        self.db_path = db_path
        Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)
        
        # Derive encryption key from password
        if password:
            salt = self._get_or_create_salt()
            self.encryption_key = hash_secret_raw(
                secret=password.encode() if isinstance(password, str) else password,
                salt=salt,
                time_cost=2,
                memory_cost=102400,
                parallelism=8,
                hash_len=32,
                type=Type.ID
            )
            self.cipher = AESGCM(self.encryption_key)
        else:
            self.encryption_key = None
            self.cipher = None
        
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _get_or_create_salt(self):
        """Get or create salt for key derivation."""
        salt_file = os.path.join(os.path.dirname(self.db_path), '.salt')
        
        if os.path.exists(salt_file):
            with open(salt_file, 'rb') as f:
                return f.read()
        else:
            salt = secrets.token_bytes(32)
            with open(salt_file, 'wb') as f:
                f.write(salt)
            try:
                os.chmod(salt_file, 0o600)
            except Exception:
                pass
            return salt
    
    def _connect(self):
        """Connect to SQLite database."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10.0)
        self.conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent access
        self.conn.execute('PRAGMA journal_mode=WAL')
        logger.info("Connected to database", event="db_connect")
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                peer_fingerprint TEXT UNIQUE NOT NULL,
                peer_name TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_message_at TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                is_archived BOOLEAN DEFAULT 0
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                direction TEXT CHECK(direction IN ('sent', 'received')),
                message_type TEXT CHECK(message_type IN ('text', 'file')),
                content_encrypted BLOB NOT NULL,
                nonce BLOB NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_name TEXT,
                file_size INTEGER,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        ''')
        
        # Contact keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_keys (
                fingerprint TEXT PRIMARY KEY,
                public_key_ed25519 BLOB NOT NULL,
                display_name TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                is_verified BOOLEAN DEFAULT 0,
                trust_level INTEGER DEFAULT 0
            )
        ''')
        
        # Local keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_keys (
                key_type TEXT PRIMARY KEY CHECK(key_type IN ('identity', 'signing')),
                private_key_encrypted BLOB NOT NULL,
                public_key BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                key_id TEXT UNIQUE
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                peer_fingerprint TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                session_key_encrypted BLOB,
                messages_exchanged INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
        logger.info("Database tables created", event="db_init")
    
    def _encrypt_content(self, content):
        """
        Encrypt content for storage.
        
        Args:
            content: Content to encrypt (bytes or string)
            
        Returns:
            tuple: (encrypted_content, nonce)
        """
        if not self.cipher:
            # No encryption - store as is
            if isinstance(content, str):
                content = content.encode('utf-8')
            return content, b''
        
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        nonce = secrets.token_bytes(12)
        encrypted = self.cipher.encrypt(nonce, content, None)
        return encrypted, nonce
    
    def _decrypt_content(self, encrypted_content, nonce):
        """
        Decrypt content from storage.
        
        Args:
            encrypted_content: Encrypted content bytes
            nonce: Nonce used for encryption
            
        Returns:
            bytes: Decrypted content
        """
        if not self.cipher or not nonce:
            return encrypted_content
        
        return self.cipher.decrypt(nonce, encrypted_content, None)
    
    def create_conversation(self, peer_fingerprint, peer_name=None):
        """
        Create or get a conversation.
        
        Args:
            peer_fingerprint: Peer's fingerprint
            peer_name: Optional peer display name
            
        Returns:
            int: Conversation ID
        """
        cursor = self.conn.cursor()
        
        # Check if conversation exists
        cursor.execute(
            'SELECT id FROM conversations WHERE peer_fingerprint = ?',
            (peer_fingerprint,)
        )
        row = cursor.fetchone()
        
        if row:
            return row[0]
        
        # Create new conversation
        cursor.execute(
            'INSERT INTO conversations (peer_fingerprint, peer_name) VALUES (?, ?)',
            (peer_fingerprint, peer_name)
        )
        self.conn.commit()
        
        logger.info(f"Created conversation with {peer_fingerprint[:16]}...", event="conversation")
        return cursor.lastrowid
    
    def save_message(self, conversation_id, direction, content, message_type='text',
                     file_name=None, file_size=None):
        """
        Save a message to the database.
        
        Args:
            conversation_id: Conversation ID
            direction: 'sent' or 'received'
            content: Message content
            message_type: 'text' or 'file'
            file_name: Optional file name
            file_size: Optional file size
            
        Returns:
            int: Message ID
        """
        cursor = self.conn.cursor()
        
        # Encrypt content
        encrypted_content, nonce = self._encrypt_content(content)
        
        # Insert message
        cursor.execute('''
            INSERT INTO messages 
            (conversation_id, direction, message_type, content_encrypted, nonce, 
             file_name, file_size, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            conversation_id, direction, message_type, encrypted_content, nonce,
            file_name, file_size, datetime.now()
        ))
        
        # Update conversation
        cursor.execute('''
            UPDATE conversations 
            SET last_message_at = ?, message_count = message_count + 1
            WHERE id = ?
        ''', (datetime.now(), conversation_id))
        
        self.conn.commit()
        
        logger.debug(f"Saved {direction} message", event="message_save")
        return cursor.lastrowid
    
    def get_messages(self, conversation_id, limit=100, offset=0):
        """
        Get messages for a conversation.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
            offset: Offset for pagination
            
        Returns:
            list: List of message dictionaries
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT id, direction, message_type, content_encrypted, nonce, 
                   timestamp, file_name, file_size
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        ''', (conversation_id, limit, offset))
        
        messages = []
        for row in cursor.fetchall():
            # Decrypt content
            decrypted = self._decrypt_content(row[3], row[4])
            
            messages.append({
                'id': row[0],
                'direction': row[1],
                'type': row[2],
                'content': decrypted.decode('utf-8') if row[2] == 'text' else decrypted,
                'timestamp': row[5],
                'file_name': row[6],
                'file_size': row[7]
            })
        
        return messages
    
    def get_conversations(self, archived=False):
        """
        Get all conversations.
        
        Args:
            archived: Include archived conversations
            
        Returns:
            list: List of conversation dictionaries
        """
        cursor = self.conn.cursor()
        
        query = '''
            SELECT id, peer_fingerprint, peer_name, started_at, 
                   last_message_at, message_count, is_archived
            FROM conversations
            WHERE is_archived = ?
            ORDER BY last_message_at DESC
        '''
        
        cursor.execute(query, (1 if archived else 0,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'id': row[0],
                'peer_fingerprint': row[1],
                'peer_name': row[2],
                'started_at': row[3],
                'last_message_at': row[4],
                'message_count': row[5],
                'is_archived': row[6]
            })
        
        return conversations
    
    def store_contact_key(self, fingerprint, public_key, display_name=None):
        """
        Store or update contact public key.
        
        Args:
            fingerprint: Contact fingerprint
            public_key: Ed25519 public key bytes
            display_name: Optional display name
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO contact_keys 
            (fingerprint, public_key_ed25519, display_name, last_seen)
            VALUES (?, ?, ?, ?)
        ''', (fingerprint, public_key, display_name, datetime.now()))
        
        self.conn.commit()
        logger.info(f"Stored contact key for {fingerprint[:16]}...", event="key_store")
    
    def get_contact_key(self, fingerprint):
        """
        Get contact public key.
        
        Args:
            fingerprint: Contact fingerprint
            
        Returns:
            bytes: Public key or None
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT public_key_ed25519 FROM contact_keys WHERE fingerprint = ?',
            (fingerprint,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed", event="db_close")
