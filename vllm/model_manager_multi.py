#!/usr/bin/env python3
"""
vLLM Multi-Model Manager API
=============================

This service allows multiple AI models to run simultaneously on different ports.
Each model runs on its own vLLM server instance, starting from port 8002.

Usage:
    python model_manager_multi.py

API Endpoints:
    GET  /models/available  - List all available models
    GET  /models/loaded    - Get all currently loaded models
    GET  /models/<model_id>/status - Get status of specific model
    POST /models/<model_id>/load   - Load a specific model
    POST /models/<model_id>/unload - Unload a specific model
    GET  /status            - Get server status

Authentication:
    All requests require API key in header: X-API-Key
"""

import os
import sys
import json
import time
import signal
import subprocess
import secrets
from pathlib import Path
from typing import Optional, Dict, List
from flask import Flask, request, jsonify
from threading import Thread, Lock
from functools import wraps
import requests

app = Flask(__name__)

# Configuration
VENV_PYTHON = "/lambda/nfs/newinstance/ai_assessment_dora/venv/bin/python"
VLLM_HOST = "0.0.0.0"
BASE_PORT = 8002  # Start from port 8002 for multi-model serving
MANAGER_HOST = "0.0.0.0"  # Listen on all interfaces for public access
MANAGER_PORT = 8001  # Model manager runs on port 8001

# API Key Configuration
API_KEY_FILE = "/lambda/nfs/newinstance/vllm/.api_key"

# Available models configuration
AVAILABLE_MODELS = {
    "qwen-14b-fast": {
        "name": "Qwen/Qwen2.5-14B-Instruct",
        "description": "Fast model - 150-200 tokens/sec",
        "vram": "28GB",
        "speed": "150-200 tok/s",
        "max_model_len": 32768,
        "best_for": "High throughput, fast responses"
    },
    "qwen-72b-quality": {
        "name": "Qwen/Qwen2.5-72B-Instruct",
        "description": "Maximum quality - 50-70 tokens/sec",
        "vram": "50GB",
        "speed": "50-70 tok/s",
        "max_model_len": 32768,
        "best_for": "Maximum quality, complex analysis"
    },
    "deepseek-v3-reasoning": {
        "name": "deepseek-ai/DeepSeek-V3",
        "description": "Best reasoning - 60-80 tokens/sec",
        "vram": "45GB",
        "speed": "60-80 tok/s",
        "max_model_len": 32768,
        "best_for": "Complex reasoning, trend analysis"
    },
    "qwen-vl-7b-multimodal": {
        "name": "Qwen/Qwen2-VL-7B-Instruct",
        "description": "Multimodal - 100-120 tokens/sec",
        "vram": "12GB",
        "speed": "100-120 tok/s",
        "max_model_len": 32768,
        "best_for": "Images + text analysis"
    },
    "qwen-vl-72b-multimodal": {
        "name": "Qwen/Qwen2-VL-72B-Instruct",
        "description": "Best multimodal - 40-60 tokens/sec",
        "vram": "70GB",
        "speed": "40-60 tok/s",
        "max_model_len": 32768,
        "best_for": "Best quality images + text"
    },
    "mistral-large-chat": {
        "name": "mistralai/Mistral-Large-Instruct-2411",
        "description": "Top chat model - 40-60 tokens/sec",
        "vram": "70GB",
        "speed": "40-60 tok/s",
        "max_model_len": 32768,
        "best_for": "Conversations, instruction following"
    },
    "phi-4-quantized": {
        "name": "unsloth/phi-4-unsloth-bnb-4bit",
        "description": "Quantized - 200+ tokens/sec",
        "vram": "4GB",
        "speed": "200+ tok/s",
        "max_model_len": 16384,
        "best_for": "Parallel processing, low memory"
    },
    "t3q-structured": {
        "name": "JungZoona/T3Q-qwen2.5-14b-v1.0-e3",
        "description": "Fine-tuned for structured output",
        "vram": "28GB",
        "speed": "120-150 tok/s",
        "max_model_len": 32768,
        "best_for": "Structured JSON output"
    },
    "calme-analysis": {
        "name": "MaziyarPanahi/calme-3.2-instruct-78b",
        "description": "Fine-tuned for complex analysis",
        "vram": "60GB",
        "speed": "45-65 tok/s",
        "max_model_len": 32768,
        "best_for": "Complex analysis tasks"
    },
    "rombos-merge": {
        "name": "rombodawg/Rombos-LLM-V2.5-Qwen-72b",
        "description": "Model merge - 50-70 tokens/sec",
        "vram": "50GB",
        "speed": "50-70 tok/s",
        "max_model_len": 32768,
        "best_for": "Combined strengths"
    }
}

