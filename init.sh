#!/usr/bin/env bash
# Initialization script for the Omniscience MCP Server

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "🤖 Initializing Project Omniscience..."
echo "📦 Syncing dependencies..."
uv sync --quiet

echo "🧠 Pre-loading Voyage-4-nano model (this may take a moment on first run)..."
uv run python -c "
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
import warnings
warnings.filterwarnings('ignore')
from sentence_transformers import SentenceTransformer
# This triggers the download and caching if not already present
SentenceTransformer('voyageai/voyage-4-nano', trust_remote_code=True)
" 2>/dev/null

echo "✅ Model loaded successfully!"
echo ""
echo "=========================================================="
echo "🚀 MCP INTEGRATION INSTRUCTIONS"
echo "=========================================================="
echo "Copy and paste the relevant configuration into your client."
echo ""
echo "📝 1. Antigravity IDE"
echo "Add this to your ~/.gemini/config/mcp_config.json:"
echo '{'
echo '  "mcpServers": {'
echo '    "omniscience": {'
echo '      "command": "'$DIR'/run_server.sh"'
echo '    }'
echo '  }'
echo '}'
echo ""
echo "📝 2. Claude Desktop / Claude Code"
echo "Add this to your claude_desktop_config.json:"
echo '{'
echo '  "mcpServers": {'
echo '    "omniscience": {'
echo '      "command": "'$DIR'/run_server.sh"'
echo '    }'
echo '  }'
echo '}'
echo ""
echo "📝 3. Cursor"
echo "Go to Settings -> Features -> MCP Servers -> Add New"
echo "Name: omniscience"
echo "Type: command"
echo "Command: $DIR/run_server.sh"
echo "=========================================================="
echo ""
echo "Initialization complete! You can now close this terminal."
