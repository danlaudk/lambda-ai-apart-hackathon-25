# Quick Start Guide - vLLM Setup

## Step 1: Start the vLLM Server

Open a terminal and run:

```bash
cd /lambda/nfs/newinstance/vllm
./start_vllm_server.sh
```

**What happens:**
- Downloads the DeepSeek model (first time only, ~3GB)
- Loads model into GPU/CPU memory
- Starts server on http://localhost:8000
- Keep this terminal open!

**Expected output:**
```
Starting vLLM server with model: MasterControlAIML/DeepSeek-R1-Qwen2.5-1.5b-SFT-R1-JSON-Unstructured-To-Structured
Server will be available at http://0.0.0.0:8000

INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
```

## Step 2: Test the Server (Optional)

Open a **new terminal** and run:

```bash
cd /lambda/nfs/newinstance/vllm
python test_vllm_client.py
```

**Expected output:**
```
Testing vLLM server...
✅ vLLM server is working correctly!
```

## Step 3: Run Your Analysis

In the **same new terminal**, run:

```bash
cd /lambda/nfs/newinstance/vllm
python LLM_vllm.py
```

This will:
1. Load your YouTube transcripts CSV
2. Extract claims from each transcript (using vLLM)
3. Cluster similar claims
4. Generate a word cloud

## Comparison: Old vs New

### Old Way (LLM.py)
```python
# Loads model EVERY time you run the script
model = AutoModelForCausalLM.from_pretrained(...)  # Slow!
tokenizer = AutoTokenizer.from_pretrained(...)
nlp_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
```

**Problems:**
- Takes 30-60 seconds to load model each time
- Uses lots of memory in your Python script
- Slow inference
- Can't process multiple requests in parallel

### New Way (LLM_vllm.py)
```python
# Just makes HTTP requests to vLLM server
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
response = client.completions.create(...)  # Fast!
```

**Benefits:**
- Model loads once, stays in memory
- 10-20x faster inference
- Simple HTTP requests
- Can process multiple transcripts in parallel
- Better memory management

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Check GPU availability: `nvidia-smi`
- Check logs for errors

### Client can't connect
- Make sure server is running (Step 1)
- Check server URL: `curl http://localhost:8000/health`
- Verify firewall settings

### Out of memory
- Reduce `--max-model-len` in `start_vllm_server.sh`
- Use smaller batch sizes
- Close other applications

## Next Steps

1. **Optimize performance**: Adjust `--max-model-len`, `--dtype` in server script
2. **Process in parallel**: Modify `LLM_vllm.py` to use async requests
3. **Monitor**: Add logging and metrics
4. **Scale**: Run multiple vLLM servers for different models

## Files Created

```
/lambda/nfs/newinstance/vllm/
├── start_vllm_server.sh    # Server startup script
├── test_vllm_client.py     # Test client
├── LLM_vllm.py             # Updated analysis script
├── requirements.txt        # Python dependencies
├── README.md               # Full documentation
└── QUICKSTART.md          # This file
```
