# Remote Access Guide - Connect to vLLM Server from Your Local Computer

**Server Public IP:** `192.222.53.238`  
**Server Private IP:** `172.27.124.252`  
**vLLM Default Port:** `8000`

---

## 🔐 **Security Notice**

Your server is accessible from the internet at `192.222.53.238`. We'll set up secure access methods.

---

## **Option 1: SSH Tunnel (RECOMMENDED - Most Secure)** 🔒

This creates an encrypted tunnel from your local computer to the server.

### **On Your Local Computer:**

```bash
# Create SSH tunnel (keeps running in terminal)
ssh -L 8000:localhost:8000 ubuntu@192.222.53.238

# Or run in background
ssh -f -N -L 8000:localhost:8000 ubuntu@192.222.53.238
```

### **Then access vLLM locally:**

```python
from openai import OpenAI

# Connect through SSH tunnel (localhost)
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-14B-Instruct",  # or any model you have
    messages=[
        {"role": "user", "content": "Hello! How are you?"}
    ],
    max_tokens=100
)

print(response.choices[0].message.content)
```

**Advantages:**
- ✅ Fully encrypted
- ✅ No firewall changes needed
- ✅ Works from anywhere
- ✅ No exposed ports

---

## **Option 2: Direct Access with API Key Authentication** 🔑

Expose vLLM directly but with API key protection.

### **Server Setup:**

1. **Update vLLM startup script with API key:**

```bash
# Edit start_vllm_server.sh
nano start_vllm_server.sh
```

Add `--api-key` parameter:
```bash
python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --host 0.0.0.0 \
    --port 8000 \
    --api-key "your-secret-api-key-here" \
    --max-model-len 4096 \
    --dtype auto \
    --trust-remote-code
```

2. **Open firewall port:**

```bash
sudo ufw allow 8000/tcp
sudo ufw enable
```

### **From Your Local Computer:**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://192.222.53.238:8000/v1",
    api_key="your-secret-api-key-here"  # Must match server
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-14B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

## **Option 3: Nginx Reverse Proxy (Production)** 🌐

Full production setup with authentication and rate limiting.

---

## **Quick Start - SSH Tunnel (RECOMMENDED)** 🚀

### **Step 1: On Server - Start vLLM**

```bash
cd /lambda/nfs/newinstance/vllm
./start_vllm_server.sh
```

### **Step 2: On Your Local Computer - Create SSH Tunnel**

```bash
ssh -L 8000:localhost:8000 ubuntu@192.222.53.238
```

Keep this terminal open!

### **Step 3: On Your Local Computer - Test Connection**

Open a NEW terminal and run:

```bash
curl http://localhost:8000/v1/models
```

### **Step 4: Use from Python**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

# List models
models = client.models.list()
print("Available models:")
for model in models.data:
    print(f"  - {model.id}")

# Chat completion
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-14B-Instruct",
    messages=[
        {"role": "user", "content": "What is 2+2?"}
    ]
)

print(response.choices[0].message.content)
```

---

## **Testing Your Connection**

### **Simple curl test:**

```bash
# List models
curl http://localhost:8000/v1/models

# Test completion
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-14B-Instruct",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

---

## **Troubleshooting**

### **Connection refused:**
- Check vLLM is running: `ps aux | grep vllm`
- Check SSH tunnel is active
- Verify port 8000 is correct

### **SSH tunnel issues:**
- Make sure you can SSH to server: `ssh ubuntu@192.222.53.238`
- Check if port 8000 is already in use locally: `lsof -i :8000`
- Try a different local port: `ssh -L 8001:localhost:8000 ubuntu@192.222.53.238`

### **Model not found:**
- List available models first
- Use exact model name from the list
- Wait for model downloads to complete

---

## **Security Best Practices** 🔐

1. ✅ **Use SSH tunnel** for remote access (encrypted)
2. ✅ **Don't expose port 8000** directly to internet
3. ✅ **Use API keys** if you must expose directly
4. ✅ **Monitor access logs**
5. ✅ **Keep SSH keys secure**

---

## **Your Server Details**

- **Public IP:** 192.222.53.238
- **SSH Access:** `ssh ubuntu@192.222.53.238`
- **vLLM Port:** 8000
- **Firewall:** Currently inactive (ufw)

---

## **Next Steps**

1. ✅ Start vLLM server with a model
2. ✅ Create SSH tunnel from your local computer
3. ✅ Test connection with curl
4. ✅ Use from Python/your application

**Need production setup?** See full guide for Nginx reverse proxy with SSL.

