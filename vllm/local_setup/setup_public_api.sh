#!/bin/bash
# Setup script for vLLM Public API Client
# Run this on your LOCAL computer

SERVER="ubuntu@192.222.53.238"
SERVER_PATH="/lambda/nfs/newinstance/vllm"

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║              vLLM Public API Client - Setup Script                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will set up direct API access to your vLLM server."
echo "No SSH tunnel required!"
echo ""
echo "Server: $SERVER"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Step 1: Download files
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📥 Step 1: Downloading files from server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Download client library
echo "Downloading vllm_client.py..."
scp $SERVER:$SERVER_PATH/vllm_client.py . || {
    echo "❌ Failed to download vllm_client.py"
    exit 1
}
echo "✅ Downloaded vllm_client.py"
echo ""

# Download config example
echo "Downloading config_example.py..."
scp $SERVER:$SERVER_PATH/local_setup/config_example.py . || {
    echo "❌ Failed to download config_example.py"
    exit 1
}
echo "✅ Downloaded config_example.py"
echo ""

# Download test script
echo "Downloading test_public_api.py..."
scp $SERVER:$SERVER_PATH/local_setup/test_public_api.py . || {
    echo "❌ Failed to download test_public_api.py"
    exit 1
}
echo "✅ Downloaded test_public_api.py"
echo ""

# Download chat GUI
echo "Downloading chat_gui.py..."
scp $SERVER:$SERVER_PATH/local_setup/chat_gui.py . || {
    echo "⚠️  Warning: Failed to download chat_gui.py (optional)"
}
echo ""

# Download documentation
echo "Downloading documentation..."
scp $SERVER:$SERVER_PATH/PUBLIC_API_SETUP.md . 2>/dev/null
echo "✅ Downloaded documentation"
echo ""

# Step 2: Create config file
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 Step 2: Creating configuration file..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -f config.py ]; then
    echo "Creating config.py from example..."
    cp config_example.py config.py
    echo "✅ Created config.py"
    echo ""
    echo "⚠️  IMPORTANT: config.py contains your API key"
    echo "   The API key is already set from the server"
else
    echo "ℹ️  config.py already exists, skipping..."
fi
echo ""

# Step 3: Install dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Step 3: Installing Python dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip not found. Please install Python and pip first."
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "Installing openai and requests..."
$PIP_CMD install openai requests || {
    echo "⚠️  Warning: Failed to install dependencies"
    echo "   You may need to run: pip install openai requests"
}
echo "✅ Dependencies installed"
echo ""

echo "Installing gradio (optional, for chat GUI)..."
$PIP_CMD install gradio 2>/dev/null || {
    echo "⚠️  Gradio not installed (optional)"
}
echo ""

# Step 4: Make scripts executable
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Step 4: Making scripts executable..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

chmod +x test_public_api.py 2>/dev/null
chmod +x chat_gui.py 2>/dev/null
chmod +x vllm_client.py 2>/dev/null

echo "✅ Scripts are executable"
echo ""

# Step 5: Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Downloaded files:"
echo "   ✅ vllm_client.py              - Client library"
echo "   ✅ config.py                   - Configuration (with API key)"
echo "   ✅ test_public_api.py          - Connection test"
echo "   ✅ chat_gui.py                 - Chat GUI (optional)"
echo "   ✅ PUBLIC_API_SETUP.md         - Documentation"
echo ""
echo "🚀 Next steps:"
echo ""
echo "   1. Test the connection:"
echo "      python test_public_api.py"
echo ""
echo "   2. Launch chat GUI (optional):"
echo "      python chat_gui.py"
echo ""
echo "   3. Use in your own scripts:"
echo "      from vllm_client import VLLMClient"
echo "      from config import SERVER_IP, API_KEY"
echo "      client = VLLMClient(server_ip=SERVER_IP, manager_api_key=API_KEY)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔒 Security Note:"
echo "   Your API key is stored in config.py"
echo "   Keep this file secure and don't commit it to version control!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 You're ready to use vLLM with direct API access!"
echo ""

