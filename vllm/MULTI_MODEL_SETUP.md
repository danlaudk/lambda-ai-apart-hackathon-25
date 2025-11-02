# Multi-Model Serving Setup Guide

This guide explains how to use the multi-model serving system that allows multiple AI models to run simultaneously on different ports.

## Overview

The multi-model serving system enables:
- Running multiple vLLM servers simultaneously
- Each model runs on its own port (starting from port 8002)
- Load/unload models independently
- No need to stop one model to load another

## Files

The multi-model setup uses files with the `_multi` suffix:

- `model_manager_multi.py` - Multi-model manager API
- `vllm_client_multi.py` - Client for connecting to multiple models
- `start_model_manager_multi.sh` - Script to start the multi-model manager
- `start_vllm_server_multi.sh` - Script to start individual vLLM servers (used internally)

## Quick Start

### 1. Start the Multi-Model Manager

```bash
cd /home/ubuntu/newinstance/vllm
./start_model_manager_multi.sh
```

Or run in background with screen:
```bash
screen -S model_manager_multi ./start_model_manager_multi.sh
```

The manager will start on port **8001**.

### 2. Use the Multi-Model Client

```python
from vllm_client_multi import VLLMClientMulti

# Connect to multi-model manager
client = VLLMClientMulti(
    server_ip="localhost",  # or your server IP
    manager_api_key="your-api-key-here"  # Get from .api_key file
)

# Load multiple models
client.load_model("qwen-14b-fast")      # Will start on port 8002
client.load_model("qwen-72b-quality")  # Will start on port 8003
client.load_model("deepseek-v3-reasoning")  # Will start on port 8004

# Use specific models
response1 = client.chat("qwen-14b-fast", "What is machine learning?")
response2 = client.chat("qwen-72b-quality", "Explain quantum computing")

# Unload a model when done
client.unload_model("qwen-14b-fast")
```

## API Endpoints

The multi-model manager provides the following API endpoints:

### List Available Models
```bash
GET /models/available
Headers: X-API-Key: <your-api-key>
```

### Get All Loaded Models
```bash
GET /models/loaded
Headers: X-API-Key: <your-api-key>
```

### Get Model Status
```bash
GET /models/<model_id>/status
Headers: X-API-Key: <your-api-key>
```

### Load a Model
```bash
POST /models/<model_id>/load
Headers: X-API-Key: <your-api-key>
```

### Unload a Model
```bash
POST /models/<model_id>/unload
Headers: X-API-Key: <your-api-key>
```

### Get Manager Status
```bash
GET /status
Headers: X-API-Key: <your-api-key>
```

## Port Allocation

- Ports start from **8002** and increment for each new model
- Port **8001** is reserved for the model manager API
- Port **8000** is reserved for the original single-model setup (if used)
- Ports are allocated sequentially and do not get reused after unloading

## Example: Loading Multiple Models

```python
from vllm_client_multi import VLLMClientMulti

client = VLLMClientMulti(
    server_ip="localhost",
    manager_api_key="your-key-here"
)

# Load models
models_to_load = [
    "qwen-14b-fast",
    "qwen-72b-quality",
    "deepseek-v3-reasoning"
]

for model_id in models_to_load:
    print(f"Loading {model_id}...")
    client.load_model(model_id)
    print(f"✅ {model_id} loaded")

# Check what's loaded
client.print_loaded_models()

# Use different models for different tasks
fast_response = client.chat("qwen-14b-fast", "Quick summary")
quality_response = client.chat("qwen-72b-quality", "Detailed analysis")
reasoning_response = client.chat("deepseek-v3-reasoning", "Complex problem")
```

## Differences from Single-Model Setup

### Single-Model Setup (Original)
- One model at a time
- Model switching requires stopping current model
- Fixed port (8000)
- Files: `model_manager.py`, `vllm_client.py`

### Multi-Model Setup
- Multiple models simultaneously
- Load/unload independently
- Dynamic ports (8002+)
- Files: `model_manager_multi.py`, `vllm_client_multi.py`

## Troubleshooting

### Model won't load
- Check if you have enough GPU memory
- Verify the model name is correct
- Check server logs for errors

### Port conflicts
- Ensure ports 8002+ are available
- Check if another process is using the ports

### API key issues
- API key is in `.api_key` file
- Must be included in all API requests as `X-API-Key` header

## Resource Management

**Important**: Each model consumes GPU memory. Be mindful of:
- Total available GPU VRAM
- Number of models loaded simultaneously
- Model sizes (smaller models use less VRAM)

**Recommendation**: Load only the models you need. Unload models when not in use to free GPU memory.

## Notes

- The multi-model manager uses the same API key as the single-model manager (from `.api_key` file)
- Models can take 1-3 minutes to load
- Each model runs as an independent vLLM server process
- The manager tracks all loaded models and their ports

