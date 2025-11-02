#!/bin/bash
################################################################################
# Start vLLM Multi-Model Manager API
################################################################################
#
# This script starts the Multi-Model Manager API service that enables
# running multiple vLLM servers simultaneously on different ports.
# Each model runs on its own port starting from 8002.
#
# USAGE:
#   ./start_model_manager_multi.sh
#
# Or run in background with screen:
#   screen -S model_manager_multi ./start_model_manager_multi.sh
#
# REQUIREMENTS:
#   pip install flask flask-cors psutil requests
#
################################################################################

echo "================================================================================"
echo "🚀 Starting vLLM Multi-Model Manager API"
echo "================================================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if model_manager_multi.py exists
if [ ! -f "model_manager_multi.py" ]; then
    echo "❌ Error: model_manager_multi.py not found"
    echo "Please ensure you are in the correct directory"
    echo "Expected location: /lambda/nfs/newinstance/vllm/"
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: flask not found"
    echo "Installing dependencies..."
    pip install flask flask-cors psutil requests
fi

python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: requests not found"
    echo "Installing dependencies..."
    pip install requests
fi

echo "✅ Dependencies OK"
echo ""

# Start Multi-Model Manager
echo "🚀 Starting Multi-Model Manager on port 8001..."
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Keep this terminal open (or use screen/tmux)"
echo "   - Multi-Model Manager will manage multiple vLLM instances"
echo "   - Models will start on ports 8002, 8003, 8004, etc."
echo "   - Each model runs on its own port independently"
echo "   - Clients can connect via SSH tunnel to port 8001"
echo ""
echo "================================================================================"
echo ""

python3 model_manager_multi.py

echo ""
echo "================================================================================"
echo "Multi-Model Manager stopped"
echo "================================================================================"

