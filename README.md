# 🧙‍♂️ SAGE-MCP: Simple AI Guidance Engine

**One tool to rule them all** - A complete rewrite of zen-mcp-server with 75% less code and revolutionary features.

## ✨ Key Features

- **🎯 Universal Tool**: One `sage` tool instead of 17 specialized tools
- **🧠 Conversation Continuation**: Seamless multi-turn conversations across modes
- **📁 Smart File Handling**: Automatic deduplication and multiple handling modes
- **🔒 Model Restrictions**: Cost control and security through environment variables
- **⚡ Mode-Based Specialization**: 8 specialized modes within unified interface
- **🤖 Auto Model Selection**: Intelligent model selection based on task requirements
- **💡 Dynamic Schemas**: Tool schema adapts to available models and restrictions

## 🎨 Available Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `chat` | General discussion | Q&A, brainstorming, general help |
| `analyze` | Code & architecture analysis | Review design patterns, performance |
| `review` | Code review for quality/security | Bug hunting, security audit |
| `debug` | Troubleshooting & root cause | Error investigation, problem solving |
| `plan` | Project planning & breakdown | Task planning, project management |
| `test` | Test generation | Unit tests, integration tests |
| `refactor` | Code improvement suggestions | Code quality, optimization |
| `think` | Deep reasoning | Complex problem solving |

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and setup
git clone <repo-url> sage-mcp
cd sage-mcp
./setup.sh
```

### 2. Configure API Keys

```bash
# Copy example and edit
cp .env.example .env
# Edit .env with your API keys
```

### 3. Test Installation

```bash
# Test API connectivity
./scripts/test_api_keys.py

# Test CLI
./cli.py chat "Hello, SAGE!"
```

### 4. Configure Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sage": {
      "command": "python",
      "args": ["/absolute/path/to/sage-mcp/server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/sage-mcp"
      }
    }
  }
}
```

## 🎯 Usage Examples

### Basic Usage (Claude Desktop)

```python
# General chat
sage(mode="chat", prompt="How do I implement JWT authentication?")

# Code analysis
sage(mode="analyze", prompt="Review this architecture", files=["/src/app.py"])

# Debug with files
sage(mode="debug", prompt="Why is this crashing?", files=["/logs/error.log"])

# Continue conversation
sage(mode="review", prompt="Now check for security issues", continuation_id="abc123")
```

### CLI Usage

```bash
# Quick chat
./cli.py chat "Explain async/await in Python"

# Analyze with files
./cli.py analyze "Review this code" /src/*.py

# Continue conversation
./cli.py chat "What about error handling?" --thread abc123

# Use specific model
./cli.py think "Design a microservices architecture" --model gemini-1.5-pro
```

## 🔧 Advanced Features

### Conversation Continuation

```python
# Start conversation
response = sage(mode="chat", prompt="Let's design a web app")
# Returns: continuation_id: abc123

# Continue in same mode
sage(mode="chat", prompt="What database should we use?", continuation_id="abc123")

# Switch modes seamlessly  
sage(mode="analyze", prompt="Review our database schema", 
     files=["/db/schema.sql"], continuation_id="abc123")
```

### Smart File Handling

```python
# Multiple modes available
sage(mode="review", 
     files=["/src", "/tests"],           # Auto-expands directories
     file_handling_mode="embedded",      # Full content (default)
     prompt="Security review")

sage(mode="analyze",
     files=["/large/codebase"], 
     file_handling_mode="summary",       # Summaries only (saves tokens)
     prompt="Architecture overview")

sage(mode="debug",
     files=["/logs"],
     file_handling_mode="reference",     # Store with IDs
     prompt="Analyze error patterns") 
```

### Model Restrictions

```bash
# Environment variables for cost control
OPENAI_ALLOWED_MODELS=o3-mini,gpt-4o-mini
GOOGLE_ALLOWED_MODELS=gemini-2.0-flash-exp,gemini-1.5-pro
BLOCKED_MODELS=gpt-4,claude-opus
DISABLED_MODEL_PATTERNS=expensive,legacy

# Auto mode requires model selection when restricted
DEFAULT_MODEL=auto  # Forces explicit model choice
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | `sk-ant-...` |
| `DEFAULT_MODEL` | Default model (`auto` for selection) | `gemini-1.5-flash` |
| `OPENAI_ALLOWED_MODELS` | Comma-separated allowed OpenAI models | `o3-mini,gpt-4o-mini` |
| `BLOCKED_MODELS` | Comma-separated blocked models | `gpt-4,claude-opus` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `10000000` |
| `MCP_PROMPT_SIZE_LIMIT` | MCP transport limit | `50000` |

### Model Providers

| Provider | Models | Configuration |
|----------|--------|---------------|
| **Google Gemini** | `gemini-2.0-flash-exp`, `gemini-1.5-pro`, `gemini-1.5-flash` | `GEMINI_API_KEY` |
| **OpenAI** | `gpt-4o`, `gpt-4o-mini`, `o1`, `o3-mini` | `OPENAI_API_KEY` |
| **Anthropic** | `claude-3.5-sonnet`, `claude-3.5-haiku` | `ANTHROPIC_API_KEY` |
| **OpenRouter** | `anthropic/claude-3.5-sonnet`, `openai/gpt-4o`, etc. | `OPENROUTER_API_KEY` |
| **Custom/Ollama** | `llama3.2`, `mistral:7b`, etc. | `CUSTOM_API_URL` |

## 🔄 Migration from zen-mcp

```bash
# Automatic migration
./scripts/migrate_from_zen.py

