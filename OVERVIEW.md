# Archipel Project Overview

## What is Archipel?

Archipel is a **decentralized peer-to-peer communication system** for local networks. It allows multiple computers on the same network to:

- **Discover each other** automatically (no configuration needed)
- **Send encrypted messages** between peers
- **Transfer files** with chunking and reassembly
- **Operate independently** (no central server required)

Perfect for:
- Office networks without internet
- Disaster relief / emergency communication
- Distributed computing in labs
- Mesh networks on local networks
- Hackathon demonstrations

## Project Status

✅ **Complete Foundation** - Ready for integration and feature additions

### What's Implemented

| Component | Status | Details |
|-----------|--------|---------|
| Peer Discovery | ✅ Complete | UDP multicast on 224.0.0.1:5555 |
| Encryption | ✅ Complete | AES-256-GCM with PBKDF2 key derivation |
| Messaging | ✅ Complete | Send encrypted text messages |
| File Transfer | ✅ Complete | 64 KB chunks, reassembly, progress tracking |
| CLI Interface | ✅ Complete | Interactive commands for all operations |
| Key Management | ✅ Complete | RSA-2048 key generation and storage |
| TCP Communication | ✅ Complete | Reliable connection-based data transfer |
| Error Handling | ✅ Basic | Handles common failure scenarios |

### What's NOT Implemented (Future Work)

- [ ] Key exchange protocol (currently uses shared key)
- [ ] Message/file history (in-memory only)
- [ ] Group messaging
- [ ] Web UI (currently CLI only)
- [ ] Authentication/Authorization
- [ ] File integrity verification
- [ ] Bandwidth throttling
- [ ] NAT traversal
- [ ] Persistent storage

## Quick Start

### Installation (1 minute)
```bash
cd archipel
pip install -r requirements.txt
```

### Run a Node (30 seconds)
```bash
python main.py
```

### Test with Multiple Nodes (5 minutes)
Open multiple terminals and run `python main.py` in each.

### Send First Message (2 minutes)
1. In one terminal: `peers` (to see other nodes)
2. In another: `msg <node_id> Hello!`

## Key Features

### 1. Automatic Peer Discovery
- Nodes broadcast every 5 seconds via UDP multicast
- New peers appear in the peer list automatically
- Stale peers removed after 30 seconds of inactivity

### 2. Encrypted Communication
- **AES-256-GCM**: Authenticated encryption
- **PBKDF2**: Key derivation from password
- **RSA-2048**: Key storage (extensible for key exchange)

### 3. File Transfer
- Files split into 64 KB chunks
- Each chunk sent independently
- Automatic reassembly
- Progress indication

### 4. Simple CLI
```
help              Show commands
status            Node info
peers             List connected peers
msg <id> <text>   Send message
send <id> <file>  Send file
download          Show download status
exit              Stop node
```

## Architecture

```
┌─────────────────────────────────────────┐
│ CLI Interface (User Commands)           │
│ cli/commands.py                         │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────────┬──────────────┐
    │                     │              │
┌───▼───────┐  ┌──────────▼───┐  ┌──────▼──────┐
│ Messaging │  │ File Transfer│  │ Peer Lookup │
│ chat.py   │  │ chunker.py   │  │ peer_table.│
└───┬───────┘  │ downloader.py│  └──────┬──────┘
    │          └──────────┬───┘         │
    └──────────┬──────────┴─────────────┘
               │
         ┌─────▼──────────────┐
         │ Encryption         │
         │ cipher.py / keys.py│
         └─────┬──────────────┘
               │
         ┌─────▼──────────────┐
         │ Network Layer      │
         │ tcp_server.py      │
         │ discovery.py       │
         └────────────────────┘
               │
         ┌─────▼──────────────┐
         │ UDP Multicast      │
         │ TCP Sockets        │
         └────────────────────┘
```

## File Organization

