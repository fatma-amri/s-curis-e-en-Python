# Quick Start Guide - Secure P2P Messenger

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## First Launch

1. Run the application:
```bash
python main.py
```

2. On first launch:
   - You'll be prompted to create a password
   - Confirm your password
   - Your cryptographic keys will be generated
   - Your unique fingerprint will be displayed - save this!

## Connecting with a Peer

### Option 1: You Listen (Server Mode)

1. Click `Connection > New Connection...`
2. Select "Listen (Server Mode)"
3. Choose a port (default: 5555)
4. Click "Connect"
5. Share your IP address and port with your peer
6. Wait for them to connect

### Option 2: You Connect (Client Mode)

1. Get your peer's IP address and port number
2. Click `Connection > New Connection...`
3. Select "Connect (Client Mode)"
4. Enter peer's IP address and port
5. Click "Connect"
6. Wait for handshake to complete

## Verifying Connection Security

After connecting:
1. A dialog shows the peer's fingerprint
2. **IMPORTANT**: Verify this fingerprint with your contact via a trusted channel (phone, in person, etc.)
3. Both fingerprints should match
4. If they don't match, disconnect immediately - potential MITM attack!

## Sending Messages

1. Type your message in the text box at the bottom
2. Press Enter or click "Send"
3. Your messages appear as blue bubbles on the right
4. Received messages appear as gray bubbles on the left

## Sending Files

1. Click the "📎 File" button
2. Select a file (max 10MB)
3. File will be encrypted and sent
4. Received files are saved in `data/files/<peer_fingerprint>/`

## Settings

Access via `Tools > Settings...`

### Network Settings
- Default Port: Port for listening (default: 5555)
- Connection Timeout: Seconds to wait for connection (default: 10)
- Heartbeat Interval: Seconds between keep-alive messages (default: 30)

### Security Settings
- Rekey After Messages: Refresh keys after N messages (default: 1000)
- Rekey After Time: Refresh keys after N seconds (default: 86400 = 24h)

### Interface Settings
- Window dimensions
- Max message length

## Troubleshooting

### "Failed to connect to peer"
- Check IP address and port are correct
- Ensure peer is listening (server mode)
- Check firewall settings
- Try pinging the peer's IP address

### "Handshake failed"
- Both users need to have the application running
- Firewall might be blocking the connection
- Try restarting the application

### "Password incorrect"
- If you forgot your password, you cannot recover your keys
- Delete `data/keys/` directory to start fresh (loses identity)

### Connection drops frequently
- Check network stability
- Increase heartbeat interval in settings
- Consider using wired connection instead of WiFi

## Security Best Practices

1. **Strong Password**: Use a unique, strong password for key encryption
2. **Verify Fingerprints**: Always verify peer fingerprints out-of-band
3. **Keep Keys Safe**: Backup `data/keys/` directory securely
4. **Network Security**: Use behind a firewall when possible
5. **Physical Security**: Lock your computer when away
6. **Update Dependencies**: Keep Python packages updated

## Network Configuration

### Port Forwarding (for remote connections)

If connecting over the internet:
1. Configure port forwarding on your router
2. Forward chosen port to your computer's local IP
3. Share your public IP (find at whatismyip.com) and port

### Firewall Configuration

Allow incoming/outgoing connections on your chosen port:

**Windows Firewall:**
```
Control Panel > System and Security > Windows Defender Firewall > 
Advanced Settings > Inbound Rules > New Rule
```

**Linux (ufw):**
```bash
sudo ufw allow 5555/tcp
```

**macOS:**
```
System Preferences > Security & Privacy > Firewall > Firewall Options
```

## Data Storage

Application stores data in:
- `data/keys/`: Your encrypted private keys
- `data/database/`: Encrypted message history
- `data/files/`: Received files (organized by peer)
- `data/logs/`: Application logs (no sensitive data)

## Command Line Options

Currently, the application must be launched via GUI. Command-line options may be added in future versions.

## Keyboard Shortcuts

- `Enter`: Send message
- `Shift+Enter`: New line in message
- `Ctrl+W` / `Cmd+W`: Close window

## Getting Your Fingerprint

Your fingerprint uniquely identifies you:
1. Click `Connection > Show Fingerprint`
2. Share this with contacts for verification
3. Format: `XX:XX:XX:...` (64 hex characters)

## FAQ

**Q: Can I use this over the internet?**
A: Yes, but you need port forwarding configured. See Network Configuration.

**Q: Is this really secure?**
A: It uses industry-standard encryption (ChaCha20-Poly1305, Ed25519, X25519). However, it hasn't been professionally audited. Use for non-critical communications.

**Q: Can I have multiple conversations?**
A: Currently, the app supports one active conversation at a time. Multiple conversations are stored in the database for future implementation.

**Q: What if I lose my password?**
A: Your keys cannot be recovered without the password. You'll need to generate new keys (new identity).

**Q: Can someone intercept my messages?**
A: Messages are encrypted end-to-end. However, ensure you verify fingerprints to prevent MITM attacks.

**Q: Does this work on mobile?**
A: No, currently desktop only (Windows, macOS, Linux).

**Q: Can I delete messages?**
A: Use `Tools > Clear Chat` to clear the display. To delete from database, delete the database file (loses all history).

## Support

For issues or questions:
- Check logs in `data/logs/`
- Review README.md for technical details
- Submit issues on GitHub repository

## License

MIT License - See LICENSE file for details
