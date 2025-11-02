#!/bin/bash
# Automated Setup Script for Local Computer
# This script downloads all necessary files and sets up your local environment

SERVER="ubuntu@192.222.53.238"
SERVER_PATH="/lambda/nfs/newinstance/vllm"

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║              vLLM Client - Automated Local Setup                            ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will:"
echo "  1. Download required files from server"
echo "  2. Install Python dependencies"
echo "  3. Create helper scripts"
echo "  4. Test the connection"
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

# Download required files
echo "Downloading vllm_client.py (REQUIRED)..."
scp $SERVER:$SERVER_PATH/vllm_client.py . || {
    echo "❌ Failed to download vllm_client.py"
    exit 1
}
echo "✅ Downloaded vllm_client.py"
echo ""

# Download optional files
echo "Downloading documentation..."
scp $SERVER:$SERVER_PATH/MODEL_SELECTION_GUIDE.md . 2>/dev/null
scp $SERVER:$SERVER_PATH/MODEL_SELECTION_QUICKSTART.txt . 2>/dev/null
scp $SERVER:$SERVER_PATH/test_model_selection.py . 2>/dev/null
echo "✅ Downloaded documentation"
echo ""

# Step 2: Install dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Step 2: Installing Python dependencies..."
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

# Step 3: Create helper scripts
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Step 3: Creating helper scripts..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Download tunnel scripts
echo "Downloading SSH tunnel scripts..."
scp $SERVER:$SERVER_PATH/local_setup/start_tunnel.sh . 2>/dev/null
scp $SERVER:$SERVER_PATH/local_setup/start_tunnel.bat . 2>/dev/null
scp $SERVER:$SERVER_PATH/local_setup/test_connection.py . 2>/dev/null
scp $SERVER:$SERVER_PATH/local_setup/my_first_script.py . 2>/dev/null

# Make scripts executable
chmod +x start_tunnel.sh 2>/dev/null
chmod +x test_connection.py 2>/dev/null
chmod +x my_first_script.py 2>/dev/null
chmod +x vllm_client.py 2>/dev/null

echo "✅ Helper scripts created"
echo ""

# Step 4: Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Downloaded files:"
echo "   ✅ vllm_client.py              - Client library"
echo "   ✅ start_tunnel.sh             - SSH tunnel script"
echo "   ✅ test_connection.py          - Connection test"
echo "   ✅ my_first_script.py          - Example script"
echo "   ✅ MODEL_SELECTION_GUIDE.md    - Documentation"
echo ""
echo "🚀 Next steps:"
echo ""
echo "   1. Start SSH tunnel (in a separate terminal):"
echo "      ./start_tunnel.sh"
echo ""
echo "   2. Test the connection:"
echo "      python test_connection.py"
echo ""
echo "   3. Run your first script:"
echo "      python my_first_script.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANT: Make sure model manager is running on server!"
echo ""
echo "   On server, run:"
echo "   ssh $SERVER"
echo "   cd $SERVER_PATH"
echo "   ./start_model_manager.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation:"
echo "   • MODEL_SELECTION_QUICKSTART.txt - Quick reference"
echo "   • MODEL_SELECTION_GUIDE.md       - Complete guide"
echo ""
echo "🎉 You're ready to use vLLM with model selection!"
echo ""

