#!/bin/bash
# Archipel Node Startup Script for Linux/macOS

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting Archipel Node..."
python3 main.py --port 0 --keys ./keys
