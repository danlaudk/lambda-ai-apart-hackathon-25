# 🖥️ Local Computer Setup - Model Selection Feature

This guide shows you how to set up your **local computer** to connect to the vLLM server and select which AI model to use.

---

## 📋 **Prerequisites**

- SSH access to server: `ubuntu@192.222.53.238`
- Python 3.8+ installed on your local computer
- `pip` package manager

---

## 🚀 **Setup Instructions**

### **Step 1: Create a Project Directory**

On your **local computer**, create a directory for your vLLM client:

```bash
# Create directory
mkdir ~/vllm_client
cd ~/vllm_client
```

---

### **Step 2: Download Required Files**

Download the client library and documentation from the server:

```bash
# Download Python client library (REQUIRED)
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/vllm_client.py .

# Download test script (OPTIONAL - for testing)
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/test_model_selection.py .

# Download documentation (OPTIONAL - for reference)
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/MODEL_SELECTION_GUIDE.md .
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/MODEL_SELECTION_QUICKSTART.txt .
```

---

### **Step 3: Install Python Dependencies**

Install required Python packages on your local computer:

```bash
pip install openai requests
```

Or if you use a virtual environment (recommended):

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install openai requests
```

---

### **Step 4: Create SSH Tunnel Script**

Create a script to easily start the SSH tunnels:

**On Linux/Mac:**

Create file `start_tunnel.sh`:

```bash
#!/bin/bash
echo "🔐 Creating SSH tunnels to vLLM server..."
echo ""
echo "Port 8000: vLLM Inference API"
echo "Port 8001: Model Manager API"
echo ""
echo "Keep this terminal open!"
echo "Press Ctrl+C to disconnect"
echo ""

ssh -L 8000:localhost:8000 -L 8001:localhost:8001 ubuntu@192.222.53.238
```

Make it executable:
```bash
chmod +x start_tunnel.sh
```

**On Windows:**

Create file `start_tunnel.bat`:

```batch
@echo off
echo Creating SSH tunnels to vLLM server...
echo.
echo Port 8000: vLLM Inference API
echo Port 8001: Model Manager API
echo.
echo Keep this window open!
echo Press Ctrl+C to disconnect
echo.

ssh -L 8000:localhost:8000 -L 8001:localhost:8001 ubuntu@192.222.53.238
```

---

### **Step 5: Create a Simple Test Script**

Create `test_connection.py` to verify everything works:

```python
#!/usr/bin/env python3
"""
Test connection to vLLM server with model selection
"""

from vllm_client import VLLMClient

