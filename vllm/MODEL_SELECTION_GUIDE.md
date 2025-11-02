# 🎯 Model Selection from Your Local Computer

This guide shows you how to **choose which AI model to use** from your local computer when connecting to the vLLM server.

---

## 🚀 **Quick Start**

### **Step 1: Start Model Manager on Server**

On the **server** (192.222.53.238), run:

```bash
cd /lambda/nfs/newinstance/vllm
python model_manager.py
```

This starts:
- **Model Manager API** on port 8001 (for switching models)
- **vLLM API** on port 8000 (for inference)

---

### **Step 2: Create SSH Tunnels on Your Local Computer**

On your **local computer**, create TWO SSH tunnels:

```bash
# Tunnel for vLLM inference (port 8000)
ssh -L 8000:localhost:8000 ubuntu@192.222.53.238 &

# Tunnel for Model Manager (port 8001)
ssh -L 8001:localhost:8001 ubuntu@192.222.53.238 &
```

Or in a single command:
```bash
ssh -L 8000:localhost:8000 -L 8001:localhost:8001 ubuntu@192.222.53.238
```

---

### **Step 3: Use from Your Python Script**

Download the client library to your local computer:

```bash
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/vllm_client.py .
```

Then use it in your script:

```python
from vllm_client import VLLMClient

# Create client
client = VLLMClient(
    vllm_url="http://localhost:8000",
    manager_url="http://localhost:8001"
)

# List available models
client.print_available_models()

# Select the model you want
client.select_model("qwen-14b-fast")  # Fast model
# OR
client.select_model("qwen-72b-quality")  # Best quality
# OR
client.select_model("deepseek-v3-reasoning")  # Best reasoning

# Use the model
response = client.chat("What is machine learning?")
print(response)
```

---

## 📋 **Available Models**

You can choose from **10 different models**:

| Model ID | Description | Speed | VRAM | Best For |
|----------|-------------|-------|------|----------|
| `qwen-14b-fast` | Fast model | 150-200 tok/s | 28GB | High throughput |
| `qwen-72b-quality` | Maximum quality | 50-70 tok/s | 50GB | Complex analysis |
| `deepseek-v3-reasoning` | Best reasoning | 60-80 tok/s | 45GB | Trend analysis |
| `qwen-vl-7b-multimodal` | Multimodal | 100-120 tok/s | 12GB | Images + text |
| `qwen-vl-72b-multimodal` | Best multimodal | 40-60 tok/s | 70GB | Best quality vision |
| `mistral-large-chat` | Top chat | 40-60 tok/s | 70GB | Conversations |
| `phi-4-quantized` | Quantized | 200+ tok/s | 4GB | Low memory |
| `t3q-structured` | Structured output | 120-150 tok/s | 28GB | JSON output |
| `calme-analysis` | Complex analysis | 45-65 tok/s | 60GB | Deep analysis |
| `rombos-merge` | Model merge | 50-70 tok/s | 50GB | Combined strengths |

---

## 💡 **Usage Examples**

### **Example 1: Basic Chat**

```python
from vllm_client import VLLMClient

client = VLLMClient()

# Select fast model
client.select_model("qwen-14b-fast")

# Chat
response = client.chat("Explain quantum computing in simple terms")
print(response)
```

---

### **Example 2: YouTube Claim Extraction**

```python
from vllm_client import VLLMClient

client = VLLMClient()

# Select model optimized for structured output
client.select_model("t3q-structured")

# Extract claims from transcript
transcript = """
In this video, I'll show you how Python became the most popular 
programming language in 2024. Python was created by Guido van Rossum 
in 1991. Today, over 8 million developers use Python worldwide.
"""

claims = client.extract_claims(transcript)
print(claims)
```

---

### **Example 3: Switch Models During Runtime**

```python
from vllm_client import VLLMClient

client = VLLMClient()

# Start with fast model for quick processing
client.select_model("qwen-14b-fast")
response1 = client.chat("Quick question: What is AI?")

# Switch to quality model for complex analysis
client.select_model("qwen-72b-quality")
response2 = client.chat("Provide a detailed analysis of AI ethics")

# Switch to reasoning model for trend analysis
client.select_model("deepseek-v3-reasoning")
response3 = client.chat("Analyze trends in AI development")
```

---

### **Example 4: Multimodal Analysis (Images + Text)**

```python
from vllm_client import VLLMClient

client = VLLMClient()

# Select multimodal model
client.select_model("qwen-vl-7b-multimodal")

# Now you can analyze images + text together
# (Note: Image support requires additional setup)
```

---

### **Example 5: Interactive Model Selection**

