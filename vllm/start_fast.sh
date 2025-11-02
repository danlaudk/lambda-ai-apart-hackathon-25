#!/bin/bash
# Quick start with FAST model (Qwen2.5-14B)
# Best for: High throughput, fast responses

VENV_PYTHON="/lambda/nfs/newinstance/ai_assessment_dora/venv/bin/python"
MODEL_NAME="Qwen/Qwen2.5-14B-Instruct"

echo "🚀 Starting vLLM with FAST model: $MODEL_NAME"
echo "Expected speed: 150-200 tokens/sec"
echo ""

$VENV_PYTHON -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 32768 \
    --dtype auto \
    --trust-remote-code \
    --gpu-memory-utilization 0.95