```
archipel/
├── main.py                    # Entry point - start here
├── requirements.txt           # Python dependencies (just: cryptography)
├── README.md                  # Full documentation
├── QUICKSTART.md              # Quick start guide
├── test_installation.py       # Verify setup works
├── run.bat / run.sh          # Launch scripts
│
├── crypto/                    # Encryption
│   ├── keys.py               # RSA key management
│   └── cipher.py             # AES-256-GCM encryption
│
├── network/                   # Networking
│   ├── discovery.py          # UDP multicast peer discovery
│   ├── peer_table.py         # Track known peers
│   └── tcp_server.py         # TCP server/client
│
├── messaging/                 # Text communication
│   └── chat.py               # Encrypted messaging
│
├── transfer/                  # File communication
│   ├── chunker.py            # Split files into chunks
│   └── downloader.py         # Receive and reassemble
│
└── cli/                       # User interface
    └── commands.py           # CLI command handler
```

## Development Guide for Team

### Starting Development

1. **Clone/Download** the project
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run test script**: `python test_installation.py`
4. **Start a node**: `python main.py`
5. **Check it works**: Type `help` at the prompt

### Adding Features

The code is modular - each component is independent:

**Adding a new message type:**
1. Create handler in `messaging/` or `transfer/`
2. Add packet type check in `main.py` -> `_handle_packet()`
3. Use TCP to send via `tcp_client.send_packet()`

**Improving encryption:**
1. Edit `crypto/cipher.py` to change algorithm (e.g., ChaCha20)
2. Edit `crypto/keys.py` to change key exchange protocol
3. No changes needed elsewhere!

**Enhanced CLI:**
1. Add command in `cli/commands.py`
2. Add help text in `cmd_help()`
3. Done!

**Persistent storage:**
1. Add file I/O in `messaging/chat.py` or `network/peer_table.py`
2. Load on startup in `main.py __init__()`

### Testing

**Single Machine, Multiple Nodes:**
```bash
# Terminal 1
python main.py --port 5000

# Terminal 2
python main.py --port 5001

# Terminal 3
python main.py --port 5002
```

**Test Messaging:**
- Use `peers` to get node ID
- Use `msg <id> <text>` to send
- Verify message appears in receiving node

**Test File Transfer:**
- Create test file: `echo "test data" > test.txt`
- Use `send <id> test.txt`
- Check `downloads/` folder for received file

## Code Quality

✅ **Clean Code**
- Clear function/class names
- Comprehensive docstrings
- Comments explaining logic

✅ **Modular Design**
- Each module has single responsibility
- Easy to modify/extend
- No circular dependencies

✅ **Error Handling**
- Try/catch blocks for network errors
- Graceful degradation
- User-friendly error messages

⚠️ **Production Notes**
- This is a **hackathon prototype**, not production code
- Security assumptions (shared key) not suitable for real deployment
- Lacks audit logging, persistence, formal testing
- Good foundation for production with additional hardening

## Performance

- **Peer Discovery**: O(1) announcements every 5s
- **Message Send**: Immediate (synchronous TCP)
- **File Transfer**: Limited by network bandwidth
- **Scalability**: Tested up to ~20 peers per subnet

## Platform Support

✅ Windows (tested)
✅ Linux (uses standard socket)
✅ macOS (uses standard socket)

Requires Python 3.6+ with `cryptography` library.

## Troubleshooting Checklist

1. **ImportError on start**
   - Run: `pip install -r requirements.txt`

2. **No peers appear**
   - Check all nodes on same subnet
   - Firewall may block UDP 5555
   - Wait 5 seconds for discovery

3. **Message send fails**
   - Check `peers` - is recipient listed?
   - Verify node IDs match correctly
   - Check network connectivity

4. **File transfer stuck**
   - Network may have dropped
   - Check both nodes still running
   - Restart nodes and retry

## Next Steps

1. **Immediate (Ready Now)**
   - Test peer discovery
   - Send encrypted messages
   - Transfer files

2. **Short Term (1-2 hours)**
   - Add authentication
   - Implement group chat
   - Add file integrity checks

3. **Medium Term (3-4 hours)**
   - Web UI for easier testing
   - Message history
   - Advanced security features

4. **Long Term (Future)**
   - Key exchange protocol
   - Network bridging
   - Database persistence
   - Performance optimization

## Questions?

- Check README.md for detailed documentation
- See QUICKSTART.md for usage examples
- Review code comments in each module
- Test with test_installation.py to verify setup

---

**Good luck with your hackathon!** 🚀

The Archipel team