# Global state: Track loaded models
# Format: {model_id: {"process": Popen, "port": int, "status": str}}
loaded_models: Dict[str, Dict] = {}
model_lock = Lock()
port_counter = BASE_PORT


def get_next_port() -> int:
    """Get next available port"""
    global port_counter
    port = port_counter
    port_counter += 1
    return port


def is_port_available(port: int) -> bool:
    """Check if port is available"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=1)
        return False  # Port is in use
    except:
        return True  # Port appears available


def start_vllm_server(model_id: str, port: int) -> subprocess.Popen:
    """Start vLLM server with specified model on specific port"""
    model_config = AVAILABLE_MODELS[model_id]
    model_name = model_config["name"]
    max_model_len = model_config["max_model_len"]
    
    cmd = [
        VENV_PYTHON, "-m", "vllm.entrypoints.openai.api_server",
        "--model", model_name,
        "--host", VLLM_HOST,
        "--port", str(port),
        "--max-model-len", str(max_model_len),
        "--dtype", "auto",
        "--trust-remote-code",
        "--gpu-memory-utilization", "0.95"
    ]
    
    print(f"Starting vLLM server for model '{model_id}' ({model_name}) on port {port}")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return process


def stop_vllm_server(process: subprocess.Popen):
    """Stop vLLM server gracefully"""
    if process and process.poll() is None:
        print("Stopping vLLM server...")
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print("Force killing vLLM server...")
            process.kill()
            process.wait()


def load_or_generate_api_key() -> str:
    """Load API key from file or generate new one"""
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as f:
            return f.read().strip()
    else:
        # Generate new API key
        api_key = secrets.token_urlsafe(32)
        with open(API_KEY_FILE, 'w') as f:
            f.write(api_key)
        os.chmod(API_KEY_FILE, 0o600)  # Secure permissions
        print(f"Generated new API key: {api_key}")
        print(f"API key saved to: {API_KEY_FILE}")
        return api_key


# Load API key at startup
API_KEY = load_or_generate_api_key()


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if not provided_key:
            return jsonify({"error": "Missing API key. Provide X-API-Key header."}), 401
        if provided_key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 403
        return f(*args, **kwargs)
    return decorated_function


def wait_for_server_ready(port: int, timeout: int = 300) -> bool:
    """Wait for vLLM server to be ready on specified port"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                print(f"vLLM server on port {port} is ready!")
                return True
        except:
            pass
        time.sleep(2)

    return False


def load_model_async(model_id: str, port: int):
    """Load model asynchronously in background thread"""
    global loaded_models
    
    with model_lock:
        if model_id in loaded_models:
            return  # Already loading or loaded
        
        loaded_models[model_id] = {
            "process": None,
            "port": port,
            "status": "loading"
        }
    
    try:
        # Start new server
        process = start_vllm_server(model_id, port)
        
        with model_lock:
            loaded_models[model_id]["process"] = process
        
        # Wait for server to be ready
        if wait_for_server_ready(port):
            with model_lock:
                loaded_models[model_id]["status"] = "ready"
            print(f"Model '{model_id}' loaded successfully on port {port}")
        else:
            with model_lock:
                loaded_models[model_id]["status"] = "error"
            print(f"Model '{model_id}' failed to start on port {port}")
            
    except Exception as e:
        print(f"Error loading model '{model_id}': {e}")
        with model_lock:
            loaded_models[model_id]["status"] = "error"


@app.route('/models/available', methods=['GET'])
@require_api_key
def get_available_models():
    """List all available models"""
    return jsonify({
        "models": AVAILABLE_MODELS,
        "count": len(AVAILABLE_MODELS)
    })


@app.route('/models/loaded', methods=['GET'])
@require_api_key
def get_loaded_models():
    """Get all currently loaded models"""
    with model_lock:
        loaded_info = []
        for model_id, info in loaded_models.items():
            process = info["process"]
            is_running = process is not None and process.poll() is None
            
            loaded_info.append({
                "model_id": model_id,
                "model_info": AVAILABLE_MODELS.get(model_id, {}),
                "port": info["port"],
                "status": info["status"] if is_running else "stopped",
                "is_running": is_running,
                "vllm_url": f"http://localhost:{info['port']}"
            })
        
        return jsonify({
            "loaded_models": loaded_info,
            "count": len(loaded_info)
        })


