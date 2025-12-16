# Secure P2P Messenger 🔐

A peer-to-peer encrypted messaging application with end-to-end encryption built in Python.

## 🎯 Features

- **End-to-End Encryption**: ChaCha20-Poly1305 AEAD for message encryption
- **Secure Key Exchange**: X25519 ECDH with Ed25519 signatures
- **P2P Architecture**: Direct peer-to-peer connections without central server
- **Encrypted Storage**: Local message history encrypted with Argon2id
- **Modern GUI**: User-friendly Tkinter interface with chat bubbles
- **Secure Logging**: Audit logging that never exposes sensitive data
- **File Transfer**: Support for sending files (up to 10MB)
- **Automatic Rekeying**: Session keys refreshed after 1000 messages or 24 hours

## 🏗️ Architecture

```
secure_p2p_messenger/
├── main.py                    # Application entry point
├── core/                      # Core cryptographic and networking modules
│   ├── crypto_manager.py      # ChaCha20-Poly1305 encryption
│   ├── key_manager.py         # Ed25519/X25519 key management
│   ├── network_manager.py     # P2P networking with TCP
│   ├── protocol.py            # Communication protocol
│   └── message_handler.py     # Message processing
├── storage/                   # Database and file storage
│   ├── database_manager.py    # SQLite with encryption
│   ├── conversation_storage.py
│   └── file_storage.py
├── gui/                       # User interface
│   ├── main_window.py
│   ├── chat_interface.py
│   ├── connection_dialog.py
│   └── settings_window.py
├── utils/                     # Utilities
│   ├── config.py
│   ├── logger.py
│   └── validators.py
└── tests/                     # Unit tests
```

## 🔐 Security

### Cryptographic Specifications

**Key Exchange:**
- X25519 for ECDH key exchange
- Ed25519 for digital signatures
- HKDF-SHA256 for session key derivation

**Message Encryption:**
- ChaCha20-Poly1305 AEAD
- Format: `[VERSION:1][TYPE:1][NONCE:12][CIPHERTEXT:variable][TAG:16]`
- Unique nonce per message
- Associated data includes timestamp and sender ID

**Storage Encryption:**
- Argon2id for key derivation from password
- AES-256-GCM for database encryption
- Keys stored encrypted with ChaCha20-Poly1305

### Security Features

- **MITM Protection**: Mutual Ed25519 signatures
- **Replay Attack Protection**: Unique nonces and timestamp validation
- **Forward Secrecy**: Session keys derived from ephemeral ECDH
- **Secure Memory**: Explicit key clearing and garbage collection
- **Rate Limiting**: Protection against DoS attacks

## 📦 Installation

### Requirements

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/fatma-amri/s-curis-e-en-Python.git
cd s-curis-e-en-Python
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## 🚀 Usage

### First Time Setup

When you run the application for the first time:

1. You'll be prompted to create a password
2. Cryptographic keys will be generated automatically
3. Your unique fingerprint will be displayed
4. Share this fingerprint with contacts for verification

### Establishing a Connection

**Server Mode (Listen for connections):**
1. Go to `Connection > New Connection...`
2. Select "Listen (Server Mode)"
3. Choose a port (default: 5555)
4. Click "Connect"
5. Wait for a peer to connect

**Client Mode (Connect to peer):**
1. Go to `Connection > New Connection...`
2. Select "Connect (Client Mode)"
3. Enter peer's IP address and port
4. Click "Connect"
5. Wait for handshake to complete

### Verifying Connection

After connecting:
1. A dialog will show the peer's fingerprint
2. Verify this fingerprint with your contact via a trusted channel
3. If fingerprints match, the connection is secure

### Sending Messages

1. Type your message in the input field at the bottom
2. Press Enter or click "Send"
3. Messages appear as blue bubbles on the right (sent) or gray bubbles on the left (received)

### Sending Files

1. Click the "📎 File" button
2. Select a file (max 10MB)
3. File will be encrypted and sent to peer

## ⚙️ Configuration

Edit `config.json` or use `Tools > Settings...` to configure:

- Network settings (port, timeouts)
- Security parameters (rekeying thresholds)
- UI preferences (window size, message length)

## 🧪 Testing

### Diagnostic Tools

Before running the application, you can test your network configuration:

```bash
# Comprehensive network diagnostics
python network_debug.py

# Test localhost connectivity
python test_localhost_connection.py

# Test network connectivity between machines
# On machine A:
python test_network_connection.py server

# On machine B:
python test_network_connection.py client <IP_of_A>
```

### Unit Tests

Run unit tests:

```bash
# Test cryptography
python -m unittest tests.test_crypto

# Test networking
python -m unittest tests.test_network

# Test storage
python -m unittest tests.test_storage

# Run all tests
python -m unittest discover tests
```

## 📝 Database Schema

The application uses SQLite for local storage:

- `conversations`: Chat session metadata
- `messages`: Encrypted message history
- `contact_keys`: Peer public keys and verification status
- `local_keys`: Your encrypted private keys
- `sessions`: Session key history

## 🛡️ Best Practices

1. **Password**: Use a strong, unique password for key encryption
2. **Fingerprint Verification**: Always verify peer fingerprints out-of-band
3. **Network**: Use behind a firewall; configure port forwarding if needed
4. **Backups**: Backup your `data/keys/` directory securely
5. **Updates**: Keep dependencies updated for security patches

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 👥 Authors

- **Fatma Amri** - *Initial work*
- **Mariem Baraket** - *Initial work*

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔍 Troubleshooting

**Connection fails:**
- Run `python network_debug.py` for comprehensive diagnostics
- Run `python test_localhost_connection.py` to test basic connectivity
- Check firewall settings (see [TROUBLESHOOTING.md](TROUBLESHOOTING.md))
- Verify IP address and port
- Ensure peer is listening
- See detailed guide: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Password incorrect:**
- Keys cannot be recovered without password
- You'll need to delete `data/keys/` and start fresh (loses identity)

**Messages not sending:**
- Check connection status in status bar
- Try reconnecting
- Check logs in `data/logs/network_manager.log`

**Port already in use:**
- Run `python network_debug.py` to find available ports
- Use a different port in the application
- Or stop the process using the port

For comprehensive troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## 📚 References

- [ChaCha20-Poly1305 RFC](https://tools.ietf.org/html/rfc8439)
- [Ed25519 Signature Scheme](https://ed25519.cr.yp.to/)
- [X25519 Key Exchange](https://cr.yp.to/ecdh.html)
- [Argon2 Password Hashing](https://github.com/P-H-C/phc-winner-argon2)

## ⚠️ Disclaimer

This is an educational project demonstrating secure P2P communication. While it implements strong cryptographic primitives, it has not undergone a professional security audit. Use at your own risk for non-critical communications.

For production use, consider:
- Professional security audit
- Formal verification of cryptographic implementation
- Threat modeling for your specific use case
- Additional features like perfect forward secrecy rotation