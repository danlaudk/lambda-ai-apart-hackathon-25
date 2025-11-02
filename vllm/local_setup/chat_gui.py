#!/usr/bin/env python3
"""
vLLM Chat GUI
=============

Simple chat interface for vLLM server using Gradio.

Requirements:
    pip install gradio

Usage:
    python chat_gui.py
"""

import sys
import os

# Add parent directory to path
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

try:
    import gradio as gr
except ImportError:
    print("❌ Error: gradio not installed!")
    print()
    print("Please install gradio:")
    print("  pip install gradio")
    sys.exit(1)

from vllm_client import VLLMClient


# Initialize client
print("Initializing vLLM client...")
client = VLLMClient(
    server_ip=SERVER_IP,
    manager_api_key=API_KEY
)

# Load default model
print("Loading default model...")
client.select_model("qwen-14b-fast")
print("✅ Ready!")


def chat(message, history):
    """Chat function for Gradio"""
    try:
        response = client.chat(message, max_tokens=500)
        return response
    except Exception as e:
        return f"❌ Error: {str(e)}"


def select_model_ui(model_id):
    """Model selection for UI"""
    try:
        print(f"Loading model: {model_id}")
        success = client.select_model(model_id)
        if success:
            return f"✅ Loaded: {model_id}"
        return f"❌ Failed to load: {model_id}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def extract_claims_ui(transcript):
    """Extract claims from transcript"""
    try:
        claims = client.extract_claims(transcript)
        return claims
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Create UI
with gr.Blocks(title="vLLM Chat", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 vLLM Chat Interface")
    gr.Markdown(f"Connected to: **{SERVER_IP}**")
    
    with gr.Tab("💬 Chat"):
        with gr.Row():
            model_dropdown = gr.Dropdown(
                choices=[
                    "qwen-14b-fast",
                    "qwen-72b-quality",
                    "deepseek-v3-reasoning",
                    "qwen-vl-7b-multimodal",
                    "mistral-large-chat",
                    "phi-4-quantized",
                    "t3q-structured",
                    "calme-analysis",
                    "rombos-merge"
                ],
                value="qwen-14b-fast",
                label="Select Model"
            )
            model_status = gr.Textbox(
                label="Status",
                value="✅ qwen-14b-fast loaded",
                interactive=False
            )
        
        model_dropdown.change(
            select_model_ui,
            inputs=[model_dropdown],
            outputs=[model_status]
        )
        
        chatbot = gr.ChatInterface(
            chat,
            examples=[
                "What is machine learning?",
                "Explain quantum computing in simple terms",
                "Write a Python function to calculate fibonacci numbers"
            ],
            title=None
        )
    
    with gr.Tab("📋 Claim Extraction"):
        gr.Markdown("Extract factual claims from YouTube transcripts")
        
        with gr.Row():
            with gr.Column():
                transcript_input = gr.Textbox(
                    label="YouTube Transcript",
                    placeholder="Paste your YouTube transcript here...",
                    lines=10
                )
                extract_btn = gr.Button("Extract Claims", variant="primary")
            
            with gr.Column():
                claims_output = gr.Textbox(
                    label="Extracted Claims",
                    lines=10
                )
        
        extract_btn.click(
            extract_claims_ui,
            inputs=[transcript_input],
            outputs=[claims_output]
        )
        
        gr.Examples(
            examples=[[
                """Python is a popular programming language. It was created by 
                Guido van Rossum in 1991. Today, over 8 million developers use 
                Python worldwide. The language is known for its simplicity."""
            ]],
            inputs=[transcript_input]
        )
    
    with gr.Tab("ℹ️ Info"):
        gr.Markdown(f"""
        ## Server Information
        
        - **Server IP:** {SERVER_IP}
        - **Model Manager Port:** 8001
        - **vLLM Port:** 8000
        
        ## Available Models
        
        | Model | Speed | Best For |
        |-------|-------|----------|
        | qwen-14b-fast | 150-200 tok/s | Fast processing ⚡ |
        | qwen-72b-quality | 50-70 tok/s | Maximum quality 💎 |
        | deepseek-v3-reasoning | 60-80 tok/s | Complex reasoning 🧠 |
        | qwen-vl-7b-multimodal | 100-120 tok/s | Images + text 🖼️ |
        | mistral-large-chat | 40-60 tok/s | Conversations 💬 |
        | phi-4-quantized | 200+ tok/s | Low memory 🔧 |
        | t3q-structured | 120-150 tok/s | JSON output 📋 |
        | calme-analysis | 45-65 tok/s | Deep analysis 🎓 |
        | rombos-merge | 50-70 tok/s | Combined strengths 🔀 |
        
        ## Tips
        
        - Switch models based on your task
        - Faster models = lower quality
        - Slower models = higher quality
        - Model loading takes 1-3 minutes
        """)

# Launch
print()
print("=" * 80)
print("🚀 Launching Chat GUI")
print("=" * 80)
print()
print("Opening in browser...")
print("If it doesn't open automatically, go to: http://localhost:7860")
print()

demo.launch(
    share=False,
    server_name="0.0.0.0",
    server_port=7860,
    show_error=True
)

