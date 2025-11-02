#!/usr/bin/env python3
"""
vLLM Model Manager API
======================

This service allows remote clients to switch between different AI models.
It manages the vLLM server process and handles model switching.

Usage:
    python model_manager.py

API Endpoints:
    GET  /models/available  - List all available models
    GET  /models/current    - Get currently loaded model
    POST /models/load       - Load a specific model
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

app = Flask(__name__)

# Configuration
VENV_PYTHON = "/lambda/nfs/newinstance/ai_assessment_dora/venv/bin/python"
VLLM_HOST = "0.0.0.0"
VLLM_PORT = 8000
MANAGER_HOST = "0.0.0.0"  # Listen on all interfaces for public access
MANAGER_PORT = 8001  # Model manager runs on different port

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

# Global state
current_process: Optional[subprocess.Popen] = None
current_model: Optional[str] = None
process_lock = Lock()
is_loading = False


def start_vllm_server(model_id: str) -> subprocess.Popen:
    """Start vLLM server with specified model"""
    model_config = AVAILABLE_MODELS[model_id]
    model_name = model_config["name"]
    max_model_len = model_config["max_model_len"]
    
    cmd = [
        VENV_PYTHON, "-m", "vllm.entrypoints.openai.api_server",
        "--model", model_name,
        "--host", VLLM_HOST,
        "--port", str(VLLM_PORT),
        "--max-model-len", str(max_model_len),
        "--dtype", "auto",
        "--trust-remote-code",
        "--gpu-memory-utilization", "0.95"
    ]
    
    print(f"Starting vLLM server with model: {model_name}")
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


def wait_for_server_ready(timeout: int = 300) -> bool:
    """Wait for vLLM server to be ready"""
    import requests
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:{VLLM_PORT}/health", timeout=2)
            if response.status_code == 200:
                print("vLLM server is ready!")
                return True
        except:
            pass
        time.sleep(2)

    return False


@app.route('/models/available', methods=['GET'])
@require_api_key
def get_available_models():
    """List all available models"""
    return jsonify({
        "models": AVAILABLE_MODELS,
        "count": len(AVAILABLE_MODELS)
    })


@app.route('/models/current', methods=['GET'])
@require_api_key
def get_current_model():
    """Get currently loaded model"""
    global current_model, current_process

    if current_model and current_process and current_process.poll() is None:
        return jsonify({
            "model_id": current_model,
            "model_info": AVAILABLE_MODELS[current_model],
            "status": "running",
            "vllm_url": f"http://localhost:{VLLM_PORT}"
        })
    else:
        return jsonify({
            "model_id": None,
            "status": "no_model_loaded"
        })


@app.route('/models/load', methods=['POST'])
@require_api_key
def load_model():
    """Load a specific model"""
    global current_process, current_model, is_loading, process_lock

    data = request.get_json()
    model_id = data.get('model_id')

    if not model_id:
        return jsonify({"error": "model_id is required"}), 400

    if model_id not in AVAILABLE_MODELS:
        return jsonify({
            "error": f"Model '{model_id}' not found",
            "available_models": list(AVAILABLE_MODELS.keys())
        }), 404

    with process_lock:
        if is_loading:
            return jsonify({"error": "Another model is currently loading"}), 409
        
        is_loading = True
    
    try:
        # Stop current server if running
        if current_process:
            stop_vllm_server(current_process)
            current_process = None
            current_model = None
            time.sleep(2)  # Give it time to clean up
        
        # Start new server
        current_process = start_vllm_server(model_id)
        current_model = model_id
        
        # Wait for server to be ready
        if wait_for_server_ready():
            return jsonify({
                "status": "success",
                "model_id": model_id,
                "model_info": AVAILABLE_MODELS[model_id],
                "vllm_url": f"http://localhost:{VLLM_PORT}",
                "message": "Model loaded successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Model started but did not become ready in time"
            }), 500
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
    finally:
        with process_lock:
            is_loading = False


@app.route('/status', methods=['GET'])
@require_api_key
def get_status():
    """Get overall status"""
    global current_model, current_process, is_loading

    return jsonify({
        "manager_status": "running",
        "is_loading": is_loading,
        "current_model": current_model,
        "vllm_running": current_process is not None and current_process.poll() is None,
        "vllm_port": VLLM_PORT,
        "manager_port": MANAGER_PORT
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Public health check endpoint (no auth required)"""
    return jsonify({"status": "healthy"}), 200


def cleanup_on_exit(signum, frame):
    """Cleanup when manager exits"""
    global current_process
    print("\nShutting down model manager...")
    if current_process:
        stop_vllm_server(current_process)
    sys.exit(0)


if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup_on_exit)
    signal.signal(signal.SIGTERM, cleanup_on_exit)

    print("=" * 80)
    print("🚀 vLLM Model Manager Starting (Public API with Authentication)")
    print("=" * 80)
    print(f"Manager API: http://{MANAGER_HOST}:{MANAGER_PORT}")
    print(f"vLLM API: http://{VLLM_HOST}:{VLLM_PORT}")
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
    app.run(host=MANAGER_HOST, port=MANAGER_PORT, debug=False)

