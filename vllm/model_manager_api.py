#!/usr/bin/env python3
"""
vLLM Model Manager API
======================

This is a Flask API service that manages vLLM instances and allows
runtime model switching from remote clients.

DEPLOYMENT:
This file should be deployed to the server at:
/lambda/nfs/newinstance/vllm/model_manager_api.py

USAGE ON SERVER:
python model_manager_api.py

This will start the Model Manager API on port 8001.
Clients can then select models remotely via HTTP API.

REQUIREMENTS:
pip install flask psutil requests
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import psutil
import time
import os
import signal
import requests
from typing import Optional, Dict, List
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for remote access

# Configuration
VLLM_PORT = 8000
MANAGER_PORT = 8001
VLLM_HOST = "0.0.0.0"
VLLM_BASE_PATH = "/lambda/nfs/newinstance/vllm"

# Model configurations
AVAILABLE_MODELS = {
    "qwen-14b-fast": {
        "name": "Qwen/Qwen2.5-14B-Instruct",
        "speed": "150-200 tok/s",
        "vram": "28GB",
        "description": "Fast processing, high throughput",
        "max_model_len": 32768,
        "gpu_memory_utilization": 0.95
    },
    "qwen-72b-quality": {
        "name": "Qwen/Qwen2.5-72B-Instruct",
        "speed": "50-70 tok/s",
        "vram": "50GB",
        "description": "Maximum quality, complex analysis",
        "max_model_len": 32768,
        "gpu_memory_utilization": 0.95
    },
    "llama-8b-fast": {
        "name": "meta-llama/Llama-3.1-8B-Instruct",
        "speed": "200+ tok/s",
        "vram": "16GB",
        "description": "Very fast, good for simple tasks",
        "max_model_len": 32768,
        "gpu_memory_utilization": 0.90
    },
    "llama-70b-quality": {
        "name": "meta-llama/Llama-3.1-70B-Instruct",
        "speed": "30-50 tok/s",
        "vram": "140GB",
        "description": "High quality responses",
        "max_model_len": 32768,
        "gpu_memory_utilization": 0.95
    },
    "mistral-7b": {
        "name": "mistralai/Mistral-7B-Instruct-v0.3",
        "speed": "200+ tok/s",
        "vram": "14GB",
        "description": "Fast general purpose",
        "max_model_len": 32768,
        "gpu_memory_utilization": 0.90
    },
    "phi-4-quantized": {
        "name": "phi-4-unsloth-bnb-4bit",
        "speed": "100+ tok/s",
        "vram": "4GB",
        "description": "Quantized, low VRAM",
        "max_model_len": 16384,
        "gpu_memory_utilization": 0.80
    }
}

# Global state
current_vllm_process: Optional[subprocess.Popen] = None
current_model_id: Optional[str] = None
model_loading = False
model_load_lock = threading.Lock()


def kill_vllm_processes():
    """Kill all existing vLLM processes"""
    logger.info("Killing existing vLLM processes...")
    try:
        # Find and kill vllm processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('vllm' in str(arg).lower() for arg in cmdline):
                    logger.info(f"Killing process {proc.info['pid']}: {proc.info['name']}")
                    proc.kill()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
        
        time.sleep(2)  # Wait for processes to fully terminate
        logger.info("All vLLM processes killed")
        return True
    except Exception as e:
        logger.error(f"Error killing vLLM processes: {e}")
        return False


def start_vllm_server(model_id: str) -> bool:
    """Start vLLM server with specified model"""
    global current_vllm_process, current_model_id, model_loading
    
    if model_id not in AVAILABLE_MODELS:
        logger.error(f"Unknown model ID: {model_id}")
        return False
    
    model_config = AVAILABLE_MODELS[model_id]
    model_name = model_config["name"]
    
    logger.info(f"Starting vLLM server with model: {model_name}")
    
    # Build vLLM command
    cmd = [
        "vllm", "serve", model_name,
        "--host", VLLM_HOST,
        "--port", str(VLLM_PORT),
        "--trust-remote-code",
        "--max-model-len", str(model_config["max_model_len"]),
        "--gpu-memory-utilization", str(model_config["gpu_memory_utilization"])
    ]
    
    try:
        # Start vLLM process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=VLLM_BASE_PATH
        )
        
        current_vllm_process = process
        current_model_id = model_id
        
        logger.info(f"vLLM process started with PID: {process.pid}")
        return True
        
    except Exception as e:
        logger.error(f"Error starting vLLM: {e}")
        current_vllm_process = None
        current_model_id = None
        return False


def wait_for_vllm_ready(timeout: int = 300) -> bool:
    """Wait for vLLM server to be ready"""
    logger.info("Waiting for vLLM server to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:{VLLM_PORT}/v1/models", timeout=5)
            if response.status_code == 200:
                logger.info("vLLM server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(5)
    
    logger.error("Timeout waiting for vLLM server")
    return False


def load_model_async(model_id: str):
    """Load model asynchronously"""
    global model_loading
    
    with model_load_lock:
        model_loading = True
        try:
            # Kill existing vLLM processes
            kill_vllm_processes()
            
            # Start new vLLM server
            if start_vllm_server(model_id):
                # Wait for server to be ready
                if wait_for_vllm_ready():
                    logger.info(f"Model {model_id} loaded successfully")
                else:
                    logger.error(f"Model {model_id} failed to load (timeout)")
            else:
                logger.error(f"Failed to start vLLM server for model {model_id}")
        finally:
            model_loading = False


# API Routes

@app.route('/status', methods=['GET'])
def get_status():
    """Get Model Manager status"""
    return jsonify({
        "status": "running",
        "current_model": current_model_id,
        "model_loading": model_loading,
        "vllm_port": VLLM_PORT,
        "manager_port": MANAGER_PORT
    })


@app.route('/models', methods=['GET'])
def list_models():
    """List all available models"""
    models = []
    for model_id, config in AVAILABLE_MODELS.items():
        models.append({
            "id": model_id,
            "name": config["name"],
            "speed": config["speed"],
            "vram": config["vram"],
            "description": config["description"],
            "is_current": model_id == current_model_id
        })
    
    return jsonify({
        "models": models,
        "current_model": current_model_id
    })


@app.route('/models/current', methods=['GET'])
def get_current_model():
    """Get currently loaded model"""
    if current_model_id:
        return jsonify({
            "model_id": current_model_id,
            "model_config": AVAILABLE_MODELS[current_model_id],
            "loading": model_loading
        })
    else:
        return jsonify({
            "model_id": None,
            "message": "No model currently loaded",
            "loading": model_loading
        }), 404


@app.route('/models/select', methods=['POST'])
def select_model():
    """Select and load a model"""
    data = request.get_json()
    model_id = data.get('model_id')
    
    if not model_id:
        return jsonify({"error": "model_id is required"}), 400
    
    if model_id not in AVAILABLE_MODELS:
        return jsonify({"error": f"Unknown model: {model_id}"}), 404
    
    if model_loading:
        return jsonify({"error": "Another model is currently loading"}), 409
    
    if model_id == current_model_id:
        return jsonify({
            "message": f"Model {model_id} is already loaded",
            "model_id": model_id
        })
    
    # Start loading model in background thread
    thread = threading.Thread(target=load_model_async, args=(model_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "message": f"Loading model {model_id}...",
        "model_id": model_id,
        "estimated_time": "1-3 minutes"
    }), 202


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    logger.info("="*80)
    logger.info("🚀 Starting vLLM Model Manager API")
    logger.info("="*80)
    logger.info(f"Manager Port: {MANAGER_PORT}")
    logger.info(f"vLLM Port: {VLLM_PORT}")
    logger.info(f"Available Models: {len(AVAILABLE_MODELS)}")
    logger.info("="*80)
    
    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=MANAGER_PORT,
        debug=False,
        threaded=True
    )