@app.route('/models/<model_id>/status', methods=['GET'])
@require_api_key
def get_model_status(model_id):
    """Get status of specific model"""
    if model_id not in AVAILABLE_MODELS:
        return jsonify({
            "error": f"Model '{model_id}' not found",
            "available_models": list(AVAILABLE_MODELS.keys())
        }), 404
    
    with model_lock:
        if model_id in loaded_models:
            info = loaded_models[model_id]
            process = info["process"]
            is_running = process is not None and process.poll() is None
            
            return jsonify({
                "model_id": model_id,
                "model_info": AVAILABLE_MODELS[model_id],
                "port": info["port"],
                "status": info["status"] if is_running else "stopped",
                "is_running": is_running,
                "vllm_url": f"http://localhost:{info['port']}"
            })
        else:
            return jsonify({
                "model_id": model_id,
                "status": "not_loaded",
                "port": None,
                "is_running": False
            })


@app.route('/models/<model_id>/load', methods=['POST'])
@require_api_key
def load_model(model_id):
    """Load a specific model"""
    global loaded_models
    
    if model_id not in AVAILABLE_MODELS:
        return jsonify({
            "error": f"Model '{model_id}' not found",
            "available_models": list(AVAILABLE_MODELS.keys())
        }), 404
    
    with model_lock:
        # Check if already loaded
        if model_id in loaded_models:
            info = loaded_models[model_id]
            process = info["process"]
            if process is not None and process.poll() is None:
                return jsonify({
                    "status": "already_loaded",
                    "model_id": model_id,
                    "port": info["port"],
                    "vllm_url": f"http://localhost:{info['port']}",
                    "message": "Model is already loaded"
                })
            elif info["status"] == "loading":
                return jsonify({
                    "status": "loading",
                    "model_id": model_id,
                    "message": "Model is currently loading"
                }), 409
        
        # Get next available port
        port = get_next_port()
        
        # Start loading in background
        thread = Thread(target=load_model_async, args=(model_id, port), daemon=True)
        thread.start()
        
        return jsonify({
            "status": "loading",
            "model_id": model_id,
            "port": port,
            "vllm_url": f"http://localhost:{port}",
            "message": f"Loading model '{model_id}' on port {port}. This may take 1-3 minutes."
        }), 202


@app.route('/models/<model_id>/unload', methods=['POST'])
@require_api_key
def unload_model(model_id):
    """Unload a specific model"""
    global loaded_models
    
    with model_lock:
        if model_id not in loaded_models:
            return jsonify({
                "error": f"Model '{model_id}' is not loaded",
                "message": "Model is not currently loaded"
            }), 404
        
        info = loaded_models[model_id]
        process = info["process"]
        port = info["port"]
        
        # Stop the server
        if process:
            stop_vllm_server(process)
        
        # Remove from loaded models
        del loaded_models[model_id]
        
        return jsonify({
            "status": "unloaded",
            "model_id": model_id,
            "port": port,
            "message": f"Model '{model_id}' unloaded successfully"
        })


@app.route('/status', methods=['GET'])
@require_api_key
def get_status():
    """Get overall status"""
    with model_lock:
        loaded_count = len(loaded_models)
        running_count = sum(
            1 for info in loaded_models.values()
            if info["process"] is not None and info["process"].poll() is None
        )
        
        return jsonify({
            "manager_status": "running",
            "manager_port": MANAGER_PORT,
            "base_port": BASE_PORT,
            "loaded_models_count": loaded_count,
            "running_models_count": running_count,
            "available_models_count": len(AVAILABLE_MODELS)
        })


@app.route('/health', methods=['GET'])
def health_check():
    """Public health check endpoint (no auth required)"""
    return jsonify({"status": "healthy"}), 200


def cleanup_on_exit(signum, frame):
    """Cleanup when manager exits"""
    global loaded_models
    print("\nShutting down multi-model manager...")
    
    with model_lock:
        for model_id, info in loaded_models.items():
            process = info["process"]
            if process:
                print(f"Stopping model '{model_id}' on port {info['port']}...")
                stop_vllm_server(process)
    
    sys.exit(0)


if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup_on_exit)
    signal.signal(signal.SIGTERM, cleanup_on_exit)

    print("=" * 80)
    print("🚀 vLLM Multi-Model Manager Starting (Public API with Authentication)")
    print("=" * 80)
    print(f"Manager API: http://{MANAGER_HOST}:{MANAGER_PORT}")
    print(f"Base Port for Models: {BASE_PORT}")
    print(f"Available models: {len(AVAILABLE_MODELS)}")
    print(f"API Key: {API_KEY}")
    print(f"API Key File: {API_KEY_FILE}")
    print("=" * 80)
    print()
    print("⚠️  IMPORTANT: Save your API key! You'll need it for all requests.")
    print("   Add header: X-API-Key: <your-api-key>")
    print()
    print("=" * 80)
    print()

    # Start Flask app
    app.run(host=MANAGER_HOST, port=MANAGER_PORT, debug=False, threaded=True)

