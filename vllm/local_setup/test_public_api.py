#!/usr/bin/env python3
"""
Test Public API Connection
===========================

This script tests the connection to the vLLM server using direct API access.
No SSH tunnel required!

Usage:
    python test_public_api.py
"""

import sys
import os

# Add parent directory to path to import vllm_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import SERVER_IP, API_KEY
except ImportError:
    print("❌ Error: config.py not found!")
    print()
    print("Please create config.py from config_example.py:")
    print("  cp config_example.py config.py")
    print("  # Then edit config.py with your API key")
    sys.exit(1)

from vllm_client import VLLMClient


def main():
    print("=" * 80)
    print("🧪 Testing vLLM Public API Connection")
    print("=" * 80)
    print()
    print(f"Server: {SERVER_IP}")
    print(f"API Key: {API_KEY[:20]}...")
    print()
    
    # Step 1: Connect
    print("Step 1: Connecting to server...")
    print("-" * 80)
    try:
        client = VLLMClient(
            server_ip=SERVER_IP,
            manager_api_key=API_KEY
        )
        print("✅ Client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return
    print()
    
    # Step 2: List available models
    print("Step 2: Listing available models...")
    print("-" * 80)
    try:
        models = client.list_available_models()
        if models['count'] > 0:
            print(f"✅ Found {models['count']} models")
            print()
            client.print_available_models()
        else:
            print("❌ No models found")
            return
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        print()
        print("Possible issues:")
        print("  • API key is incorrect")
        print("  • Server is not running")
        print("  • Firewall blocking connection")
        print("  • Wrong server IP")
        return
    print()
    
    # Step 3: Check current model
    print("Step 3: Checking current model...")
    print("-" * 80)
    try:
        current = client.get_current_model()
        if current:
            print(f"✅ Current model: {current['model_id']}")
        else:
            print("ℹ️  No model currently loaded")
    except Exception as e:
        print(f"⚠️  Could not check current model: {e}")
    print()
    
    # Step 4: Test model selection
    print("Step 4: Testing model selection...")
    print("-" * 80)
    print("   Selecting: qwen-14b-fast")
    print("   This will take 1-3 minutes...")
    print()
    try:
        success = client.select_model("qwen-14b-fast")
        if success:
            print("✅ Model loaded successfully!")
        else:
            print("❌ Failed to load model")
            return
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    print()
    
    # Step 5: Test chat
    print("Step 5: Testing chat...")
    print("-" * 80)
    try:
        response = client.chat("Say hello in one sentence!")
        print(f"✅ Chat response: {response}")
    except Exception as e:
        print(f"❌ Chat failed: {e}")
        return
    print()
    
    # Step 6: Test claim extraction
    print("Step 6: Testing claim extraction...")
    print("-" * 80)
    sample_transcript = """
    Python is a popular programming language. It was created by Guido van Rossum
    in 1991. Today, over 8 million developers use Python worldwide.
    """
    try:
        claims = client.extract_claims(sample_transcript)
        print("✅ Claim extraction:")
        print(claims)
    except Exception as e:
        print(f"❌ Claim extraction failed: {e}")
    print()
    
    # Success!
    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Your vLLM client is working correctly!")
    print()
    print("Next steps:")
    print("  • Use client in your own scripts")
    print("  • Try different models")
    print("  • Launch chat GUI: python chat_gui.py")
    print()


if __name__ == "__main__":
    main()