def main():
    print("=" * 80)
    print("🧪 Testing vLLM Connection with Model Selection")
    print("=" * 80)
    print()
    
    # Create client
    print("📡 Connecting to vLLM server...")
    try:
        client = VLLMClient(
            vllm_url="http://localhost:8000",
            manager_url="http://localhost:8001"
        )
        print("✅ Connected!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Make sure:")
        print("1. SSH tunnel is running (./start_tunnel.sh)")
        print("2. Model manager is running on server")
        return
    
    print()
    
    # List available models
    print("📋 Available Models:")
    print("-" * 80)
    client.print_available_models()
    
    # Get current model
    print("🔍 Checking current model...")
    current = client.get_current_model()
    if current:
        print(f"✅ Current model: {current['model_id']}")
        print(f"   {current['model_info']['description']}")
    else:
        print("⚠️  No model currently loaded")
        print("   Selecting default model...")
        client.select_model("qwen-14b-fast")
    
    print()
    
    # Test chat
    print("=" * 80)
    print("💬 Testing Chat")
    print("=" * 80)
    print()
    
    question = "What is 2+2? Answer in one sentence."
    print(f"Question: {question}")
    print("Response: ", end="", flush=True)
    
    try:
        response = client.chat(question, max_tokens=50, stream=True)
        print()
        print()
        print("✅ SUCCESS! Everything is working!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print()
    print("=" * 80)
    print("🎉 Setup Complete!")
    print("=" * 80)
    print()
    print("You can now use the vLLM client in your scripts!")
    print()

if __name__ == "__main__":
    main()
```

Make it executable:
```bash
chmod +x test_connection.py  # Linux/Mac only
```

---

## 🎯 **Usage Workflow**

### **Every Time You Want to Use the vLLM Server:**

**Terminal 1 - SSH Tunnel (keep open):**
```bash
cd ~/vllm_client
./start_tunnel.sh  # Linux/Mac
# OR
start_tunnel.bat  # Windows
```

**Terminal 2 - Your Python Scripts:**
```bash
cd ~/vllm_client
python test_connection.py  # Test it works
python your_script.py      # Run your actual script
```

---

## 📝 **Example: Your First Script**

Create `my_first_script.py`:

```python
from vllm_client import VLLMClient

# Connect to server
client = VLLMClient()

# List available models
print("Available models:")
client.print_available_models()

# Select a model
print("\nSelecting fast model...")
client.select_model("qwen-14b-fast")

# Use it
print("\nAsking a question...")
response = client.chat("Explain machine learning in one sentence")
print(f"Response: {response}")

# Extract claims from YouTube transcript
print("\nExtracting claims from transcript...")
transcript = """
Python is the most popular programming language in 2024.
It was created by Guido van Rossum in 1991.
Over 8 million developers use Python worldwide.
"""

claims = client.extract_claims(transcript)
print(f"Claims: {claims}")

print("\n✅ Done!")
```

Run it:
```bash
python my_first_script.py
```

---

## 🔧 **Advanced: Integration with Existing Scripts**

If you already have scripts using OpenAI API, just add model selection:

**Before (without model selection):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-14B-Instruct",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**After (with model selection):**
```python
from vllm_client import VLLMClient

# Add model selection
client = VLLMClient()
client.select_model("qwen-14b-fast")  # Choose your model!

# Use simplified API
response = client.chat("Hello")
print(response)
```

---

## 📊 **Model Selection Guide**

Choose the right model for your task:

| Task | Recommended Model | Why |
|------|------------------|-----|
| **Fast processing (1000s of videos)** | `qwen-14b-fast` | 150-200 tokens/sec |
| **Best quality extraction** | `qwen-72b-quality` | Maximum accuracy |
| **Trend analysis** | `deepseek-v3-reasoning` | Best reasoning |
| **Structured JSON output** | `t3q-structured` | Optimized for JSON |
| **Images + text** | `qwen-vl-7b-multimodal` | Multimodal |
| **Low memory** | `phi-4-quantized` | Only 4GB VRAM |

**Example - Optimize for different phases:**
```python
from vllm_client import VLLMClient

client = VLLMClient()

# Phase 1: Fast extraction
client.select_model("qwen-14b-fast")
for video in videos:
    claims = client.extract_claims(video.transcript)

# Phase 2: Deep analysis
client.select_model("deepseek-v3-reasoning")
analysis = client.chat("Analyze trends in these claims...")
```

---

## ⚠️ **Troubleshooting**

### **Problem: "Connection refused" on port 8000 or 8001**

**Solution:**
1. Check SSH tunnel is running: `./start_tunnel.sh`
2. Check model manager is running on server:
   ```bash
   ssh ubuntu@192.222.53.238
   cd /lambda/nfs/newinstance/vllm
   ./start_model_manager.sh
   ```

---

### **Problem: "ModuleNotFoundError: No module named 'vllm_client'"**

**Solution:**
Make sure `vllm_client.py` is in the same directory as your script, or install it:
```bash
# Check file exists
ls -l vllm_client.py

# If not, download it again
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/vllm_client.py .
```

---

### **Problem: "No module named 'openai'" or "No module named 'requests'"**

**Solution:**
Install dependencies:
```bash
pip install openai requests
```

---

### **Problem: Model loading takes too long**

**Solution:**
This is normal! Large models take 1-3 minutes to load. The client waits automatically.
- Small models (14B): ~1-2 minutes
- Large models (72B+): ~2-3 minutes

---

### **Problem: SSH tunnel keeps disconnecting**

**Solution:**
Add keep-alive to SSH config. Create/edit `~/.ssh/config`:
```
Host vllm-server
    HostName 192.222.53.238
    User ubuntu
    LocalForward 8000 localhost:8000
    LocalForward 8001 localhost:8001
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Then connect with:
```bash
ssh vllm-server
```

---

## 📁 **Your Directory Structure**

After setup, your local directory should look like:

```
~/vllm_client/
├── vllm_client.py                    # Client library (REQUIRED)
├── start_tunnel.sh                   # SSH tunnel script
├── test_connection.py                # Test script
├── my_first_script.py                # Your scripts
├── test_model_selection.py           # Optional test
├── MODEL_SELECTION_GUIDE.md          # Optional docs
└── MODEL_SELECTION_QUICKSTART.txt    # Optional docs
```

---

## ✅ **Verification Checklist**

Before running your scripts, verify:

- [ ] SSH tunnel is running (`./start_tunnel.sh`)
- [ ] Model manager is running on server
- [ ] `vllm_client.py` is downloaded
- [ ] Python dependencies installed (`pip install openai requests`)
- [ ] Test script works (`python test_connection.py`)

---

## 🎉 **You're Ready!**

You can now:
- ✅ Connect to vLLM server from your local computer
- ✅ Choose from 10 different AI models
- ✅ Switch models during runtime
- ✅ Optimize for speed vs quality
- ✅ Use in your Python scripts

**Next Steps:**
1. Run `./start_tunnel.sh` to connect
2. Run `python test_connection.py` to verify
3. Start using in your scripts!

---

## 📚 **Additional Resources**

- **MODEL_SELECTION_QUICKSTART.txt** - Quick reference
- **MODEL_SELECTION_GUIDE.md** - Complete guide with examples
- **test_model_selection.py** - Interactive test script

Download from server:
```bash
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/MODEL_SELECTION_GUIDE.md .
```

---

## 🆘 **Need Help?**

If you encounter issues:
1. Check the troubleshooting section above
2. Verify SSH tunnel is running
3. Verify model manager is running on server
4. Check `MODEL_SELECTION_GUIDE.md` for detailed examples

