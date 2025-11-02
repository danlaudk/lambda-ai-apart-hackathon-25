#!/bin/bash
# Start with QUALITY model (Qwen2.5-72B)
# Best for: Maximum quality, complex analysis

VENV_PYTHON="/lambda/nfs/newinstance/ai_assessment_dora/venv/bin/python"
MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"

echo "🚀 Starting vLLM with QUALITY model: $MODEL_NAME"
echo "Expected speed: 50-70 tokens/sec"
echo "VRAM usage: ~50GB"
echo ""

$VENV_PYTHON -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 32768 \
    --dtype auto \
    --trust-remote-code \
    --gpu-memory-utilization 0.95

