# vLLM Public API Setup Guide

**Direct API Access - No SSH Tunnel Required!**

This guide shows you how to connect to the vLLM server directly over the internet using API key authentication.

---

## 🔑 **Your API Key**

Your API key is stored on the server at:
```
/lambda/nfs/newinstance/vllm/.api_key
```

To view your API key on the server:
```bash
cat /lambda/nfs/newinstance/vllm/.api_key
```

**Current API Key:**
```
zHHr8CUd-ZASiZjsSXC4fuE1ifF65YyEZ8Je7g5sffU
```

⚠️ **IMPORTANT:** Keep this API key secret! Anyone with this key can use your server.

---

## 📋 **Server Information**

| Setting | Value |
|---------|-------|
| **Server IP** | `192.222.53.238` |
| **Model Manager Port** | `8001` |
| **vLLM Inference Port** | `8000` |
| **API Key** | See above |

---

## 🚀 **Phase 1: Server Setup (COMPLETE)**

✅ Model Manager deployed with API key authentication  
✅ Listening on public IP (0.0.0.0)  
✅ 10 AI models available  
✅ Running in background  

---

## 💻 **Phase 2: Local Computer Setup**

### **Step 1: Download Client Library**

On your **local computer**:

```bash
# Create directory
mkdir ~/vllm_client
cd ~/vllm_client

# Download client library
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/vllm_client.py .

# Download this guide
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/PUBLIC_API_SETUP.md .
```

---

### **Step 2: Install Dependencies**

```bash
pip install openai requests
```

---

### **Step 3: Create Configuration File**

Create `config.py` on your local computer:

```python
# config.py
SERVER_IP = "192.222.53.238"
API_KEY = "zHHr8CUd-ZASiZjsSXC4fuE1ifF65YyEZ8Je7g5sffU"
```

⚠️ **Security:** Add `config.py` to `.gitignore` if using version control!

---

### **Step 4: Test Connection**

Create `test_connection.py`:

```python
#!/usr/bin/env python3
from vllm_client import VLLMClient
from config import SERVER_IP, API_KEY

# Connect to server
client = VLLMClient(
    server_ip=SERVER_IP,
    manager_api_key=API_KEY
)

# Test connection
print("Testing connection...")
models = client.list_available_models()
print(f"✅ Connected! Found {models['count']} models")

# List models
client.print_available_models()
```

Run it:
```bash
python test_connection.py
```

---

### **Step 5: Use in Your Scripts**

Create `my_script.py`:

```python
#!/usr/bin/env python3
from vllm_client import VLLMClient
from config import SERVER_IP, API_KEY

# Connect
client = VLLMClient(
    server_ip=SERVER_IP,
    manager_api_key=API_KEY
)

# Select model
client.select_model("qwen-14b-fast")

# Use it
response = client.chat("What is machine learning?")
print(response)

# Extract claims from YouTube transcript
transcript = """
Your YouTube video transcript here...
"""
claims = client.extract_claims(transcript)
print(claims)
```

---

## 🎨 **Phase 3: Chat GUI (Optional)**

### **Simple Gradio GUI**

Install Gradio:
```bash
pip install gradio
```

Create `chat_gui.py`:

```python
#!/usr/bin/env python3
import gradio as gr
from vllm_client import VLLMClient
from config import SERVER_IP, API_KEY

# Initialize client
client = VLLMClient(
    server_ip=SERVER_IP,
    manager_api_key=API_KEY
)

# Load default model
client.select_model("qwen-14b-fast")

def chat(message, history):
    """Chat function for Gradio"""
    response = client.chat(message)
    return response

def select_model_ui(model_id):
    """Model selection for UI"""
    success = client.select_model(model_id)
    if success:
        return f"✅ Loaded: {model_id}"
    return f"❌ Failed to load: {model_id}"

# Create UI
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 vLLM Chat Interface")
    
    with gr.Row():
        model_dropdown = gr.Dropdown(
            choices=[
                "qwen-14b-fast",
                "qwen-72b-quality",
                "deepseek-v3-reasoning",
                "qwen-vl-7b-multimodal",
                "mistral-large-chat",
                "phi-4-quantized",
                "t3q-structured"
            ],
            value="qwen-14b-fast",
            label="Select Model"
        )
        model_status = gr.Textbox(label="Status", value="✅ qwen-14b-fast loaded")
    
    model_dropdown.change(select_model_ui, inputs=[model_dropdown], outputs=[model_status])
    
    chatbot = gr.ChatInterface(chat)

# Launch
demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
```

Run it:
```bash
python chat_gui.py
```

Then open: `http://localhost:7860`

---

## 📊 **Available Models**

| Model ID | Speed | VRAM | Best For |
|----------|-------|------|----------|
| `qwen-14b-fast` | 150-200 tok/s | 28GB | Fast processing ⚡ |
| `qwen-72b-quality` | 50-70 tok/s | 50GB | Maximum quality 💎 |
| `deepseek-v3-reasoning` | 60-80 tok/s | 45GB | Complex reasoning 🧠 |
| `qwen-vl-7b-multimodal` | 100-120 tok/s | 12GB | Images + text 🖼️ |
| `qwen-vl-72b-multimodal` | 40-60 tok/s | 70GB | Best multimodal 🖼️💎 |
| `mistral-large-chat` | 40-60 tok/s | 70GB | Conversations 💬 |
| `phi-4-quantized` | 200+ tok/s | 4GB | Low memory 🔧 |
| `t3q-structured` | 120-150 tok/s | 28GB | JSON output 📋 |
| `calme-analysis` | 45-65 tok/s | 60GB | Deep analysis 🎓 |
| `rombos-merge` | 50-70 tok/s | 50GB | Combined strengths 🔀 |

---

## 🔒 **Security Notes**

1. **API Key Protection:**
   - Never commit API key to version control
   - Use environment variables or config files
   - Rotate key if compromised

2. **Firewall:**
   - Ensure ports 8000 and 8001 are open on server
   - Consider IP whitelisting for production

3. **HTTPS:**
   - For production, use HTTPS with reverse proxy (nginx/caddy)
   - Current setup uses HTTP (fine for testing)

---

## ⚠️ **Troubleshooting**

### **Problem: Connection refused**
**Solution:**
```bash
# Check if model manager is running on server
ssh ubuntu@192.222.53.238
ps aux | grep model_manager

# If not running, start it
cd /lambda/nfs/newinstance/vllm
python model_manager.py
```

### **Problem: Invalid API key**
**Solution:**
```bash
# Get current API key from server
ssh ubuntu@192.222.53.238
cat /lambda/nfs/newinstance/vllm/.api_key

# Update your config.py with correct key
```

### **Problem: Firewall blocking connection**
**Solution:**
```bash
# On server, check if ports are open
sudo ufw status
sudo ufw allow 8000
sudo ufw allow 8001
```

---

## ✅ **Summary**

**What you have:**
- ✅ Direct API access (no SSH tunnel needed)
- ✅ Secure API key authentication
- ✅ 10 AI models to choose from
- ✅ Simple Python client library
- ✅ Optional chat GUI

**How to use:**
1. Download `vllm_client.py` to local computer
2. Create `config.py` with server IP and API key
3. Install dependencies: `pip install openai requests`
4. Use in your scripts!

**No SSH tunnel required!** Just connect directly to `192.222.53.238:8001`

---

## 📚 **Next Steps**

1. **Test the connection** with `test_connection.py`
2. **Try the chat GUI** with `chat_gui.py`
3. **Integrate into your YouTube analysis** scripts
4. **Experiment with different models** for different tasks

Enjoy your high-performance AI server! 🚀