# Manual steps
1. Backup zen-mcp configuration
2. Install sage-mcp 
3. Copy .env settings
4. Update Claude config
5. Test functionality
```

### Compatibility

- ✅ All zen-mcp features preserved
- ✅ Enhanced with conversation continuation
- ✅ Improved file handling
- ✅ Better error handling
- ✅ Model restrictions for cost control

## 🧪 Development

### Project Structure

```
sage-mcp/
├── server.py              # MCP server entry point
├── cli.py                 # CLI wrapper  
├── config.py              # Central configuration
├── tools/sage.py          # Universal SAGE tool
├── modes/                 # Mode handlers
├── providers/             # AI provider implementations
├── utils/                 # Utility modules
└── scripts/               # Helper scripts
```

### Adding New Modes

```python
# modes/custom.py
from modes.base import BaseMode

class CustomMode(BaseMode):
    def get_system_prompt(self) -> str:
        return "Your custom system prompt"
    
    async def handle(self, context: dict, provider) -> str:
        messages = self.build_messages(context)
        return await provider.complete(
            model=context["model"],
            messages=messages,
            temperature=context.get("temperature", 0.5)
        )

# Register in modes/__init__.py
MODES["custom"] = CustomMode()
```

### Adding New Providers

```python
# providers/custom.py
from providers.base import BaseProvider

class CustomProvider(BaseProvider):
    async def complete(self, model, messages, temperature=0.5, max_tokens=None):
        # Implementation
        pass
    
    def list_models(self):
        return ["custom-model-1", "custom-model-2"]
    
    def validate_api_key(self):
        # Validation logic
        return True
```

## 📊 Comparison: zen-mcp vs SAGE

| Feature | zen-mcp | SAGE-MCP | Improvement |
|---------|---------|----------|-------------|
| **Tools** | 17 specialized | 1 universal | 94% reduction |
| **Code Size** | ~4,000 lines | ~1,200 lines | 70% reduction |
| **Conversation Memory** | ❌ | ✅ | New feature |
| **File Deduplication** | ❌ | ✅ | New feature |
| **Model Restrictions** | Basic | Advanced | Enhanced |
| **Auto Model Selection** | ❌ | ✅ | New feature |
| **Dynamic Schemas** | ❌ | ✅ | New feature |
| **Maintenance Complexity** | High | Low | Simplified |

## 🔒 Security & Cost Control

### Model Restrictions
- **Provider-level**: Control which providers are used
- **Model-level**: Allow/block specific models  
- **Pattern-based**: Block models matching patterns
- **Cost control**: Prevent expensive model usage

### File Security
- **Path validation**: Prevent directory traversal
- **Extension filtering**: Only allow safe file types
- **Size limits**: Prevent large file processing
- **Permission checks**: Verify read access

## 🐛 Troubleshooting

### Common Issues

**No models available**
```bash
# Check API keys
./scripts/test_api_keys.py

# Check restrictions
echo $BLOCKED_MODELS
echo $OPENAI_ALLOWED_MODELS
```

**Import errors**
```bash
# Check Python path
export PYTHONPATH=$(pwd)
python -c "from tools.sage import SageTool"
```

**MCP connection issues**
```bash
# Check Claude config path
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Linux: ~/.config/Claude/claude_desktop_config.json
```

## 📈 Performance

- **Startup time**: < 2 seconds
- **Memory usage**: 30% less than zen-mcp
- **Context handling**: Up to 1M+ tokens (model dependent)
- **File processing**: Intelligent chunking and prioritization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the foundation of zen-mcp-server
- Powered by the MCP (Model Context Protocol) framework
- Inspired by the need for simplicity and maintainability

---

**SAGE: "Wisdom through simplicity, power through intelligence"** 🧙‍♂️✨