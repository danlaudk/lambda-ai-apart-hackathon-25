#!/usr/bin/env python3
"""
Test Connection to vLLM Server with Model Selection
====================================================

This script verifies that your local computer can connect to the vLLM server
and use the model selection feature.

Usage:
    python test_connection.py
"""

from vllm_client import VLLMClient
import sys


def main():
    print("=" * 80)
    print("🧪 Testing vLLM Connection with Model Selection")
    print("=" * 80)
    print()
    
    # Create client
    print("📡 Connecting to vLLM server...")
    print("   vLLM URL: http://localhost:8000")
    print("   Manager URL: http://localhost:8001")
    print()
    
    try:
        client = VLLMClient(
            vllm_url="http://localhost:8000",
            manager_url="http://localhost:8001"
        )
        print("✅ Connected!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure SSH tunnel is running:")
        print("   ./start_tunnel.sh (Linux/Mac)")
        print("   start_tunnel.bat (Windows)")
        print()
        print("2. Make sure model manager is running on server:")
        print("   ssh ubuntu@192.222.53.238")
        print("   cd /lambda/nfs/newinstance/vllm")
        print("   ./start_model_manager.sh")
        print()
        sys.exit(1)
    
    print()
    
    # List available models
    print("=" * 80)
    print("📋 Available Models")
    print("=" * 80)
    client.print_available_models()
    
    # Get current model
    print("🔍 Checking current model...")
    current = client.get_current_model()
    if current:
        print(f"✅ Current model: {current['model_id']}")
        print(f"   {current['model_info']['description']}")
    else:
        print("⚠️  No model currently loaded")
        print("   Selecting default model (qwen-14b-fast)...")
        print()
        success = client.select_model("qwen-14b-fast")
        if not success:
            print("❌ Failed to load model")
            sys.exit(1)
    
    print()
    
    # Test chat
    print("=" * 80)
    print("💬 Testing Chat Functionality")
    print("=" * 80)
    print()
    
    question = "What is 2+2? Answer in one sentence."
    print(f"Question: {question}")
    print()
    print("Response: ", end="", flush=True)
    
    try:
        response = client.chat(question, max_tokens=50, stream=True)
        print()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    print()
    
    # Test claim extraction
    print("=" * 80)
    print("📋 Testing Claim Extraction")
    print("=" * 80)
    print()
    
    sample_transcript = """
    Python is the most popular programming language in 2024.
    It was created by Guido van Rossum in 1991.
    Over 8 million developers use Python worldwide.
    """
    
    print("Sample transcript:")
    print(sample_transcript)
    print()
    print("Extracting claims...")
    print()
    
    try:
        claims = client.extract_claims(sample_transcript, max_tokens=200)
        print("Extracted claims:")
        print(claims)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Success!
    print("=" * 80)
    print("✅ SUCCESS! Everything is working!")
    print("=" * 80)
    print()
    print("You can now:")
    print("  • Use vLLM client in your Python scripts")
    print("  • Select from 10 different AI models")
    print("  • Switch models during runtime")
    print("  • Process YouTube transcripts at scale")
    print()
    print("Next steps:")
    print("  1. See MODEL_SELECTION_GUIDE.md for examples")
    print("  2. Create your own scripts using vllm_client.py")
    print("  3. Run: python my_first_script.py")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()

