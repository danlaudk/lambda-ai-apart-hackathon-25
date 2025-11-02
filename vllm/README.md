# vLLM Setup for YouTube Transcript Analysis

This directory contains the vLLM server setup for running the DeepSeek model efficiently.

## What is vLLM?

vLLM is a high-performance inference engine for LLMs that provides:
- **Fast inference**: 10-20x faster than vanilla transformers
- **Efficient memory usage**: PagedAttention for better GPU memory management
- **OpenAI-compatible API**: Easy to integrate with existing code
- **Batching**: Automatic request batching for better throughput

## Setup

### 1. Start the vLLM Server

```bash
cd /lambda/nfs/newinstance/vllm
./start_vllm_server.sh
```

The server will:
- Download the DeepSeek model (first time only)
- Start on `http://0.0.0.0:8000`
- Provide an OpenAI-compatible API

### 2. Test the Server

In a new terminal:

```bash
cd /lambda/nfs/newinstance/vllm
python test_vllm_client.py
```

## Using vLLM in Your Code

Instead of loading the model directly in Python, you make HTTP requests to the vLLM server:

```python
from openai import OpenAI

# Point to local vLLM server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # vLLM doesn't require auth
)

response = client.chat.completions.create(
    model="MasterControlAIML/DeepSeek-R1-Qwen2.5-1.5b-SFT-R1-JSON-Unstructured-To-Structured",
    messages=[{"role": "user", "content": "Extract claims from this text..."}],
    max_tokens=1024
)

print(response.choices[0].message.content)
```

## Benefits for Your Use Case

1. **Faster processing**: Process transcripts much faster
2. **Better memory management**: Model stays loaded in vLLM, not in your Python script
3. **Easy scaling**: Can process multiple transcripts in parallel
4. **Simple code**: Just HTTP requests instead of model loading

## Configuration

Edit `start_vllm_server.sh` to change:
- `PORT`: Server port (default: 8000)
- `--max-model-len`: Maximum sequence length (default: 4096)
- `--dtype`: Data type (auto, float16, bfloat16)

## Monitoring

Check server logs for:
- Model loading progress
- Request processing times
- Memory usage
- Errors

## Stopping the Server

Press `Ctrl+C` in the terminal running the server.
