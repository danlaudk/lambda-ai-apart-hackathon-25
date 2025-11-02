#!/bin/bash

# vLLM Server Startup Script
# This script starts a vLLM server with your chosen model

# Path to Python virtual environment
VENV_PYTHON="/lambda/nfs/newinstance/ai_assessment_dora/venv/bin/python"

# Default model (change this to use a different model)
# Options:
#   - Qwen/Qwen2.5-14B-Instruct (RECOMMENDED - Fast & Good Quality)
#   - Qwen/Qwen2.5-72B-Instruct (Maximum Quality)
#   - deepseek-ai/DeepSeek-V3 (Best Reasoning)
#   - Qwen/Qwen2-VL-7B-Instruct (Multimodal - Images + Text)
#   - mistralai/Mistral-Large-Instruct-2411 (Top Chat Model)
#   - unsloth/phi-4-unsloth-bnb-4bit (Quantized - Low VRAM)

MODEL_NAME="Qwen/Qwen2.5-14B-Instruct"
HOST="0.0.0.0"
PORT=8000

echo "=========================================="
echo "🚀 Starting vLLM Server"
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

echo "📦 Loading model (this may take a few minutes)..."
echo ""

# Start vLLM server with OpenAI-compatible API
$VENV_PYTHON -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --host "$HOST" \
    --port "$PORT" \
    --max-model-len 32768 \
    --dtype auto \
    --trust-remote-code \
    --gpu-memory-utilization 0.95

