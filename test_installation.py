#!/usr/bin/env python3
"""
Simple test script to verify Archipel installation and imports.
Run this before starting nodes to catch any import/dependency issues.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing Archipel imports...")
    print("-" * 50)
    
    errors = []
    
    # Test standard library imports
    test_modules = [
        ("socket", "Network socket support"),
        ("threading", "Threading support"),
        ("json", "JSON parsing"),
        ("time", "Time functions"),
        ("uuid", "UUID generation"),
        ("hashlib", "Hash functions"),
        ("pathlib", "File path handling"),
    ]
    
    for module, description in test_modules:
        try:
            __import__(module)
            print(f"✓ {module:20} - {description}")
        except ImportError as e:
            errors.append(f"✗ {module:20} - {description}\n    Error: {e}")
            print(f"✗ {module:20} - {description}")
    
    # Test cryptography library
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        print(f"✓ {'cryptography':20} - AES, RSA, PBKDF2")
    except ImportError as e:
        errors.append(f"✗ cryptography - Not installed\n    Error: {e}\n    Install with: pip install cryptography")
        print(f"✗ {'cryptography':20} - Not installed (required)")
    
    # Test project modules
    print()
    print("Testing Archipel modules...")
    print("-" * 50)
    
    project_modules = [
        ("crypto.keys", "Key management"),
        ("crypto.cipher", "Encryption/decryption"),
        ("network.discovery", "Peer discovery"),
        ("network.peer_table", "Peer management"),
        ("network.tcp_server", "TCP communication"),
        ("messaging.chat", "Encrypted messaging"),
        ("transfer.chunker", "File chunking"),
        ("transfer.downloader", "File downloading"),
        ("cli.commands", "CLI interface"),
    ]
    
    for module, description in project_modules:
        try:
            __import__(module)
            print(f"✓ {module:25} - {description}")
        except ImportError as e:
            errors.append(f"✗ {module:25} - {description}\n    Error: {e}")
            print(f"✗ {module:25} - {description}")
    
    print()
    print("-" * 50)
    
    if errors:
        print(f"\n❌ {len(errors)} error(s) found:\n")
        for error in errors:
            print(error)
        print("\nFix errors above before running the node.")
        return False
    else:
        print("\n✅ All imports successful!")
        print("\nYou can now start the node:")
        print("  python main.py")
        return True


def check_file_structure():
    """Check that all required files exist."""
    print("\nChecking file structure...")
    print("-" * 50)
    
    required_files = [
        "main.py",
        "requirements.txt",
        "network/__init__.py",
        "network/discovery.py",
        "network/peer_table.py",
        "network/tcp_server.py",
        "crypto/__init__.py",
        "crypto/keys.py",
        "crypto/cipher.py",
        "messaging/__init__.py",
        "messaging/chat.py",
        "transfer/__init__.py",
        "transfer/chunker.py",
        "transfer/downloader.py",
        "cli/__init__.py",
        "cli/commands.py",
    ]
    
    errors = []
    for filepath in required_files:
        path = Path(filepath)
        if path.exists():
            print(f"✓ {filepath}")
        else:
            errors.append(f"✗ {filepath} - NOT FOUND")
            print(f"✗ {filepath} - NOT FOUND")
    
    print()
    
    if errors:
        print(f"❌ {len(errors)} file(s) missing!")
        return False
    else:
        print("✅ All files present!")
        return True

def main():
    print("=" * 50)
    print("Archipel Installation Test")
    print("=" * 50)
    print()
    
    # Check structure
    structure_ok = check_file_structure()
    print()
    
    # Test imports
    imports_ok = test_imports()
    
    print()
    print("=" * 50)
    
    if structure_ok and imports_ok:
        print("✅ Installation verified! Ready to run.")
        return 0
    else:
        print("❌ Installation incomplete. See errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
