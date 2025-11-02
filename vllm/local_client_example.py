#!/usr/bin/env python3
"""
vLLM Remote Client Example
==========================

This script demonstrates how to connect to your vLLM server from your local computer.

SETUP:
1. On server: Start vLLM server
   cd /lambda/nfs/newinstance/vllm && ./start_vllm_server.sh

2. On local computer: Create SSH tunnel
   ssh -L 8000:localhost:8000 ubuntu@192.222.53.238

3. On local computer: Run this script
   python local_client_example.py

REQUIREMENTS:
pip install openai
"""

from openai import OpenAI
import sys

# Configuration
VLLM_BASE_URL = "http://localhost:8000/v1"  # Through SSH tunnel
# For direct access (not recommended): "http://192.222.53.238:8000/v1"

API_KEY = "dummy"  # vLLM doesn't require real API key by default

def test_connection():
    """Test if we can connect to the vLLM server"""
    print("🔍 Testing connection to vLLM server...")
    print(f"   Base URL: {VLLM_BASE_URL}")
    print()
    
    try:
        client = OpenAI(base_url=VLLM_BASE_URL, api_key=API_KEY)
        
        # List available models
        models = client.models.list()
        print("✅ Connection successful!")
        print(f"\n📋 Available models ({len(models.data)}):")
        for model in models.data:
            print(f"   - {model.id}")
        
        return client, models.data
    
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Is vLLM server running on the remote machine?")
        print("   2. Is SSH tunnel active? (ssh -L 8000:localhost:8000 ubuntu@192.222.53.238)")
        print("   3. Check server logs: tail -f /lambda/nfs/newinstance/vllm/vllm_server.log")
        sys.exit(1)


def chat_completion_example(client, model_name):
    """Example: Chat completion"""
    print(f"\n💬 Chat Completion Example")
    print(f"   Model: {model_name}")
    print("-" * 80)
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Explain what a Large Language Model is in one sentence."}
    ]
    
    print("📤 Sending request...")
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=100,
        temperature=0.7
    )
    
    print(f"📥 Response:")
    print(f"   {response.choices[0].message.content}")
    print()
    print(f"📊 Stats:")
    print(f"   Tokens used: {response.usage.total_tokens}")
    print(f"   Prompt tokens: {response.usage.prompt_tokens}")
    print(f"   Completion tokens: {response.usage.completion_tokens}")


def streaming_example(client, model_name):
    """Example: Streaming response"""
    print(f"\n🌊 Streaming Example")
    print(f"   Model: {model_name}")
    print("-" * 80)
    
    messages = [
        {"role": "user", "content": "Count from 1 to 10 slowly."}
    ]
    
    print("📤 Sending streaming request...")
    print("📥 Response (streaming): ", end="", flush=True)
    
    stream = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=100,
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    
    print("\n")


def youtube_claim_extraction_example(client, model_name):
    """Example: Extract claims from YouTube transcript (your use case!)"""
    print(f"\n🎥 YouTube Claim Extraction Example")
    print(f"   Model: {model_name}")
    print("-" * 80)
    
    # Sample YouTube transcript
    transcript = """
    In this video, I'm going to show you how to build a web application using Python.
    Python is the most popular programming language in 2024 according to the TIOBE index.
    We'll be using Flask, which is a lightweight web framework. Flask was created by
    Armin Ronacher in 2010. By the end of this tutorial, you'll have a fully functional
    web app deployed to the cloud.
    """
    
    prompt = f"""Extract factual claims from the following YouTube video transcript.
Return ONLY a JSON array of claims. Each claim should be a verifiable statement.

Transcript:
{transcript}

Return format:
{{"claims": ["claim 1", "claim 2", ...]}}
"""
    
    print("📤 Extracting claims from transcript...")
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a factual claim extraction system. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.0  # Low temperature for consistent extraction
    )
    
    print(f"📥 Extracted Claims:")
    print(response.choices[0].message.content)


def interactive_chat(client, model_name):
    """Interactive chat session"""
    print(f"\n💭 Interactive Chat Mode")
    print(f"   Model: {model_name}")
    print("   Type 'quit' or 'exit' to end the conversation")
    print("-" * 80)
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        print("🤖 Assistant: ", end="", flush=True)
        
        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            stream=True
        )
        
        assistant_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                assistant_response += content
        
        print()  # New line after response
        messages.append({"role": "assistant", "content": assistant_response})


def main():
    """Main function"""
    print("=" * 80)
    print("🚀 vLLM Remote Client - Connection Test & Examples")
    print("=" * 80)
    
    # Test connection and get available models
    client, models = test_connection()
    
    if not models:
        print("❌ No models available. Please start vLLM server with a model.")
        sys.exit(1)
    
    # Use the first available model
    model_name = models[0].id
    
    # Run examples
    print("\n" + "=" * 80)
    print("📚 Running Examples")
    print("=" * 80)
    
    try:
        # Example 1: Basic chat completion
        chat_completion_example(client, model_name)
        
        # Example 2: Streaming
        streaming_example(client, model_name)
        
        # Example 3: YouTube claim extraction (your use case!)
        youtube_claim_extraction_example(client, model_name)
        
        # Example 4: Interactive chat (optional)
        print("\n" + "=" * 80)
        response = input("Would you like to try interactive chat mode? (y/n): ").strip().lower()
        if response == 'y':
            interactive_chat(client, model_name)
        
        print("\n" + "=" * 80)
        print("✅ All examples completed successfully!")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

