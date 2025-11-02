# AI Agent Setup Guide - vLLM Remote Model Selection

**Purpose:** This guide is for AI agents to help users set up remote access to a vLLM server with model selection capabilities.

**Server:** `ubuntu@192.222.53.238`  
**Server Path:** `/lambda/nfs/newinstance/vllm/`

---

## Overview

The remote server has:
- ✅ **10 AI models** downloaded (2TB total)
- ✅ **vLLM server** for high-performance inference
- ✅ **Model Manager API** for remote model selection
- ✅ **H100 80GB GPU** for elite performance

The user needs to:
1. Download client files to their local computer
2. Install Python dependencies
3. Create SSH tunnel to server
4. Use Python scripts to select models and run inference

---

## Step 1: Download Required Files

Help the user download these files from the server to their local computer:

### Required Files:
```bash
# Create directory on local computer
mkdir ~/vllm_client
cd ~/vllm_client

# Download client library (REQUIRED)
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/vllm_client.py .

# Download SSH tunnel script (REQUIRED)
# For Linux/Mac:
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/local_setup/start_tunnel.sh .

# For Windows:
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/local_setup/start_tunnel.bat .

# Download test script (RECOMMENDED)
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/local_setup/test_connection.py .

# Download example script (OPTIONAL)
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/local_setup/my_first_script.py .
```

### Automated Setup (Alternative):
```bash
# Download and run automated setup
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/local_setup/setup_local.sh .
chmod +x setup_local.sh
./setup_local.sh
```

---

## Step 2: Install Python Dependencies

Help the user install required Python packages:

```bash
pip install openai requests
```

Or if using pip3:
```bash
pip3 install openai requests
```

---

## Step 3: Make Scripts Executable

On Linux/Mac:
```bash
chmod +x start_tunnel.sh test_connection.py
```

On Windows, this step is not needed.

---

## Step 4: Start SSH Tunnel

The user needs to create an SSH tunnel to access the server securely.

### On Linux/Mac:
```bash
./start_tunnel.sh
```

This runs:
```bash
ssh -L 8000:localhost:8000 -L 8001:localhost:8001 ubuntu@192.222.53.238
```

### On Windows:
```cmd
start_tunnel.bat
```

Or manually:
```cmd
ssh -L 8000:localhost:8000 -L 8001:localhost:8001 ubuntu@192.222.53.238
```

**Important:** Keep this terminal open! The tunnel must stay active.

---

## Step 5: Test Connection

In a **new terminal** (while SSH tunnel is running):

```bash
cd ~/vllm_client
python test_connection.py
```

This will:
- ✅ Test connection to Model Manager (port 8001)
- ✅ List available models
- ✅ Test connection to vLLM server (port 8000)

---

## Step 6: Use in Python Scripts

Now the user can use the vLLM client in their Python scripts:

### Basic Example:
```python
from vllm_client import VLLMClient

# Connect to server
client = VLLMClient()

# List available models
client.print_available_models()

# Select a model
client.select_model("qwen-14b-fast")

# Use it
response = client.chat("What is machine learning?")
print(response)
```

### YouTube Transcript Analysis Example:
```python
from vllm_client import VLLMClient

# Connect
client = VLLMClient()

# Select fast model for processing
client.select_model("qwen-14b-fast")

# Extract claims from transcript
transcript = """
Your YouTube video transcript here...
"""

claims = client.extract_claims(transcript)
print(claims)
```

### Advanced Example (Model Switching):
```python
from vllm_client import VLLMClient

client = VLLMClient()

# Use fast model for initial processing
client.select_model("qwen-14b-fast")
summary = client.chat("Summarize this: ...")

# Switch to reasoning model for analysis
client.select_model("deepseek-v3-reasoning")
analysis = client.chat("Analyze trends in: " + summary)

# Switch to structured model for JSON output
client.select_model("t3q-structured")
structured = client.extract_claims(transcript)
```

---

## Available Models

Help the user choose the right model for their task:

