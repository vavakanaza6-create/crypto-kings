# Archipel - Hackathon Development Roadmap

## Project Phases (24-hour Hackathon)

```
Hour 0-2:    Setup & Validation
Hour 2-4:    Core Testing
Hour 4-8:    Feature Integration
Hour 8-12:   Enhancement & Polish
Hour 12-24:  Stretch Goals & Demo
```

---

## Phase 1: Setup & Validation (0-2 hours)

**Goals:**
- [ ] Environment setup complete
- [ ] All dependencies installed
- [ ] Installation test passes
- [ ] All team members can run a node

**Tasks:**
1. Clone/download Archipel project
2. Run: `pip install -r requirements.txt`
3. Run: `python test_installation.py`
4. Each developer: `python main.py` in their terminal
5. Verify nodes appear in each other's peer lists

**Success Criteria:**
- ✅ No ImportError
- ✅ Node starts without crashing
- ✅ Multiple nodes auto-discover each other

**Owner:** Infrastructure Lead
**Time:** 30 min setup + 30 min validation

---

## Phase 2: Core Testing (2-4 hours)

**Goals:**
- [ ] Peer discovery verified
- [ ] Messaging works end-to-end
- [ ] File transfer works
- [ ] All bugs documented for Phase 3

**Tasks:**

### 2.1 Test Peer Discovery
```bash
# Terminal 1
python main.py

# Terminal 2
python main.py

# In either terminal:
> peers
# Should see the other node
```

**Checklist:**
- [ ] Peers appear within 5 seconds
- [ ] Peers persist in list
- [ ] Stale peers removed after 30 seconds

**Owner:** Network Team
**Time:** 30 min

### 2.2 Test Encrypted Messaging
```bash
# Terminal 1: Node A
Node_A> peers
# Copy Node B's ID

# Terminal 2: Node B
Node_B> peers

# In Terminal 1:
Node_A> msg <Node_B_ID> Hello World

# In Terminal 2, should see:
[Chat] Message from 127.0.0.1:xxxx
> Hello World
```

**Checklist:**
- [ ] Messages are encrypted (look at TCP packets - should be hex)
- [ ] Message successfully received
- [ ] Can send multiple messages
- [ ] Can send in both directions

**Owner:** Messaging Team
**Time:** 45 min

### 2.3 Test File Transfer
```bash
# Create test file
echo "Test content for Archipel" > test.txt

# Terminal 1: Sender
Node_A> send <Node_B_ID> test.txt
# Should show progress

# Terminal 2: Receiver
Node_B> download
# Should show progress
# File should appear in ./downloads/test.txt
```

**Checklist:**
- [ ] File chunks are sent
- [ ] Download progress shown
- [ ] File successfully received
- [ ] File integrity verified (compare with original)
- [ ] Large files work (try 1 MB+)

**Owner:** Transfer Team
**Time:** 45 min

**Bug Collection:**
- [ ] All bugs documented in `BUGS.md`
- [ ] Include: error message, steps to reproduce, severity

---

## Phase 3: Feature Integration (4-8 hours)

Pick **ONE** of the following features to implement:

### Option A: Message History & Storage
**Time:** 2-3 hours
**Difficulty:** Medium

Implementation:
1. Add file storage in `messaging/chat.py`
2. Save messages with timestamp to JSON
3. Add command: `history <peer_id>` to show past messages
4. Auto-save on receive/send

**Files to Modify:**
- `messaging/chat.py` (add persistence)
- `cli/commands.py` (add `cmd_history()`)
- `main.py` (load history on startup)

**Success:** Users can see past messages with a peer

---

### Option B: Authentication & Signing
**Time:** 2-3 hours
**Difficulty:** Medium-Hard

Implementation:
1. Use RSA keys to sign messages
2. Verify sender identity
3. Prevent spoofing
4. Add signature to message packets

**Files to Modify:**
- `crypto/cipher.py` (add `sign()` and `verify()`)
- `messaging/chat.py` (sign/verify messages)
- `network/tcp_server.py` (validate signatures)

**Success:** Messages show confirmed sender identity

---

### Option C: Group Messaging
**Time:** 2-3 hours
**Difficulty:** Medium

Implementation:
1. Create group management system
2. Broadcast to group members
3. Track group membership
4. Add commands: `group_create`, `group_add`, `group_send`

**Files to Create:**
- `messaging/groups.py` (new file)

**Files to Modify:**
- `cli/commands.py` (add group commands)
- `main.py` (initialize group manager)

**Success:** Send single message to multiple peers

---

### Option D: Web UI Interface
**Time:** 3-4 hours
**Difficulty:** Medium

Implementation:
1. Create simple Flask web server
2. REST API endpoints for node operations
3. HTML/JavaScript frontend
4. Real-time updates

**Files to Create:**
- `web/app.py` (Flask server)
- `web/templates/index.html`
- `web/static/style.css`

**Files to Modify:**
- `main.py` (add Flask app initialization)
- `requirements.txt` (add flask)

**Success:** Can control node from web browser

---

### Option E: File Integrity Verification
**Time:** 1-2 hours
**Difficulty:** Easy-Medium

Implementation:
1. Calculate SHA256 hash of files
2. Send hash in file metadata
3. Verify hash on receive
4. Reject corrupted files

**Files to Modify:**
- `transfer/chunker.py` (calculate hash)
- `transfer/downloader.py` (verify hash)
- `network/tcp_server.py` (handle verification)

