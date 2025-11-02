#!/bin/bash
# SSH Tunnel Creator for vLLM Remote Access
# 
# This script helps you create an SSH tunnel from your local computer
# to the vLLM server running on the remote machine.
#
# USAGE (on your local computer):
#   bash create_ssh_tunnel.sh
#
# Or copy this command and run it directly:
#   ssh -L 8000:localhost:8000 ubuntu@192.222.53.238

SERVER_IP="192.222.53.238"
SERVER_USER="ubuntu"
LOCAL_PORT="8000"
REMOTE_PORT="8000"

echo "=========================================="
echo "🔐 SSH Tunnel Setup for vLLM"
echo "=========================================="
echo ""
echo "Server: $SERVER_USER@$SERVER_IP"
echo "Local Port: $LOCAL_PORT"
echo "Remote Port: $REMOTE_PORT"
echo ""
echo "This will create an encrypted tunnel so you can access"
echo "the vLLM server at: http://localhost:$LOCAL_PORT"
echo ""
echo "=========================================="
echo ""

# Check if SSH is available
if ! command -v ssh &> /dev/null; then
    echo "❌ ERROR: ssh command not found"
    echo "Please install OpenSSH client first"
    exit 1
fi

# Check if port is already in use
if command -v lsof &> /dev/null; then
    if lsof -Pi :$LOCAL_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  WARNING: Port $LOCAL_PORT is already in use on your local machine"
        echo ""
        read -p "Do you want to use a different port? (y/n): " use_different_port
        if [ "$use_different_port" = "y" ]; then
            read -p "Enter new local port number: " LOCAL_PORT
        else
            echo "Continuing anyway... (existing tunnel may interfere)"
        fi
    fi
fi

echo "📡 Creating SSH tunnel..."
echo ""
echo "Command: ssh -L $LOCAL_PORT:localhost:$REMOTE_PORT $SERVER_USER@$SERVER_IP"
echo ""
echo "💡 Tips:"
echo "   - Keep this terminal window open"
echo "   - Access vLLM at: http://localhost:$LOCAL_PORT"
echo "   - Press Ctrl+C to close the tunnel"
echo ""
echo "=========================================="
echo ""

# Create the tunnel
ssh -L $LOCAL_PORT:localhost:$REMOTE_PORT $SERVER_USER@$SERVER_IP

echo ""
echo "👋 SSH tunnel closed"

