# 🚀 Connect to Your vLLM Server from Your Local Computer

**Server IP:** 192.222.53.238
**Ports:** 8000 (vLLM), 8001 (Model Manager)

---

## 🎯 **NEW FEATURE: Model Selection!**

You can now **choose which AI model to use** from your local computer!

- ✅ **10 different models** available
- ✅ **Switch models** during runtime
- ✅ **Optimize** for speed vs quality
- ✅ **Easy Python API**

**See:** `MODEL_SELECTION_GUIDE.md` for complete instructions

---

## ✅ **Two Ways to Connect:**

### **Option 1: Model Selection (RECOMMENDED - NEW!)**
Choose which model to use from your local computer. See `MODEL_SELECTION_QUICKSTART.txt`

### **Option 2: Single Model (Simple)**
Use one pre-loaded model. Continue reading below.

---

## 🔐 **Step 1: Create SSH Tunnel (On Your Local Computer)**

Open a terminal on your **local computer** and run:

```bash
ssh -L 8000:localhost:8000 ubuntu@192.222.53.238
```

**Important:** Keep this terminal window open while using vLLM!

---

## 🧪 **Step 2: Test Connection (On Your Local Computer)**

Open a **NEW terminal** on your local computer and test:

```bash
curl http://localhost:8000/v1/models
```

You should see:
```json
{
  "data": [
    {
      "id": "Qwen/Qwen2.5-14B-Instruct",
      "max_model_len": 32768
    }
  ]
}
```

---

## 🐍 **Step 3: Use from Python (On Your Local Computer)**

### **Install OpenAI library:**
```bash
pip install openai
```

### **Python Example:**

```python
from openai import OpenAI

# Connect to your vLLM server through SSH tunnel
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # vLLM doesn't require real API key
)

# Test chat completion
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-14B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ],
    max_tokens=200
)

print(response.choices[0].message.content)
```

---

## 📊 **YouTube Claim Extraction Example**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

# Sample YouTube transcript
transcript = """
In this video, I'll show you how Python became the most popular 
programming language in 2024. Python was created by Guido van Rossum 
in 1991. Today, over 8 million developers use Python worldwide.
"""

# Extract claims
prompt = f"""Extract factual claims from this YouTube transcript.
Return ONLY a JSON array of claims.

Transcript: {transcript}

Format: {{"claims": ["claim 1", "claim 2", ...]}}
"""

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-14B-Instruct",
    messages=[
        {"role": "system", "content": "You are a factual claim extraction system."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=500,
    temperature=0.0  # Low temperature for consistent extraction
)

print(response.choices[0].message.content)
```

---

## 🎯 **Available Models on Server**

You have **10 models** downloaded and ready to use:

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| **Qwen2.5-14B-Instruct** ⚡ | 30GB | 150-200 tok/s | **CURRENTLY RUNNING** - Fast processing |
| Qwen2.5-72B-Instruct 💎 | 145GB | 50-70 tok/s | Maximum quality |
| DeepSeek-V3 🧠 | 689GB | 60-80 tok/s | Complex reasoning |
| Qwen2-VL-7B-Instruct 🖼️ | 17GB | 100-120 tok/s | Images + text |
| Qwen2-VL-72B-Instruct 🖼️💎 | 147GB | 40-60 tok/s | Best multimodal |
| Mistral-Large-Instruct 💬 | 490GB | 40-60 tok/s | Top chat model |
| phi-4-unsloth-bnb-4bit 🔧 | 10GB | 200+ tok/s | Quantized, low VRAM |
| T3Q-qwen2.5-14b 📋 | 30GB | 120-150 tok/s | Structured JSON output |
| calme-3.2-instruct-78b 🎓 | 312GB | 45-65 tok/s | Complex analysis |
| Rombos-LLM-V2.5-Qwen-72b 🔀 | 145GB | 50-70 tok/s | Model merge |

---

## 🔄 **Switch to a Different Model**

### **On the server:**

1. **Stop current server:** Press `Ctrl+C` in the server terminal

2. **Start with different model:**

```bash
# Fast model (currently running)
./start_fast.sh

# Maximum quality
./start_quality.sh

# Best reasoning
./start_reasoning.sh

# Multimodal (images + text)
./start_multimodal.sh

# Interactive selector
./select_model.sh
```

3. **Your SSH tunnel stays connected** - no changes needed on local computer!

---

## 📁 **Download Example Scripts**

Copy the example script to your local computer:

```bash
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/local_client_example.py .
```

Then run it:
```bash
python local_client_example.py
```

This includes:
- ✅ Connection test
- ✅ Chat completion example
- ✅ Streaming example
- ✅ YouTube claim extraction example
- ✅ Interactive chat mode

---

## 🔧 **Troubleshooting**

### **"Connection refused"**
- Check vLLM server is running on remote machine
- Check SSH tunnel is active (terminal window open)

### **"Port already in use"**
Another program is using port 8000 on your local computer.

**Solution:** Use different port:
```bash
ssh -L 8001:localhost:8000 ubuntu@192.222.53.238
```

Then use `http://localhost:8001` instead of `http://localhost:8000`

### **Slow responses**
- Current model (14B) should be fast (150-200 tok/s)
- If slow, check GPU usage on server: `nvidia-smi`
- Try the quantized model for maximum speed: `./select_model.sh` → option 6

### **Out of memory errors**
- Current model uses ~28GB VRAM (plenty of room on H100)
- If switching to larger models (72B+), they use 50-70GB VRAM
- All models fit comfortably on your H100 80GB GPU

---

## 💡 **Pro Tips**

### **1. Keep SSH tunnel alive**
Add to your local `~/.ssh/config`:
```
Host vllm-server
    HostName 192.222.53.238
    User ubuntu
    LocalForward 8000 localhost:8000
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Then just run: `ssh vllm-server`

### **2. Run in background**
On server, use `screen` or `tmux`:
```bash
screen -S vllm
./start_fast.sh
# Press Ctrl+A then D to detach
```

Reattach later:
```bash
screen -r vllm
```

### **3. Monitor performance**
```bash
# GPU usage
watch -n 1 nvidia-smi

# Server logs
tail -f vllm_server.log
```

---

## 🎉 **You're All Set!**

Your H100 GPU server is ready to process YouTube videos at scale!

**Current Setup:**
- ✅ vLLM server running with Qwen2.5-14B-Instruct
- ✅ 10 top-tier models downloaded (2TB)
- ✅ Secure SSH tunnel access
- ✅ OpenAI-compatible API
- ✅ Ready for production use

**Next Steps:**
1. Create SSH tunnel from your local computer
2. Test with `curl http://localhost:8000/v1/models`
3. Run Python examples
4. Process your YouTube transcripts!

---

**Questions?** Check the other guides:
- `QUICK_START.txt` - Quick reference
- `REMOTE_ACCESS_GUIDE.md` - Complete setup guide
- `WINDOWS_SETUP.md` - Windows-specific instructions
- `local_client_example.py` - Ready-to-run examples