**Success:** Transferred files verified against corruption

---

## Phase 4: Enhancement & Polish (8-12 hours)

**Focus:** Quality, stability, demo-readiness

### 4.1 Error Messages
- [ ] All exceptions caught and logged
- [ ] User-friendly error messages
- [ ] No stack traces shown to user

### 4.2 UI Polish
- [ ] Clear output formatting
- [ ] Loading indicators for long operations
- [ ] Status indicators (✓, ✗, ...)

### 4.3 Documentation
- [ ] Code comments updated
- [ ] CLI help text complete
- [ ] README updated with new features

### 4.4 Performance
- [ ] Test with 10+ peers
- [ ] Large file transfer (100 MB)
- [ ] High-frequency messaging
- [ ] Profile bottlenecks if any

### 4.5 Testing
- [ ] Create test scenarios document
- [ ] Walk through each feature
- [ ] Record any crashes/hangs

---

## Phase 5: Stretch Goals (12-24 hours)

If core features are solid, attempt:

- [ ] **NAT Traversal**: Make it work across networks
- [ ] **Persistence Layer**: SQLite storage for messages
- [ ] **End-to-End per-peer Keys**: Diffie-Hellman key exchange
- [ ] **Mobile App**: Python Kivy app for Android
- [ ] **Performance Optimization**: Async I/O with asyncio
- [ ] **Advanced Security**: TLS/SSL for TCP connections
- [ ] **Network Diagnostics**: Latency, packet loss monitoring
- [ ] **Demo Presentation**: Slides, walkthrough, showcase

---

## Demo Preparation (Hour 22-24)

**What to Demo:**

1. **Startup** (30 seconds)
   - Start 2-3 nodes
   - Show discovery in action

2. **Peer Discovery** (1 minute)
   - Show peer list growing
   - Show automatic removal

3. **Messaging** (2 minutes)
   - Send encrypted message
   - Show it arrives correctly
   - Optionally: show encrypted content on wire

4. **File Transfer** (2 minutes)
   - Send a file (smaller for demo)
   - Show progress
   - Verify received file

5. **Feature Showcase** (3-5 minutes)
   - Demonstrate whichever feature(s) your team built
   - E.g., message history, authentication, groups, etc.

**Total Demo Time:** ~10 minutes

---

## Team Assignments

### Network Team
- Peer discovery reliability
- TCP communication robustness
- Handling disconnections

### Crypto Team
- Encryption verification
- Key management
- Security features (signing, etc.)

### Messaging Team
- Message delivery
- Message history (if chosen)
- Group messaging (if chosen)

### Transfer Team
- File chunking correctness
- Reassembly verification
- Progress tracking accuracy

### DevOps / UI Team
- Web UI (if chosen)
- Installation/setup documentation
- Demo scripts/automation

---

## Daily Sync Checklist

**Every 2 hours:**
- [ ] Phase complete?
- [ ] Blockers?
- [ ] On schedule?

**Questions to ask:**
1. Are all tests passing?
2. Any merge conflicts to resolve?
3. Do we need to pivot/adjust schedule?

---

## Git Workflow (if using version control)

```bash
# Each team: checkout to feature branch
git checkout -b feature/messaging-history

# Make changes...

# Commit regularly
git add .
git commit -m "Add message persistence"

# Sync with main
git pull origin main
git push origin feature/messaging-history

# Create pull request for review
# Once approved: merge to main
```

**Note:** Make sure `__pycache__` and `keys/` are in `.gitignore`

---

## Success Criteria

### Minimum Viable Demo ✅
- [ ] 2+ nodes discover each other
- [ ] Send encrypted message successfully
- [ ] Transfer file successfully
- [ ] Demo runs without crashing

### Strong Demo ⭐
- [ ] All of above, PLUS one integrated feature
- [ ] All error cases handled gracefully
- [ ] Performance acceptable (no lag)

### Outstanding Demo 🎉
- [ ] Multiple features integrated
- [ ] Web UI or visual enhancement
- [ ] Network stress-tested
- [ ] Comprehensive documentation
- [ ] Polished presentation

---

## Emergency Fallback

**If running behind schedule:**

- [ ] Skip optional features
- [ ] Focus on core 3: discovery, messaging, files
- [ ] Demo with just core features
- [ ] Can explain future work verbally

**If core features broken:**

- [ ] Debug the network layer first (most likely issue)
- [ ] Check `test_installation.py` for dependency errors
- [ ] Verify port availability (try different port: `python main.py --port 9000`)
- [ ] Check firewall isn't blocking multicast

---

## Resource Links

- **Python Documentation**: https://docs.python.org/3/
- **Cryptography Library**: https://cryptography.io/
- **Socket Programming**: https://docs.python.org/3/library/socket.html
- **Asyncio Guide**: https://docs.python.org/3/library/asyncio.html

---

## Good Luck! 🚀

You have a solid foundation. Focus on:
1. **Testing thoroughly** - Most issues are integration bugs
2. **Clear communication** - Keep team informed of progress
3. **Regular commits** - Don't lose work to accidents
4. **Enjoy the process** - It's a hackathon, have fun!

---

**Questions during hackathon?**
- Refer to code comments (they're detailed)
- Check README.md for architecture
- Review QUICKSTART.md for examples
- Look at other modules for patterns

**Good luck with Archipel!** 🏝️
