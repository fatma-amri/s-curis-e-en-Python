# Secure P2P Messenger - Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Secure P2P Messenger                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              GUI Layer (Tkinter)                   │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │    │
│  │  │  Main    │ │  Chat    │ │   Connection     │  │    │
│  │  │  Window  │ │Interface │ │    Dialog        │  │    │
│  │  └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │    │
│  └───────┼────────────┼────────────────┼────────────┘    │
│          │            │                │                   │
│  ┌───────▼────────────▼────────────────▼────────────┐    │
│  │           Application Core Layer                 │    │
│  │                                                   │    │
│  │  ┌─────────────┐  ┌─────────────┐               │    │
│  │  │   Message   │  │   Network   │               │    │
│  │  │   Handler   │  │   Manager   │               │    │
│  │  └──────┬──────┘  └──────┬──────┘               │    │
│  │         │                 │                       │    │
│  │  ┌──────▼──────┐   ┌─────▼──────┐               │    │
│  │  │   Crypto    │   │  Protocol  │               │    │
│  │  │   Manager   │   │            │               │    │
│  │  └──────┬──────┘   └────────────┘               │    │
│  │         │                                         │    │
│  │  ┌──────▼──────┐                                 │    │
│  │  │    Key      │                                 │    │
│  │  │   Manager   │                                 │    │
│  │  └─────────────┘                                 │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │          Storage Layer                           │    │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────┐  │    │
│  │  │ Database   │  │Conversation│  │   File   │  │    │
│  │  │  Manager   │  │  Storage   │  │ Storage  │  │    │
│  │  └────────────┘  └────────────┘  └──────────┘  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │          Utilities Layer                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │    │
│  │  │  Config  │  │  Logger  │  │  Validators  │  │    │
│  │  └──────────┘  └──────────┘  └──────────────┘  │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### GUI Layer

#### MainWindow
- Main application window
- Menu bar and status bar
- Manages application lifecycle
- Coordinates between GUI components

#### ChatInterface
- Message display with bubbles
- Input field and send button
- File attachment interface
- Message scrolling and formatting

#### ConnectionDialog
- Server/Client mode selection
- IP and port configuration
- Fingerprint display
- Connection initiation

#### SettingsWindow
- Network settings configuration
- Security parameters
- UI preferences
- Configuration persistence

### Core Layer

#### KeyManager
- X25519 key pair generation (ECDH)
- Ed25519 key pair generation (signatures)
- Key storage with encryption
- ECDH key exchange
- Signature creation and verification
- Fingerprint generation

#### CryptoManager
- ChaCha20-Poly1305 AEAD encryption
- Message format handling
- Nonce management
- AAD construction
- Session key management

#### NetworkManager
- TCP socket management
- Server and client modes
- Handshake protocol
- Message send/receive threads
- Heartbeat mechanism
- Connection state management

#### Protocol
- Message type definitions
- Protocol message encoding/decoding
- Handshake message construction
- Length-prefixed message format

#### MessageHandler
- Message encryption/decryption coordination
- Rekeying logic
- Message callback management
- Session counter tracking

### Storage Layer

#### DatabaseManager
- SQLite database management
- Table creation and schema
- Encrypted storage with AES-GCM
- Conversation and message CRUD
- Contact key storage
- Thread-safe operations

#### ConversationStorage
- High-level conversation API
- Message saving and retrieval
- Conversation state management

#### FileStorage
- File receive handling
- File send preparation
- File integrity verification
- Secure file naming

### Utilities Layer

#### Config
- Configuration loading from JSON
- Default configuration values
- Directory initialization
- Configuration persistence

#### SecureLogger
- JSON-formatted logging
- Sensitive data redaction
- Log rotation
- Multiple log levels

#### Validators
- IP address validation
- Port number validation
- Filename sanitization
- Input length validation

## Security Architecture

### Cryptographic Flow

```
┌──────────────┐                    ┌──────────────┐
│   Client A   │                    │   Client B   │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       │  1. HELLO (identity_pub,          │
       │     signing_pub, signature)       │
       ├──────────────────────────────────>│
       │                                   │
       │  2. HELLO_ACK (identity_pub,      │
       │     signing_pub, signature,       │
       │     challenge)                    │
       │<──────────────────────────────────┤
       │                                   │
       │  3. Perform ECDH                  │  3. Perform ECDH
       │     shared_secret = ECDH()        │     shared_secret = ECDH()
       │                                   │
       │  4. Derive session key            │  4. Derive session key
       │     session_key = HKDF()          │     session_key = HKDF()
       │                                   │
       │  5. CHALLENGE_RESPONSE            │
       │     (response, signature)         │
       ├──────────────────────────────────>│
       │                                   │
       │  6. READY                         │
       │<──────────────────────────────────┤
       │                                   │
       │  === Secure Channel Established ===
       │                                   │
       │  7. TEXT_MESSAGE                  │
       │     (encrypted with session_key)  │
       ├──────────────────────────────────>│
       │                                   │
```

