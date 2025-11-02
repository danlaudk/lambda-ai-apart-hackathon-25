#!/bin/bash
################################################################################
# Start vLLM Model Manager API
################################################################################
#
# This script starts the Model Manager API service that enables runtime
# model switching for vLLM.
#
# USAGE:
#   ./start_model_manager.sh
#
# Or run in background with screen:
#   screen -S model_manager ./start_model_manager.sh
#
# REQUIREMENTS:
#   pip install flask flask-cors psutil requests
#
################################################################################

echo "================================================================================"
echo "🚀 Starting vLLM Model Manager API"
echo "================================================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if model_manager_api.py exists
if [ ! -f "model_manager_api.py" ]; then
    echo "❌ Error: model_manager_api.py not found"
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

echo "✅ Dependencies OK"
echo ""

# Start Model Manager
echo "🚀 Starting Model Manager on port 8001..."
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Keep this terminal open (or use screen/tmux)"
echo "   - Model Manager will manage vLLM instances automatically"
echo "   - Clients can connect via SSH tunnel to port 8001"
echo ""
echo "================================================================================"
echo ""

python3 model_manager_api.py

echo ""
echo "================================================================================"
echo "Model Manager stopped"
echo "================================================================================"

