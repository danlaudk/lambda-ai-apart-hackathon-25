#!/bin/bash

# vLLM Multi-Model Server Startup Script
# This script starts a vLLM server with a specific model on a specific port
# Used by the multi-model manager to start individual model instances

# Usage:
#   ./start_vllm_server_multi.sh <model_name> <port>
# Example:
#   ./start_vllm_server_multi.sh "Qwen/Qwen2.5-14B-Instruct" 8002

# Path to Python virtual environment
VENV_PYTHON="/lambda/nfs/newinstance/ai_assessment_dora/venv/bin/python"

# Get model name and port from arguments
MODEL_NAME="${1:-Qwen/Qwen2.5-14B-Instruct}"
PORT="${2:-8002}"
HOST="0.0.0.0"

# Default max model length
MAX_MODEL_LEN=32768

# Check if model name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <model_name> <port>"
    echo "Example: $0 \"Qwen/Qwen2.5-14B-Instruct\" 8002"
    exit 1
fi

echo "=========================================="
echo "🚀 Starting vLLM Multi-Model Server"
echo "=========================================="
echo "Model: $MODEL_NAME"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Server URL: http://$HOST:$PORT"
echo "=========================================="
echo ""

# Check if venv Python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ ERROR: Python virtual environment not found at $VENV_PYTHON"
    echo "Please check the path and try again."
    exit 1
fi

# Check if vLLM is installed
if ! $VENV_PYTHON -c "import vllm" 2>/dev/null; then
    echo "❌ ERROR: vLLM not installed in virtual environment"
    echo "Installing vLLM..."
    $VENV_PYTHON -m pip install vllm
fi

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "❌ ERROR: Port $PORT is already in use"
    exit 1
fi

echo "📦 Loading model (this may take a few minutes)..."
echo ""

# Start vLLM server with OpenAI-compatible API
$VENV_PYTHON -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --host "$HOST" \
    --port "$PORT" \
    --max-model-len "$MAX_MODEL_LEN" \
    --dtype auto \
    --trust-remote-code \
    --gpu-memory-utilization 0.95


