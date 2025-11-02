# Windows Setup Guide - Connect to vLLM Server

**Server IP:** `192.222.53.238`

---

## 🪟 **For Windows Users**

### **Option 1: Using PowerShell/CMD (Built-in SSH)**

Windows 10/11 has SSH built-in!

1. **Open PowerShell or Command Prompt**

2. **Create SSH Tunnel:**
```powershell
ssh -L 8000:localhost:8000 ubuntu@192.222.53.238
```

3. **Keep this window open!**

4. **Test in a NEW PowerShell window:**
```powershell
curl http://localhost:8000/v1/models
```

---

### **Option 2: Using PuTTY**

If you prefer a GUI:

1. **Download PuTTY:** https://www.putty.org/

2. **Configure PuTTY:**
   - **Host Name:** `192.222.53.238`
   - **Port:** `22`
   - **Connection Type:** SSH

3. **Set up tunnel:**
   - Go to: **Connection → SSH → Tunnels**
   - **Source port:** `8000`
   - **Destination:** `localhost:8000`
   - Click **Add**
   - Click **Open**

4. **Login** with username: `ubuntu`

5. **Keep PuTTY window open!**

6. **Access vLLM** at: `http://localhost:8000`

---

### **Option 3: Using Windows Subsystem for Linux (WSL)**

1. **Install WSL** (if not already):
```powershell
wsl --install
```

2. **Open WSL terminal**

3. **Follow Linux instructions:**
```bash
ssh -L 8000:localhost:8000 ubuntu@192.222.53.238
```

---

## 🐍 **Python Setup on Windows**

### **Install Python** (if needed):
- Download from: https://www.python.org/downloads/
- Check "Add Python to PATH" during installation

### **Install OpenAI library:**
```powershell
pip install openai
```

### **Test Connection:**

Create a file `test_vllm.py`:

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

# Test chat
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-14B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(f"\nResponse: {response.choices[0].message.content}")
```

Run it:
```powershell
python test_vllm.py
```

---

## 🔧 **Troubleshooting on Windows**

### **"ssh is not recognized"**
- Update Windows 10/11 to latest version
- Or install Git for Windows (includes SSH): https://git-scm.com/download/win
- Or use PuTTY (Option 2 above)

### **"Connection refused"**
- Make sure vLLM server is running on remote machine
- Check SSH tunnel is active (PuTTY window or PowerShell window open)

### **Firewall blocking connection**
- Windows Firewall might block localhost connections
- Allow Python through firewall when prompted

### **Port already in use**
- Another program is using port 8000
- Use different port: `ssh -L 8001:localhost:8000 ubuntu@192.222.53.238`
- Then use `http://localhost:8001` instead

---

## 📝 **Quick Reference**

### **Create SSH Tunnel (PowerShell):**
```powershell
ssh -L 8000:localhost:8000 ubuntu@192.222.53.238
```

### **Test Connection (PowerShell):**
```powershell
curl http://localhost:8000/v1/models
```

### **Python Client:**
```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
```

---

## 🎯 **Complete Windows Workflow**

1. **Open PowerShell #1** → Create SSH tunnel (keep open)
2. **Open PowerShell #2** → Run your Python scripts
3. **Access vLLM** at `http://localhost:8000`

---

## 💡 **Pro Tips for Windows**

- **Windows Terminal** is great for managing multiple terminals
- **VS Code** has built-in terminal and SSH support
- **Save SSH config** to avoid typing IP every time:

Create/edit `C:\Users\YourName\.ssh\config`:
```
Host vllm-server
    HostName 192.222.53.238
    User ubuntu
    LocalForward 8000 localhost:8000
```

Then just run: `ssh vllm-server`

---

## 🚀 **You're Ready!**

Your Windows machine can now access the H100 GPU server! 🎉

