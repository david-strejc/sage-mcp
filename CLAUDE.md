# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SAGE-MCP is a sophisticated MCP (Model Context Protocol) server that transforms Claude into a multi-talented development assistant. It features intelligent mode selection, conversation continuity, and smart file handling across multiple AI providers.

## Development Commands

### Setup and Installation
```bash
# Setup with virtual environment
./setup.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Server
```bash
# MCP Server (primary interface)
python server.py

# CLI Interface (for testing)
./cli.py chat "Hello, SAGE!"
```

### Quality Checks and Linting
```bash
# Run all quality checks (format, lint, type check, test)
./scripts/quality_check.sh

# Individual tools
black . --line-length 120
ruff check . --fix
mypy . --ignore-missing-imports --no-error-summary
```

### Testing
```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test categories
python tests/run_all_tests.py --unit
python tests/run_all_tests.py --providers --api-tests
python tests/run_all_tests.py --integration

# Environment check
python tests/run_all_tests.py --env-check
```

## Architecture

### Core Components

The codebase follows a modular architecture with clear separation of concerns:

- **`server.py`** - FastMCP server entry point with tool registration
- **`tools/sage.py`** - Universal SAGE tool with conversation continuation
- **`modes/`** - Specialized AI modes (chat, analyze, review, debug, plan, test, refactor, think)
- **`providers/`** - AI provider integrations (OpenAI, Anthropic, Google, OpenRouter, Custom/Ollama)
- **`models/manager.py`** - Intelligent model selection and capabilities management
- **`utils/`** - Core utilities (files, memory, security, tokens, model restrictions)

### Multi-Mode System

Each mode has optimized temperature settings and specialized behavior:

| Mode | Temperature | Purpose |
|------|------------|---------|
| chat | 0.7 | Creative discussion and Q&A |
| analyze | 0.3 | Focused code analysis |
| review | 0.3 | Systematic code review |
| debug | 0.2 | Precise debugging |
| plan | 0.5 | Strategic planning |
| test | 0.4 | Test generation |
| refactor | 0.4 | Code improvement |
| think | 0.8 | Deep reasoning with adjustable thinking depth |

### Conversation Continuity

The system maintains conversation context across tool calls using a thread-based memory system in `utils/memory.py`. Files are automatically deduplicated to avoid re-reading the same content.

### File Handling Modes

Three intelligent file handling strategies:
- **embedded** - Full file content in context (default)
- **summary** - Token-efficient summaries for large codebases  
- **reference** - File storage with ID references for iterative work

## Configuration

### Environment Variables

Key environment variables for development:

```bash
# Provider API Keys
OPENAI_API_KEY="your-key"
ANTHROPIC_API_KEY="your-key" 
GOOGLE_API_KEY="your-key"
OPENROUTER_API_KEY="your-key"

# Model Selection
DEFAULT_MODEL="auto"           # or specific model
DEFAULT_PROVIDER="auto"        # or specific provider
FALLBACK_MODEL="gpt-4o-mini"

# Model Restrictions (cost control)
ALLOWED_MODELS="gpt-4o,gpt-4o-mini,claude-3-5-sonnet"
DISALLOWED_MODELS="o1-preview,o1"  # Expensive models to exclude

# Feature Flags
WEBSEARCH_ENABLED="true"
FILE_SECURITY_CHECK="true"
AUTO_MODEL_SELECTION="true"

# Limits
MAX_FILE_SIZE="10000000"
MCP_PROMPT_SIZE_LIMIT="50000"
```

### Model Management

Model capabilities and restrictions are managed via:
- `models/config.yaml` - Model capabilities and token limits
- `utils/models.py` - Model restriction service
- Environment variables for runtime restrictions

## Key Implementation Patterns

### Provider Integration

All providers implement the `BaseProvider` interface in `providers/base.py`:

```python
class BaseProvider:
    async def generate(self, messages, **kwargs):
        # Provider-specific implementation
        pass
```

### Mode Handlers

All modes extend `BaseMode` in `modes/base.py` with standardized:
- Input validation
- Temperature management  
- Model selection
- Response formatting

### Security

File access is validated through `utils/security.py`:
- Path validation and sanitization
- Binary file detection
- Size limit enforcement
- Security scanning for malicious patterns

### Memory Management

Conversation continuity is handled via `utils/memory.py`:
- Thread-based conversation tracking
- Automatic file deduplication
- Context preservation across tool calls

## Development Guidelines

### Adding New Modes

1. Create mode handler in `modes/` extending `BaseMode`
2. Add temperature setting in `config.py`
3. Register in `modes/__init__.py`
4. Add tests in `tests/unit/`

### Adding New Providers

1. Create provider in `providers/` implementing `BaseProvider`
2. Add model configurations in `models/config.yaml`
3. Register in `providers/__init__.py`  
4. Add provider tests in `tests/providers/`

### Testing Strategy

The comprehensive test suite covers:
- Unit tests for core functionality
- Provider tests (API-dependent, use `--api-tests`)
- Integration tests for file handling
- E2E tests for CLI interface
- Real-world scenario tests

Run quality checks before committing:
```bash
./scripts/quality_check.sh
```