# 🖥️ vLLM Client - Local Computer Setup

This directory contains everything you need to set up your **local computer** to connect to the vLLM server and select AI models remotely.

---

## 🚀 **Quick Setup (Automated)**

### **Option 1: Automated Setup (Recommended)**

On your **local computer**, run this single command:

```bash
# Download and run setup script
curl -o setup_local.sh http://192.222.53.238/vllm/local_setup/setup_local.sh
# OR use scp:
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/local_setup/setup_local.sh .

# Run it
chmod +x setup_local.sh
./setup_local.sh
```

This will:
- ✅ Download all required files
- ✅ Install Python dependencies
- ✅ Create helper scripts
- ✅ Set up your environment

---

### **Option 2: Manual Setup**

If you prefer to set up manually:

```bash
# 1. Create directory
mkdir ~/vllm_client
cd ~/vllm_client

# 2. Download required files
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/vllm_client.py .
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/local_setup/start_tunnel.sh .
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/local_setup/test_connection.py .
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/local_setup/my_first_script.py .

# 3. Install dependencies
pip install openai requests

# 4. Make scripts executable
chmod +x start_tunnel.sh test_connection.py my_first_script.py
```

---

## 📋 **Files in This Directory**

| File | Purpose | Required? |
|------|---------|-----------|
| `setup_local.sh` | Automated setup script | ⭐ Start here |
| `start_tunnel.sh` | SSH tunnel script (Linux/Mac) | ✅ Required |
| `start_tunnel.bat` | SSH tunnel script (Windows) | ✅ Required (Windows) |
| `test_connection.py` | Test your connection | ⭐ Recommended |
| `my_first_script.py` | Example script | 📚 Example |
| `README.md` | This file | 📚 Documentation |

---

## 🎯 **Usage Workflow**

### **Every Time You Want to Use vLLM:**

**Step 1: Start Model Manager on Server**

```bash
# SSH into server
ssh ubuntu@192.222.53.238

# Start model manager
cd /lambda/nfs/newinstance/vllm
./start_model_manager.sh
```

Keep this running!

---

**Step 2: Start SSH Tunnel on Local Computer**

Open a **new terminal** on your local computer:

```bash
cd ~/vllm_client
./start_tunnel.sh  # Linux/Mac
# OR
start_tunnel.bat   # Windows
```

Keep this terminal open!

---

**Step 3: Run Your Scripts**

Open **another terminal** on your local computer:

```bash
cd ~/vllm_client

# Test connection
python test_connection.py

# Run example
python my_first_script.py

# Run your own scripts
python your_script.py
```

---

## 📝 **Example: Your First Script**

Create `my_script.py`:

```python
from vllm_client import VLLMClient

# Connect
client = VLLMClient()

# Select model
client.select_model("qwen-14b-fast")

# Use it
response = client.chat("What is machine learning?")
print(response)
```

Run it:
```bash
python my_script.py
```

---

## 📊 **Available Models**

Choose the right model for your task:

| Model ID | Speed | Best For |
|----------|-------|----------|
| `qwen-14b-fast` | 150-200 tok/s | Fast processing ⚡ |
| `qwen-72b-quality` | 50-70 tok/s | Maximum quality 💎 |
| `deepseek-v3-reasoning` | 60-80 tok/s | Complex reasoning 🧠 |
| `t3q-structured` | 120-150 tok/s | JSON output 📋 |
| `qwen-vl-7b-multimodal` | 100-120 tok/s | Images + text 🖼️ |
| `phi-4-quantized` | 200+ tok/s | Low memory 🔧 |

See `MODEL_SELECTION_GUIDE.md` for complete list.

---

## ⚠️ **Troubleshooting**

### **Problem: "Connection refused"**

**Solution:**
1. Check SSH tunnel is running: `./start_tunnel.sh`
2. Check model manager is running on server
3. Verify ports 8000 and 8001 are tunneled

---

### **Problem: "No module named 'vllm_client'"**

**Solution:**
```bash
# Make sure file exists
ls -l vllm_client.py

# If not, download it
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/vllm_client.py .
```

---

### **Problem: "No module named 'openai'"**

**Solution:**
```bash
pip install openai requests
```

---

## 📚 **Documentation**

- **LOCAL_SETUP_INSTRUCTIONS.md** - Complete setup guide
- **MODEL_SELECTION_QUICKSTART.txt** - Quick reference
- **MODEL_SELECTION_GUIDE.md** - Detailed examples

Download from server:
```bash
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/LOCAL_SETUP_INSTRUCTIONS.md .
scp ubuntu@192.222.53.238:/lambda/nfs/newinstance/vllm/MODEL_SELECTION_GUIDE.md .
```

---

## ✅ **Verification Checklist**

Before running your scripts:

- [ ] Model manager running on server (`./start_model_manager.sh`)
- [ ] SSH tunnel running on local computer (`./start_tunnel.sh`)
- [ ] `vllm_client.py` downloaded
- [ ] Python dependencies installed (`pip install openai requests`)
- [ ] Test script passes (`python test_connection.py`)

---

## 🎉 **You're Ready!**

You can now:
- ✅ Connect to vLLM server from your local computer
- ✅ Choose from 10 different AI models
- ✅ Switch models during runtime
- ✅ Process YouTube transcripts at scale

**Next Steps:**
1. Run `./setup_local.sh` (if not done)
2. Start SSH tunnel: `./start_tunnel.sh`
3. Test connection: `python test_connection.py`
4. Start coding!

---

## 🆘 **Need Help?**

See the complete documentation:
- `LOCAL_SETUP_INSTRUCTIONS.md` - Detailed setup guide
- `MODEL_SELECTION_GUIDE.md` - Usage examples
- `MODEL_SELECTION_QUICKSTART.txt` - Quick reference

