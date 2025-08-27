#!/bin/bash

# SAGE MCP Server Setup Script
# One-click installation and configuration

set -e  # Exit on error

echo "🚀 SAGE MCP Server Setup"
echo "========================"

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher required (found $python_version)"
    exit 1
fi
echo "✓ Python $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p logs
mkdir -p scripts

# Create .env from example if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys"
else
    echo "✓ .env file exists"
fi

# Test imports
echo "Testing imports..."
python -c "
import sys
sys.path.insert(0, '.')
from server import SageServer
from tools.sage import SageTool
print('✓ Imports successful')
"

# Update Claude configuration
echo ""
echo "📝 To use SAGE with Claude Desktop:"
echo "Edit: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "Add this to mcpServers:"
echo '
{
  "mcpServers": {
    "sage": {
      "command": "python",
      "args": ["'$(pwd)'/server.py"],
      "env": {
        "PYTHONPATH": "'$(pwd)'"
      }
    }
  }
}
'

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the server manually:"
echo "  source venv/bin/activate"
echo "  python server.py"
echo ""
echo "To use the CLI:"
echo "  ./cli.py chat \"Hello, SAGE!\""