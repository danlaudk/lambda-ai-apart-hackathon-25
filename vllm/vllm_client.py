#!/usr/bin/env python3
"""
vLLM Client with Model Selection
=================================

Easy-to-use client for connecting to vLLM server with model selection capability.

Usage:
    from vllm_client import VLLMClient

    # Connect and select model (with API key)
    client = VLLMClient(
        server_ip="192.222.53.238",
        manager_api_key="your-api-key-here"
    )
    client.select_model("qwen-14b-fast")

    # Use the model
    response = client.chat("What is machine learning?")
    print(response)
"""

import requests
import time
from typing import Optional, List, Dict, Any
from openai import OpenAI


class VLLMClient:
    """Client for vLLM server with model selection"""

    def __init__(
        self,
        server_ip: str = "localhost",
        vllm_port: int = 8000,
        manager_port: int = 8001,
        manager_api_key: Optional[str] = None,
        vllm_api_key: str = "dummy"
    ):
        """
        Initialize vLLM client

        Args:
            server_ip: IP address of server (default: localhost)
            vllm_port: Port of vLLM inference server (default: 8000)
            manager_port: Port of model manager API (default: 8001)
            manager_api_key: API key for model manager (REQUIRED for remote access)
            vllm_api_key: API key for vLLM (default: "dummy")
        """
        self.vllm_url = f"http://{server_ip}:{vllm_port}"
        self.manager_url = f"http://{server_ip}:{manager_port}"
        self.manager_api_key = manager_api_key
        self.vllm_api_key = vllm_api_key
        self.openai_client = None
        self.current_model = None

        # Initialize OpenAI client
        self._init_openai_client()
    
    def _init_openai_client(self):
        """Initialize OpenAI client"""
        self.openai_client = OpenAI(
            base_url=f"{self.vllm_url}/v1",
            api_key=self.vllm_api_key
        )

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

    def get_current_model(self) -> Optional[Dict[str, Any]]:
        """
        Get currently loaded model

        Returns:
            Dictionary with current model info or None
        """
        try:
            response = requests.get(
                f"{self.manager_url}/models/current",
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "running":
                self.current_model = data.get("model_id")
                return data
            return None
        except Exception as e:
            print(f"Error getting current model: {e}")
            return None
    
    def select_model(self, model_id: str, wait: bool = True, timeout: int = 300) -> bool:
        """
        Select and load a specific model

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
                f"{self.manager_url}/models/load",
                json={"model_id": model_id},
                headers=self._get_headers(),
                timeout=timeout
            )
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "success":
                self.current_model = model_id
                print(f"✅ Model loaded: {model_id}")
                print(f"   {data['model_info']['description']}")
                return True
            else:
                print(f"❌ Failed to load model: {data.get('message')}")
                return False

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """
        Send a chat message to the model
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic)
            stream: Whether to stream the response
        
        Returns:
            Model response as string
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        try:
            if stream:
                return self._chat_stream(messages, max_tokens, temperature)
            else:
                response = self.openai_client.chat.completions.create(
                    model=self._get_model_name(),
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
        
        except Exception as e:
            return f"Error: {e}"
    
    def _chat_stream(self, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        """Stream chat response"""
        try:
            stream = self.openai_client.chat.completions.create(
                model=self._get_model_name(),
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
        transcript: str,
        max_tokens: int = 1000,
        temperature: float = 0.0
    ) -> str:
        """
        Extract factual claims from YouTube transcript
        
        Args:
            transcript: YouTube video transcript
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 recommended for consistency)
        
        Returns:
            JSON string with extracted claims
        """
        prompt = f"""Extract factual claims and predictions from the following YouTube video transcript.
Return ONLY a JSON array of claims. 
Each claim should be a verifiable statement.
Each claim should be a json object with the following keys: "claim", "time", "confidence".
"claim" is the claim itself. Some claims may be predictions, some may be facts.
"time" is the timepoint for which a prediction is to come true, according to the transcript. If the claim is not a prediction, this should be None.
"confidence" is the confidence in the claim, between 0 and 1.

Transcript:
{transcript}

Return format:
{{"claims": ["claim 1", "claim 2", ...]}}
"""
        
        return self.chat(
            message=prompt,
            system_prompt="You are a factual claim extraction system. Return only valid JSON.",
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    def _get_model_name(self) -> str:
        """Get the full model name for OpenAI client"""
        if not self.current_model:
            # Try to get current model from server
            current = self.get_current_model()
            if current:
                return current["model_info"]["name"]
        
        # Fallback: try to get from vLLM directly
        try:
            models = self.openai_client.models.list()
            if models.data:
                return models.data[0].id
        except:
            pass
        
        # Last resort: use a default
        return "Qwen/Qwen2.5-14B-Instruct"
    
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


# Convenience function for quick usage
def create_client(
    server_url: str = "http://localhost:8000",
    manager_url: str = "http://localhost:8001",
    model_id: Optional[str] = None
) -> VLLMClient:
    """
    Create and optionally configure a vLLM client
    
    Args:
        server_url: vLLM server URL
        manager_url: Model manager URL
        model_id: Optional model to load immediately
    
    Returns:
        Configured VLLMClient instance
    """
    client = VLLMClient(vllm_url=server_url, manager_url=manager_url)
    
    if model_id:
        client.select_model(model_id)
    
    return client


# Example usage
if __name__ == "__main__":
    # Create client
    client = VLLMClient()
    
    # List available models
    client.print_available_models()
    
    # Select a model
    client.select_model("qwen-14b-fast")
    
    # Use the model
    response = client.chat("What is machine learning in one sentence?")
    print(f"\nResponse: {response}")

