#!/usr/bin/env python3
"""
Test client for vLLM server
This script tests the vLLM server with a sample claim extraction task
"""

from openai import OpenAI
import json

# Configure client to point to local vLLM server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # vLLM doesn't require authentication
)

# Sample YouTube transcript for testing
sample_transcript = """
The Earth orbits around the Sun once every 365.25 days. 
Water boils at 100 degrees Celsius at sea level. 
The Great Wall of China is visible from space. 
Python was created by Guido van Rossum in 1991.
"""

# Prompt for claim extraction
prompt = f"""
You are a fact extraction assistant. 
From the following YouTube transcript, extract all **factual claims** in **JSON array format**.
Each claim should be concise, self-contained, and written in natural language. 
Do not include opinions or vague statements. Only include factual, verifiable claims.

Transcript:
{sample_transcript}

Output JSON array of claims:
"""

print("Testing vLLM server...")
print(f"Server URL: http://localhost:8000/v1")
print(f"\nSample transcript:\n{sample_transcript}")
print("\n" + "="*80)

try:
    # Make request to vLLM server
    response = client.completions.create(
        model="MasterControlAIML/DeepSeek-R1-Qwen2.5-1.5b-SFT-R1-JSON-Unstructured-To-Structured",
        prompt=prompt,
        max_tokens=1024,
        temperature=0.0
    )
    
    result = response.choices[0].text
    print("\nExtracted Claims:")
    print(result)
    print("\n" + "="*80)
    
    # Try to parse as JSON
    try:
        # Find JSON array in response
        start_idx = result.find("[")
        end_idx = result.rfind("]") + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = result[start_idx:end_idx]
            claims = json.loads(json_str)
            print(f"\nSuccessfully parsed {len(claims)} claims:")
            for i, claim in enumerate(claims, 1):
                print(f"{i}. {claim}")
        else:
            print("\nCould not find JSON array in response")
    except json.JSONDecodeError as e:
        print(f"\nCould not parse JSON: {e}")
    
    print("\n✅ vLLM server is working correctly!")
    
except Exception as e:
    print(f"\n❌ Error connecting to vLLM server: {e}")
    print("\nMake sure the server is running:")
    print("  cd /lambda/nfs/newinstance/vllm")
    print("  ./start_vllm_server.sh")