```python
from vllm_client import VLLMClient

client = VLLMClient()

# Show available models
client.print_available_models()

# Let user choose
model_id = input("Enter model ID: ")
client.select_model(model_id)

# Use selected model
while True:
    question = input("\nYou: ")
    if question.lower() in ['quit', 'exit']:
        break
    
    response = client.chat(question, stream=True)
```

---

## 🔧 **Advanced Usage**

### **Check Current Model**

```python
current = client.get_current_model()
if current:
    print(f"Current model: {current['model_id']}")
    print(f"Description: {current['model_info']['description']}")
else:
    print("No model loaded")
```

---

### **Custom System Prompt**

```python
response = client.chat(
    message="What is the capital of France?",
    system_prompt="You are a geography expert. Be concise.",
    max_tokens=100,
    temperature=0.7
)
```

---

### **Streaming Responses**

```python
# Stream the response (prints as it generates)
response = client.chat(
    message="Tell me a story",
    stream=True
)
```

---

## 🔌 **API Endpoints (Direct Access)**

If you prefer to use the API directly without the Python client:

### **List Available Models**
```bash
curl http://localhost:8001/models/available
```

### **Get Current Model**
```bash
curl http://localhost:8001/models/current
```

### **Load a Model**
```bash
curl -X POST http://localhost:8001/models/load \
  -H "Content-Type: application/json" \
  -d '{"model_id": "qwen-14b-fast"}'
```

### **Check Status**
```bash
curl http://localhost:8001/status
```

---

## 📝 **Integration with Your Existing Scripts**

### **Minimal Changes Required**

If you have existing code using OpenAI client, just add model selection:

**Before:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

response = client.chat.completions.create(...)
```

**After:**
```python
from vllm_client import VLLMClient

# Add model selection capability
client = VLLMClient()
client.select_model("qwen-14b-fast")  # Choose your model

# Use the same way
response = client.chat("Your question here")
```

---

## 🚦 **Model Selection Strategy**

### **For YouTube Analysis:**

1. **Fast Processing (1000s of videos):**
   - Use: `qwen-14b-fast` or `phi-4-quantized`
   - Speed: 150-200+ tokens/sec

2. **High Quality Extraction:**
   - Use: `qwen-72b-quality` or `t3q-structured`
   - Better accuracy, slower

3. **Trend Analysis:**
   - Use: `deepseek-v3-reasoning`
   - Best for complex reasoning

4. **Thumbnail + Transcript:**
   - Use: `qwen-vl-7b-multimodal`
   - Analyze images + text together

### **Recommended Workflow:**

```python
from vllm_client import VLLMClient

client = VLLMClient()

# Phase 1: Fast extraction (use fast model)
client.select_model("qwen-14b-fast")
for video in videos[:1000]:
    claims = client.extract_claims(video.transcript)
    save_claims(claims)

# Phase 2: Deep analysis (switch to reasoning model)
client.select_model("deepseek-v3-reasoning")
trends = client.chat("Analyze trends in these claims: ...")
```

---

## ⚠️ **Important Notes**

1. **Model Loading Time:**
   - Small models (14B): ~1-2 minutes
   - Large models (72B+): ~2-3 minutes
   - The client waits automatically

2. **Memory Usage:**
   - Only ONE model runs at a time
   - Switching models stops the current one
   - Your H100 80GB can handle any single model

3. **SSH Tunnels:**
   - Keep both tunnels open (ports 8000 and 8001)
   - If tunnel drops, just reconnect

4. **Model Manager:**
   - Must be running on server
   - Manages vLLM process automatically
   - Handles graceful shutdown

---

## 🐛 **Troubleshooting**

### **"Connection refused" on port 8001**
- Check model manager is running on server
- Check SSH tunnel for port 8001 is active

### **Model loading fails**
- Check server has enough VRAM (nvidia-smi)
- Wait for previous model to fully unload
- Check server logs: `tail -f model_manager.log`

### **Slow model switching**
- Normal! Large models take 2-3 minutes to load
- The client waits automatically
- You can check status: `client.get_current_model()`

---

## 📦 **Files You Need**

Download these to your local computer:

```bash
# Client library (required)
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/vllm_client.py .

# This guide (optional)
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/MODEL_SELECTION_GUIDE.md .
```

---

## 🎉 **You're Ready!**

You can now:
- ✅ Choose from 10 different AI models
- ✅ Switch models from your local computer
- ✅ Optimize for speed vs quality
- ✅ Use multimodal models for images + text
- ✅ Integrate easily with existing scripts

**Happy analyzing!** 🚀

