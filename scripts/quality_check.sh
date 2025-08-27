#!/bin/bash
# Quality checks for SAGE MCP

echo "Running quality checks..."

# Format code
echo "Formatting code..."
source venv/bin/activate
black . --line-length 120
ruff check . --fix

# Type checking
echo "Type checking..."
mypy . --ignore-missing-imports --no-error-summary

# Run tests if they exist
if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    echo "Running tests..."
    pytest tests/ -v
fi

echo "✅ All quality checks completed!"