### Encryption Layers

1. **Transport Encryption**: ChaCha20-Poly1305 AEAD
   - Each message encrypted with unique nonce
   - Associated data includes timestamp and sender ID
   - 16-byte authentication tag

2. **Key Storage Encryption**: ChaCha20-Poly1305
   - Private keys encrypted with password-derived key
   - Argon2id for password hashing (memory-hard)

3. **Database Encryption**: AES-256-GCM
   - Message content encrypted at rest
   - Unique nonce per record

## Threading Model

```
┌─────────────────────────────────────────────────────┐
│                  Main Thread                        │
│              (Tkinter GUI Event Loop)               │
└────────────────────┬────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼─────┐  ┌─────▼─────┐  ┌───▼──────┐
│  Receive  │  │   Send    │  │Heartbeat │
│  Thread   │  │  Thread   │  │ Thread   │
└───────────┘  └───────────┘  └──────────┘
      │              │              │
      │         Queue-based         │
      │         Communication       │
      └──────────────┬──────────────┘
                     │
              ┌──────▼──────┐
              │   Sockets   │
              │   (TCP)     │
              └─────────────┘
```

## Data Flow

### Message Sending

```
User Input → GUI → MessageHandler.prepare_text_message()
                   → CryptoManager.encrypt_message()
                   → Protocol.create_text_message()
                   → NetworkManager.send_queue
                   → Send Thread
                   → Socket.send()
                   → Network
```

### Message Receiving

```
Network → Socket.recv()
        → Receive Thread
        → Protocol.decode_message()
        → NetworkManager._handle_text_message()
        → MessageHandler.handle_text_message()
        → CryptoManager.decrypt_message()
        → Callback to GUI
        → Display in ChatInterface
```

## Database Schema

```sql
conversations
├── id (PK)
├── peer_fingerprint (UNIQUE)
├── peer_name
├── started_at
├── last_message_at
└── message_count

messages
├── id (PK)
├── conversation_id (FK)
├── direction (sent/received)
├── message_type (text/file)
├── content_encrypted (BLOB)
├── nonce (BLOB)
├── timestamp
├── file_name
└── file_size

contact_keys
├── fingerprint (PK)
├── public_key_ed25519 (BLOB)
├── display_name
├── first_seen
├── last_seen
├── is_verified
└── trust_level

local_keys
├── key_type (PK)
├── private_key_encrypted (BLOB)
├── public_key (BLOB)
├── created_at
└── key_id

sessions
├── id (PK)
├── peer_fingerprint
├── started_at
├── ended_at
├── session_key_encrypted (BLOB)
└── messages_exchanged
```

## Configuration Management

Configuration is hierarchical:
1. Default values (hardcoded)
2. config.json file
3. Runtime modifications via Settings UI

Configuration sections:
- **network**: Connection parameters
- **security**: Cryptographic thresholds
- **storage**: File paths
- **ui**: Interface preferences
- **logging**: Log levels and rotation

## Error Handling

### Connection Errors
- Timeout: Retry with exponential backoff
- Refused: Report to user
- Lost: Attempt reconnection once

### Cryptographic Errors
- Invalid signature: Reject message, log security event
- Nonce reuse: Reject message, possible replay attack
- Decryption failure: Log and discard message

### Storage Errors
- Database locked: Retry with backoff
- Disk full: Alert user
- Corruption: Attempt recovery, fallback to new DB

## Performance Considerations

- **Message Encryption**: ~0.1ms per message (ChaCha20)
- **Key Exchange**: ~1ms (X25519 ECDH)
- **Database Operations**: <10ms for typical queries
- **GUI Updates**: Throttled to 60 FPS
- **Memory Usage**: ~20-50 MB typical

## Security Audit Points

1. **Key Generation**: Cryptographically secure RNG
2. **Nonce Uniqueness**: Enforced per session
3. **Memory Cleanup**: Explicit zeroing of key material
4. **Input Validation**: All user inputs sanitized
5. **Timing Attacks**: Constant-time comparison for secrets
6. **Logging**: No sensitive data in logs
7. **File Permissions**: Restricted access to key files

## Future Enhancements

- [ ] Multiple simultaneous conversations
- [ ] Group chat support
- [ ] Voice/video calls
- [ ] Mobile clients
- [ ] Perfect forward secrecy with ratcheting
- [ ] Onion routing for metadata protection
- [ ] Plugin system
- [ ] Cross-platform key backup
