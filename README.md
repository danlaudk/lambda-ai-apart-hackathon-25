# NewInstance Project

This repository contains multiple AI/LLM related projects and utilities.

## Project Structure

### vllm/
vLLM Model Manager API - A Flask-based API service for managing vLLM instances and runtime model switching. Supports multiple models including Qwen, Llama, Mistral, and Phi-4.

**Key Features:**
- Runtime model switching via HTTP API
- Multi-model support
- Remote access capabilities
- Local and remote setup guides

See `vllm/README.md` for detailed documentation.

### ai_assessment_dora/
Assessment tools for Dora project using LLM capabilities.

### ai_assessment_corey/
Assessment tools for Corey project.

### ai_api_script/
API scripts and utilities.

### ollama/
Ollama-related configurations and scripts.

## Getting Started

### Prerequisites
- Python 3.10+
- vLLM installed (for vllm components)
- Required Python packages (see `vllm/requirements.txt`)

### Quick Start

1. Navigate to the desired component directory
2. Follow component-specific setup instructions
3. For vLLM setup, see `vllm/README.md` or `vllm/QUICKSTART.md`

## Notes

- Virtual environments (`venv/`) are excluded from version control
- Database files (`.db`) are excluded from version control
- See `.gitignore` for a complete list of excluded files

## License

[Add license information if applicable]

