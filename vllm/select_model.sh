#!/bin/bash
# Interactive Model Selector for vLLM

echo "=========================================="
echo "🎯 vLLM Model Selector"
echo "=========================================="
echo ""
echo "Available models:"
echo ""
echo "1. Qwen2.5-14B-Instruct (FAST) ⚡"
echo "   - Speed: 150-200 tokens/sec"
echo "   - VRAM: ~12GB"
echo "   - Best for: High throughput, fast responses"
echo ""
echo "2. Qwen2.5-72B-Instruct (QUALITY) 💎"
echo "   - Speed: 50-70 tokens/sec"
echo "   - VRAM: ~50GB"
echo "   - Best for: Maximum quality, complex analysis"
echo ""
echo "3. DeepSeek-V3 (REASONING) 🧠"
echo "   - Speed: 60-80 tokens/sec"
echo "   - VRAM: ~45GB"
echo "   - Best for: Complex reasoning, trend analysis"
echo ""
echo "4. Qwen2-VL-7B-Instruct (MULTIMODAL) 🖼️"
echo "   - Speed: 100-120 tokens/sec"
echo "   - VRAM: ~12GB"
echo "   - Best for: Images + text (thumbnails + transcripts)"
echo ""
echo "5. Mistral-Large-Instruct-2411 (CHAT) 💬"
echo "   - Speed: 40-60 tokens/sec"
echo "   - VRAM: ~70GB"
echo "   - Best for: Conversations, instruction following"
echo ""
echo "6. phi-4-unsloth-bnb-4bit (QUANTIZED) 🔧"
echo "   - Speed: 200+ tokens/sec"
echo "   - VRAM: ~4GB"
echo "   - Best for: Parallel processing, low memory"
echo ""
echo "=========================================="
echo ""

read -p "Select model (1-6): " choice

case $choice in
    1)
        echo "Starting FAST model..."
        ./start_fast.sh
        ;;
    2)
        echo "Starting QUALITY model..."
        ./start_quality.sh
        ;;
    3)
        echo "Starting REASONING model..."
        ./start_reasoning.sh
        ;;
    4)
        echo "Starting MULTIMODAL model..."
        ./start_multimodal.sh
        ;;
    5)
        echo "Starting CHAT model..."
        VENV_PYTHON="/lambda/nfs/newinstance/ai_assessment_dora/venv/bin/python"
        $VENV_PYTHON -m vllm.entrypoints.openai.api_server \
            --model "mistralai/Mistral-Large-Instruct-2411" \
            --host 0.0.0.0 \
            --port 8000 \
            --max-model-len 32768 \
            --dtype auto \
            --trust-remote-code \
            --gpu-memory-utilization 0.95
        ;;
    6)
        echo "Starting QUANTIZED model..."
        VENV_PYTHON="/lambda/nfs/newinstance/ai_assessment_dora/venv/bin/python"
        $VENV_PYTHON -m vllm.entrypoints.openai.api_server \
            --model "unsloth/phi-4-unsloth-bnb-4bit" \
            --host 0.0.0.0 \
            --port 8000 \
            --max-model-len 16384 \
            --dtype auto \
            --trust-remote-code \
            --gpu-memory-utilization 0.95
        ;;
    *)
        echo "Invalid selection. Please run again and choose 1-6."
        exit 1
        ;;
esac

