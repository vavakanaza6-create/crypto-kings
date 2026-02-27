# Quick Start Guide for Archipel

## Setup (5 minutes)

### 1. Install Python Dependencies
```bash
cd archipel
pip install -r requirements.txt
```

This installs the `cryptography` library needed for AES encryption.

### 2. Start Your Node

**Windows:**
```bash
python main.py
```

**Linux/macOS:**
```bash
python3 main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/macOS: `run.sh`

## Running Multiple Nodes for Testing

Open 2-3 terminal windows and run the node in each:

```bash
# Terminal 1
python main.py

# Terminal 2 (in another terminal)
python main.py

# Terminal 3 (optional)
python main.py
```

Each node will:
- Auto-assign a unique TCP port
- Auto-discover other nodes on the network
- Be ready to send/receive messages and files

## Testing Peer Discovery

In any node, type:
```
peers
```

You should see the other nodes. For example:
```
> peers
Connected Peers (2):
  a1b2c3d4... | 192.168.1.100:52842
  e5f6g7h8... | 192.168.1.101:52843
```

## Testing Messaging

Send a message from Node 1 to Node 2:

**In Node 1:**
```
msg e5f6g7h8 Hello Node 2!
```

**In Node 2, you'll see:**
```
[Chat] Message from 192.168.1.101:52843
> Hello Node 2!
```

## Testing File Transfer

Send a file from Node 1 to Node 2:

**In Node 1:**
```
send e5f6g7h8 test.txt
```

The file will be split into 64 KB chunks and sent. Progress is shown:
```
[Send] Sending test.txt to e5f6g7h8...
        Size: 1024000 bytes, 16 chunks
        Progress: 100.0%
        Sent 16 chunks successfully
```

**In Node 2:**
```
download
```

Check the `downloads/` folder for the received file.

## Understanding the Architecture

### Layers

1. **crypto/** - Encryption
   - `keys.py`: Generates RSA-2048 keys for each node
   - `cipher.py`: AES-256-GCM encryption/decryption

2. **network/** - Connectivity
   - `discovery.py`: UDP multicast for finding peers
   - `peer_table.py`: Maintains list of active peers
   - `tcp_server.py`: TCP server for receiving data

3. **messaging/** - Communication
   - `chat.py`: Encrypts and sends text messages

4. **transfer/** - Files
   - `chunker.py`: Splits files into chunks
   - `downloader.py`: Receives chunks and assembles files

5. **cli/** - User Interface
   - `commands.py`: Handles user commands

### Data Flow

```
User Command (CLI)
    ↓
CLI Commands Handler
    ↓
Network Layer (TCP)
    ↓
Crypto Layer (AES-256-GCM)
    ↓
Receiving Node
```

## Debugging

### Check Node Status
```
status
```

Shows node ID, listen port, number of peers, and uptime.

### View All Peers
```
peers
```

Lists all discovered peers with their IP and port.

### Monitor Downloads
```
download
```

Shows progress of ongoing file downloads.

### Enable Debug Output

Edit `main.py` and add `print()` statements in `_handle_packet()` to see all incoming packets.

## Common Issues

### "Peer not found" when sending message
- Type `peers` to see available peers
- Make sure the peer node is still running
- Use the first 8+ characters of the node ID (shown with `peers`)

### File transfer stuck
- Check both nodes are connected: use `peers`
- Verify network connectivity
- Check disk space on receiving side

### No peers discovered
- Ensure all nodes are on the same LAN
- Check firewall isn't blocking UDP port 5555
- Try restarting both nodes

## Next Steps for Hackathon

1. **Test Core Functionality** (30 min)
   - Start 2 nodes
   - Test messaging
   - Test file transfer

2. **Integrate Custom Features** (2-3 hours)
   - Add authentication (sign messages with RSA)
   - Add message history
   - Add group messaging
   - Create web UI

3. **Optimization** (1 hour)
   - Add bandwidth limits
   - Add file integrity checks
   - Improve error handling

4. **Demo** (30 min)
   - Show peer discovery
   - Send encrypted message
   - Transfer a file
   - Show nodes survive network changes

## Architecture Notes for Developers

### Key Components

- **Node**: Main orchestrator (main.py)
- **KeyManager**: RSA key generation and storage
- **PeerDiscovery**: UDP multicast broadcaster/listener
- **TCPServer**: Accepts connections and packets
- **ChatManager**: Handles message encryption/decryption
- **FileDownloader**: Receives and assembles files

### Extension Points

Easy to add:
- New message types (in tcp_server.py packet handler)
- New file metadata (in chunker.py create_chunk_packet)
- Authentication (in crypto/cipher.py)
- Persistence (in peer_table.py and chat.py)

### Performance Characteristics

- **Peer Discovery**: 5 second interval, 30 second timeout
- **Message Encryption**: AES-256-GCM (fast, authenticated)
- **File Transfer**: 64 KB chunks (tune in chunker.py)
- **Concurrency**: Threading per connection (scales to ~100 peers)

---

**Ready to build!** Questions? Check README.md for full documentation.
