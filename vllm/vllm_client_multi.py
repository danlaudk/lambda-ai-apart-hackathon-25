#!/usr/bin/env python3
"""
vLLM Multi-Model Client with Model Selection
============================================

Easy-to-use client for connecting to multiple vLLM servers simultaneously.
Each model runs on its own port starting from 8002.

Usage:
    from vllm_client_multi import VLLMClientMulti

    # Connect to multi-model manager
    client = VLLMClientMulti(
        server_ip="192.222.53.238",
        manager_api_key="your-api-key-here"
    )
    
    # Load a model (starts on port 8002)
    client.load_model("qwen-14b-fast")
    
    # Load another model (starts on port 8003)
    client.load_model("qwen-72b-quality")
    
    # Use specific model
    response = client.chat("qwen-14b-fast", "What is machine learning?")
    print(response)
    
    # Unload a model
    client.unload_model("qwen-14b-fast")
"""

import requests
import time
from typing import Optional, List, Dict, Any
from openai import OpenAI


class VLLMClientMulti:
    """Client for multi-model vLLM servers"""

    def __init__(
        self,
        server_ip: str = "localhost",
        manager_port: int = 8001,
        manager_api_key: Optional[str] = None,
        vllm_api_key: str = "dummy"
    ):
        """
        Initialize multi-model vLLM client

        Args:
            server_ip: IP address of server (default: localhost)
            manager_port: Port of model manager API (default: 8001)
            manager_api_key: API key for model manager (REQUIRED for remote access)
            vllm_api_key: API key for vLLM (default: "dummy")
        """
        self.server_ip = server_ip
        self.manager_url = f"http://{server_ip}:{manager_port}"
        self.manager_api_key = manager_api_key
        self.vllm_api_key = vllm_api_key
        
        # Track loaded models and their OpenAI clients
        # Format: {model_id: {"port": int, "client": OpenAI}}
        self.loaded_models: Dict[str, Dict] = {}
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with API key for manager requests"""
        if self.manager_api_key:
            return {"X-API-Key": self.manager_api_key}
        return {}

    def list_available_models(self) -> Dict[str, Any]:
        """
        List all available models

        Returns:
            Dictionary with available models and their info
        """
        try:
            response = requests.get(
                f"{self.manager_url}/models/available",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error listing models: {e}")
            return {"models": {}, "count": 0}

    def get_loaded_models(self) -> Dict[str, Any]:
        """
        Get all currently loaded models

        Returns:
            Dictionary with loaded models and their info
        """
        try:
            response = requests.get(
                f"{self.manager_url}/models/loaded",
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            
            # Update local cache
            for model_info in data.get("loaded_models", []):
                model_id = model_info["model_id"]
                port = model_info["port"]
                is_running = model_info.get("is_running", False)
                
                if is_running and model_id not in self.loaded_models:
                    # Create OpenAI client for this model
                    vllm_url = f"http://{self.server_ip}:{port}"
                    openai_client = OpenAI(
                        base_url=f"{vllm_url}/v1",
                        api_key=self.vllm_api_key
                    )
                    self.loaded_models[model_id] = {
                        "port": port,
                        "client": openai_client,
                        "url": vllm_url
                    }
            
            return data
        except Exception as e:
            print(f"Error getting loaded models: {e}")
            return {"loaded_models": [], "count": 0}
    
    def get_model_status(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of specific model

        Args:
            model_id: ID of model to check

        Returns:
            Dictionary with model status or None
        """
        try:
            response = requests.get(
                f"{self.manager_url}/models/{model_id}/status",
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            
            # Update local cache if model is loaded
            if data.get("is_running") and model_id not in self.loaded_models:
                port = data["port"]
                vllm_url = f"http://{self.server_ip}:{port}"
                openai_client = OpenAI(
                    base_url=f"{vllm_url}/v1",
                    api_key=self.vllm_api_key
                )
                self.loaded_models[model_id] = {
                    "port": port,
                    "client": openai_client,
                    "url": vllm_url
                }
            
            return data
        except Exception as e:
            print(f"Error getting model status: {e}")
            return None
    
    def load_model(self, model_id: str, wait: bool = True, timeout: int = 300) -> bool:
        """
        Load a specific model

        Args:
            model_id: ID of model to load (e.g., "qwen-14b-fast")
            wait: Whether to wait for model to load (default: True)
            timeout: Maximum seconds to wait for model to load (default: 300)

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🔄 Loading model: {model_id}")
            print("   This may take 1-3 minutes...")

            response = requests.post(
                f"{self.manager_url}/models/{model_id}/load",
                headers=self._get_headers(),
                timeout=timeout
            )
            response.raise_for_status()

            data = response.json()
            
            if wait:
                # Wait for model to be ready
                start_time = time.time()
                while time.time() - start_time < timeout:
                    status = self.get_model_status(model_id)
                    if status and status.get("is_running"):
                        port = status["port"]
                        vllm_url = f"http://{self.server_ip}:{port}"
                        openai_client = OpenAI(
                            base_url=f"{vllm_url}/v1",
                            api_key=self.vllm_api_key
                        )
                        self.loaded_models[model_id] = {
                            "port": port,
                            "client": openai_client,
                            "url": vllm_url
                        }
                        print(f"✅ Model loaded: {model_id} on port {port}")
                        return True
                    time.sleep(5)
                
                print(f"⏱️  Timeout waiting for model {model_id} to load")
                return False
            else:
                print(f"🔄 Model loading started: {model_id} on port {data.get('port')}")
                return True

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def unload_model(self, model_id: str) -> bool:
        """
        Unload a specific model

        Args:
            model_id: ID of model to unload

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🔄 Unloading model: {model_id}")

            response = requests.post(
                f"{self.manager_url}/models/{model_id}/unload",
                headers=self._get_headers()
            )
            response.raise_for_status()

            # Remove from local cache
            if model_id in self.loaded_models:
                del self.loaded_models[model_id]
            
            print(f"✅ Model unloaded: {model_id}")
            return True

        except Exception as e:
            print(f"❌ Error unloading model: {e}")
            return False
    
    def chat(
        self,
        model_id: str,
        message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """
        Send a chat message to a specific model
        
        Args:
            model_id: ID of model to use
            message: User message
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic)
            stream: Whether to stream the response
        
        Returns:
            Model response as string
        """
        # Check if model is loaded locally
        if model_id not in self.loaded_models:
            # Try to get status and load client
            status = self.get_model_status(model_id)
            if not status or not status.get("is_running"):
                return f"Error: Model '{model_id}' is not loaded. Use load_model() first."
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        try:
            client = self.loaded_models[model_id]["client"]
            
            if stream:
                return self._chat_stream(client, model_id, messages, max_tokens, temperature)
            else:
                # Get model name from status
                status = self.get_model_status(model_id)
                model_name = status.get("model_info", {}).get("name", model_id)
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
        
        except Exception as e:
            return f"Error: {e}"
    
    def _chat_stream(self, client: OpenAI, model_id: str, messages: List[Dict], 
                     max_tokens: int, temperature: float) -> str:
        """Stream chat response"""
        try:
            status = self.get_model_status(model_id)
            model_name = status.get("model_info", {}).get("name", model_id)
            
            stream = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            print()  # New line after streaming
            return full_response
        
        except Exception as e:
            return f"Error: {e}"
    
    def extract_claims(
        self,
        model_id: str,
        transcript: str,
        max_tokens: int = 1000,
        temperature: float = 0.0
    ) -> str:
        """
        Extract factual claims from YouTube transcript using specific model
        
        Args:
            model_id: ID of model to use
            transcript: YouTube video transcript
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 recommended for consistency)
        
        Returns:
            JSON string with extracted claims
        """
        prompt = f"""Extract factual claims from the following YouTube video transcript.
Return ONLY a JSON array of claims. Each claim should be a verifiable statement.

Transcript:
{transcript}

Return format:
{{"claims": ["claim 1", "claim 2", ...]}}
"""
        
        return self.chat(
            model_id=model_id,
            message=prompt,
            system_prompt="You are a factual claim extraction system. Return only valid JSON.",
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    def print_available_models(self):
        """Print available models in a nice format"""
        data = self.list_available_models()
        models = data.get("models", {})
        
        print("\n" + "=" * 80)
        print("📋 Available Models")
        print("=" * 80)
        
        for model_id, info in models.items():
            print(f"\n🔹 {model_id}")
            print(f"   Name: {info['name']}")
            print(f"   Description: {info['description']}")
            print(f"   VRAM: {info['vram']} | Speed: {info['speed']}")
            print(f"   Best for: {info['best_for']}")
        
        print("\n" + "=" * 80)
        print(f"Total: {len(models)} models available")
        print("=" * 80 + "\n")
    
    def print_loaded_models(self):
        """Print loaded models in a nice format"""
        data = self.get_loaded_models()
        loaded = data.get("loaded_models", [])
        
        print("\n" + "=" * 80)
        print("📋 Loaded Models")
        print("=" * 80)
        
        if not loaded:
            print("\nNo models currently loaded.")
        else:
            for model_info in loaded:
                model_id = model_info["model_id"]
                port = model_info["port"]
                status = model_info.get("status", "unknown")
                is_running = model_info.get("is_running", False)
                
                print(f"\n🔹 {model_id}")
                print(f"   Port: {port}")
                print(f"   Status: {status}")
                print(f"   Running: {'✅ Yes' if is_running else '❌ No'}")
                print(f"   URL: http://localhost:{port}")
        
        print("\n" + "=" * 80)
        print(f"Total: {len(loaded)} models loaded")
        print("=" * 80 + "\n")


# Convenience function for quick usage
def create_client(
    server_ip: str = "localhost",
    manager_port: int = 8001,
    manager_api_key: Optional[str] = None
) -> VLLMClientMulti:
    """
    Create and configure a multi-model vLLM client
    
    Args:
        server_ip: Server IP address
        manager_port: Model manager port
        manager_api_key: API key for model manager
    
    Returns:
        Configured VLLMClientMulti instance
    """
    return VLLMClientMulti(
        server_ip=server_ip,
        manager_port=manager_port,
        manager_api_key=manager_api_key
    )


# Example usage
if __name__ == "__main__":
    # Create client
    client = VLLMClientMulti()
    
    # List available models
    client.print_available_models()
    
    # Load a model
    client.load_model("qwen-14b-fast")
    
    # Load another model
    client.load_model("qwen-72b-quality")
    
    # Show loaded models
    client.print_loaded_models()
    
    # Use specific model
    response = client.chat("qwen-14b-fast", "What is machine learning in one sentence?")
    print(f"\nResponse from qwen-14b-fast: {response}")
    
    # Unload a model
    client.unload_model("qwen-14b-fast")

