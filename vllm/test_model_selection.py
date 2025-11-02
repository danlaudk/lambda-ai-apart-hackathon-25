#!/usr/bin/env python3
"""
Test Model Selection Feature
=============================

This script demonstrates how to select different AI models from your local computer.

Usage:
    python test_model_selection.py
"""

from vllm_client import VLLMClient
import sys


def main():
    print("=" * 80)
    print("🧪 Testing vLLM Model Selection")
    print("=" * 80)
    print()
    
    # Create client
    print("📡 Connecting to vLLM server...")
    client = VLLMClient(
        vllm_url="http://localhost:8000",
        manager_url="http://localhost:8001"
    )
    print("✅ Connected!")
    print()
    
    # Show available models
    client.print_available_models()
    
    # Get current model
    print("🔍 Checking current model...")
    current = client.get_current_model()
    if current:
        print(f"✅ Current model: {current['model_id']}")
        print(f"   {current['model_info']['description']}")
    else:
        print("⚠️  No model currently loaded")
    print()
    
    # Interactive model selection
    print("=" * 80)
    print("🎯 Model Selection Test")
    print("=" * 80)
    print()
    print("Available model IDs:")
    print("  - qwen-14b-fast (recommended for testing)")
    print("  - qwen-72b-quality")
    print("  - deepseek-v3-reasoning")
    print("  - qwen-vl-7b-multimodal")
    print("  - t3q-structured")
    print("  - phi-4-quantized")
    print()
    
    model_id = input("Enter model ID to load (or 'skip' to use current): ").strip()
    
    if model_id and model_id.lower() != 'skip':
        print()
        success = client.select_model(model_id)
        if not success:
            print("❌ Failed to load model. Exiting.")
            sys.exit(1)
        print()
    
    # Test the model
    print("=" * 80)
    print("💬 Testing Chat Functionality")
    print("=" * 80)
    print()
    
    test_questions = [
        "What is machine learning in one sentence?",
        "Name three programming languages.",
        "What is 2+2?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"Question {i}: {question}")
        print("Response: ", end="", flush=True)
        
        response = client.chat(
            message=question,
            max_tokens=100,
            temperature=0.7,
            stream=True  # Stream the response
        )
        print()
    
    # Test claim extraction
    print()
    print("=" * 80)
    print("📋 Testing Claim Extraction")
    print("=" * 80)
    print()
    
    sample_transcript = """
    In this video, I'll show you how Python became the most popular 
    programming language in 2024. Python was created by Guido van Rossum 
    in 1991. Today, over 8 million developers use Python worldwide.
    The language is known for its simplicity and readability.
    """
    
    print("Sample transcript:")
    print(sample_transcript)
    print()
    print("Extracting claims...")
    print()
    
    claims = client.extract_claims(sample_transcript)
    print("Extracted claims:")
    print(claims)
    print()
    
    # Interactive chat
    print("=" * 80)
    print("💭 Interactive Chat Mode")
    print("=" * 80)
    print("Type your questions (or 'quit' to exit)")
    print("=" * 80)
    print()
    
    while True:
        try:
            question = input("You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print("Assistant: ", end="", flush=True)
            client.chat(question, stream=True)
            print()
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break
    
    print()
    print("=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