| Model ID | Speed | VRAM | Best For |
|----------|-------|------|----------|
| `qwen-14b-fast` | 150-200 tok/s | 28GB | Fast processing, high throughput |
| `qwen-72b-quality` | 50-70 tok/s | 50GB | Maximum quality, complex analysis |
| `deepseek-v3-reasoning` | 60-80 tok/s | 45GB | Complex reasoning, trend analysis |
| `qwen-vl-7b-multimodal` | 100-120 tok/s | 12GB | Images + text analysis |
| `qwen-vl-72b-multimodal` | 40-60 tok/s | 70GB | Best quality multimodal |
| `mistral-large-chat` | 40-60 tok/s | 70GB | Conversations, instruction following |
| `phi-4-quantized` | 200+ tok/s | 4GB | Parallel processing, low memory |
| `t3q-structured` | 120-150 tok/s | 28GB | Structured JSON output |
| `calme-analysis` | 45-65 tok/s | 60GB | Complex analysis tasks |
| `rombos-merge` | 50-70 tok/s | 50GB | Combined model strengths |

---

## VLLMClient API Reference

### Connection:
```python
client = VLLMClient(
    vllm_url="http://localhost:8000",      # vLLM server
    manager_url="http://localhost:8001",   # Model Manager
    api_key="dummy"                        # Not used, but required
)
```

### Model Selection:
```python
# List available models
models = client.list_available_models()
client.print_available_models()

# Get current model
current = client.get_current_model()

# Select a model (waits for loading)
client.select_model("qwen-14b-fast", wait=True, timeout=300)
```

### Chat:
```python
# Simple chat
response = client.chat("Your question here")

# With system prompt
response = client.chat(
    message="Your question",
    system_prompt="You are a helpful assistant",
    max_tokens=500,
    temperature=0.7
)

# Streaming
response = client.chat("Your question", stream=True)
```

### Claim Extraction:
```python
# Extract claims from transcript
claims = client.extract_claims(
    transcript="Your transcript here",
    max_tokens=1000,
    temperature=0.0
)
```

---

## Troubleshooting

### Problem: "Connection refused"
**Cause:** SSH tunnel not running or model manager not started  
**Solution:**
1. Check SSH tunnel is running: `./start_tunnel.sh`
2. Verify model manager is running on server
3. Test with: `curl http://localhost:8001/status`

### Problem: "No module named 'vllm_client'"
**Cause:** File not in current directory  
**Solution:**
```bash
# Check if file exists
ls -l vllm_client.py

# If not, download it
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/vllm_client.py .
```

### Problem: "No module named 'openai'"
**Cause:** Dependencies not installed  
**Solution:**
```bash
pip install openai requests
```

### Problem: Model loading takes too long
**Cause:** Large models take time to load  
**Solution:** This is normal! Models take 1-3 minutes to load. The client waits automatically.

### Problem: "Model manager not responding"
**Cause:** Model manager not started on server  
**Solution:**
```bash
# On server
ssh ubuntu@192.222.53.238
cd /lambda/nfs/newinstance/vllm
./start_model_manager.sh
```

---

## Verification Checklist

Before the user can use the system, verify:

- [ ] Files downloaded to local computer (`vllm_client.py`, `start_tunnel.sh`)
- [ ] Python dependencies installed (`pip install openai requests`)
- [ ] Model manager running on server (`./start_model_manager.sh`)
- [ ] SSH tunnel running on local computer (`./start_tunnel.sh`)
- [ ] Test script passes (`python test_connection.py`)

---

## Additional Documentation

If the user needs more details, they can download:

```bash
# Complete setup guide
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/LOCAL_SETUP_INSTRUCTIONS.md .

# Usage examples
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/MODEL_SELECTION_GUIDE.md .

# Quick reference
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/MODEL_SELECTION_QUICKSTART.txt .

# Summary
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/SETUP_SUMMARY.txt .
```

---

## Summary for AI Agents

When helping a user set up this system:

1. **Download files** - Use `scp` to download `vllm_client.py` and tunnel scripts
2. **Install dependencies** - `pip install openai requests`
3. **Start tunnel** - `./start_tunnel.sh` (keep running)
4. **Test connection** - `python test_connection.py`
5. **Write code** - Use `VLLMClient()` in Python scripts

The user can then:
- Choose from 10 AI models
- Switch models during runtime
- Process data with high-performance GPU inference
- Use OpenAI-compatible API

**Key Point:** The SSH tunnel must stay open while using the system!

