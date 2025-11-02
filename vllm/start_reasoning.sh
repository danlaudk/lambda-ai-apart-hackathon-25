#!/bin/bash
# Start with REASONING model (DeepSeek-V3)
# Best for: Complex reasoning, trend analysis

VENV_PYTHON="/lambda/nfs/newinstance/ai_assessment_dora/venv/bin/python"
MODEL_NAME="deepseek-ai/DeepSeek-V3"

echo "🚀 Starting vLLM with REASONING model: $MODEL_NAME"
echo "Expected speed: 60-80 tokens/sec"
echo "VRAM usage: ~45GB"
echo "Best for: Complex reasoning and analysis"
echo ""

$VENV_PYTHON -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 32768 \
    --dtype auto \
    --trust-remote-code \
    --gpu-memory-utilization 0.95

