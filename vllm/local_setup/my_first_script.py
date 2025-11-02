#!/usr/bin/env python3
"""
My First vLLM Script with Model Selection
==========================================

This is a simple example showing how to use the vLLM client with model selection.

Usage:
    python my_first_script.py
"""

from vllm_client import VLLMClient


def main():
    print("=" * 80)
    print("🚀 My First vLLM Script")
    print("=" * 80)
    print()
    
    # Step 1: Connect to server
    print("Step 1: Connecting to vLLM server...")
    client = VLLMClient()
    print("✅ Connected!")
    print()
    
    # Step 2: List available models
    print("Step 2: Available models:")
    print("-" * 80)
    client.print_available_models()
    
    # Step 3: Select a model
    print("Step 3: Selecting model...")
    print("   Choosing: qwen-14b-fast (fast & high quality)")
    print()
    client.select_model("qwen-14b-fast")
    print()
    
    # Step 4: Ask a question
    print("Step 4: Asking a question...")
    print("-" * 80)
    question = "Explain machine learning in one sentence"
    print(f"Question: {question}")
    print()
    print("Response: ", end="", flush=True)
    response = client.chat(question, stream=True)
    print()
    print()
    
    # Step 5: Extract claims from YouTube transcript
    print("Step 5: Extracting claims from YouTube transcript...")
    print("-" * 80)
    
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
    
    # Step 6: Try a different model
    print("Step 6: Switching to a different model...")
    print("-" * 80)
    print("   Switching to: t3q-structured (optimized for JSON output)")
    print()
    client.select_model("t3q-structured")
    print()
    
    print("Extracting claims again with structured model...")
    print()
    claims2 = client.extract_claims(sample_transcript)
    print("Extracted claims:")
    print(claims2)
    print()
    
    # Done!
    print("=" * 80)
    print("✅ Script Complete!")
    print("=" * 80)
    print()
    print("You just:")
    print("  ✅ Connected to vLLM server")
    print("  ✅ Listed available models")
    print("  ✅ Selected a model")
    print("  ✅ Asked questions")
    print("  ✅ Extracted claims from transcripts")
    print("  ✅ Switched models during runtime")
    print()
    print("Next steps:")
    print("  • Modify this script for your needs")
    print("  • Process your YouTube transcripts")
    print("  • Experiment with different models")
    print()


if __name__ == "__main__":
    main()

