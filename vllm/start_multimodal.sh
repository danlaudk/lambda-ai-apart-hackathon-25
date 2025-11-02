#!/bin/bash
# Start with MULTIMODAL model (Qwen2-VL-7B)
# Best for: Analyzing images + text (thumbnails + transcripts)

VENV_PYTHON="/lambda/nfs/newinstance/ai_assessment_dora/venv/bin/python"
MODEL_NAME="Qwen/Qwen2-VL-7B-Instruct"

echo "🚀 Starting vLLM with MULTIMODAL model: $MODEL_NAME"
echo "Expected speed: 100-120 tokens/sec"
echo "VRAM usage: ~12GB"
echo "Capabilities: Images + Text analysis"
echo ""

$VENV_PYTHON -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 32768 \
    --dtype auto \
    --trust-remote-code \
    --gpu-memory-utilization 0.95

