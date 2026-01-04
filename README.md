# 🧙 SAGE-MCP: Simple AI Guidance Engine for Claude

[![Version](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/david-strejc/sage-mcp/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Claude](https://img.shields.io/badge/Claude-MCP_Server-purple)](https://claude.ai)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen)](https://www.python.org)

> **Universal AI assistant MCP server with intelligent mode selection, conversation continuity, and smart file handling**

SAGE-MCP transforms Claude into a multi-talented development assistant that adapts to your needs. Whether you're debugging code, planning architecture, writing tests, or having a technical discussion, SAGE automatically selects the right approach and model for optimal results.

## ✨ Key Features

### 🎯 **Intelligent Mode System**
- **chat** - Natural conversations with context awareness
- **analyze** - Deep code analysis and pattern recognition  
- **review** - Comprehensive code reviews with actionable feedback
- **debug** - Systematic debugging and root cause analysis
- **plan** - Strategic project planning and architecture design
- **test** - Test generation with coverage analysis
- **refactor** - Code improvement and modernization
- **think** - Deep reasoning with adjustable thinking depth

### 🔄 **Conversation Continuity**
- Seamless multi-turn conversations across different modes
- Automatic context preservation between tool calls
- Smart file deduplication - never re-read the same files
- Thread-based memory system for long-running tasks

### 🤖 **Smart Model Selection**
- **Auto mode** - Intelligent model selection based on task complexity
- Support for multiple providers: OpenAI, Anthropic, Google, OpenRouter
- Model restrictions via environment variables for cost control
- Thinking depth control: minimal (0.5%), low (8%), medium (33%), high (67%), max (100%)

### 📁 **Intelligent File Handling**
- **embedded** - Full file content in context (default)
- **summary** - Token-efficient summaries for large codebases
- **reference** - File storage with ID references
- **output_file** - Save output directly to disk (no context pollution)
- Automatic directory expansion and smart deduplication
- Security validation for all file operations

### 🌐 **Web Search Integration**
- Real-time documentation lookup
- Best practices and current standards
- Framework and library research
- Error and issue investigation

## 🎨 Mode Specializations

| Mode | Temperature | Description | Best For |
|------|------------|-------------|----------|
| **chat** | 0.5 | Natural conversations with balanced creativity | Q&A, brainstorming, explanations |
| **analyze** | 0.2 | Focused precision for code analysis | Architecture review, pattern detection |
| **review** | 0.3 | Systematic evaluation with consistent standards | Security audits, best practices |
| **debug** | 0.1 | Deterministic analysis for troubleshooting | Error investigation, root cause analysis |
| **plan** | 0.4 | Strategic thinking for project planning | Architecture design, task breakdown |
| **test** | 0.2 | Accurate test generation with edge cases | Unit tests, integration tests |
| **refactor** | 0.3 | Careful improvements preserving functionality | Code modernization, optimization |
| **think** | 0.7 | Creative problem solving with deep reasoning | Complex algorithms, system design |

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/david-strejc/sage-mcp
cd sage-mcp

# Install dependencies
pip install -r requirements.txt

# Configure your API keys
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"
export OPENROUTER_API_KEY="your-key-here"
```

### Claude Desktop Configuration

Add to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "sage": {
      "command": "python",
      "args": ["/path/to/sage-mcp/server.py"],
      "env": {
        "OPENAI_API_KEY": "your-key",
        "ANTHROPIC_API_KEY": "your-key",
        "DEFAULT_MODEL": "gpt-4o",
        "DEFAULT_PROVIDER": "openai"
      }
    }
  }
}
```

## 📖 Usage Examples

### Basic Chat
```typescript
// In Claude:
Use sage tool to explain how async/await works in Python
```

### Code Analysis with Files
```typescript
// Analyze specific files
Use sage tool in analyze mode to review the architecture of ./src/api/

// With model selection
Use sage with model gpt-4o to analyze performance bottlenecks in server.py
```

### Multi-turn Conversations
```typescript
// First turn
Use sage to help me design a caching system

// Continue the conversation (Claude will auto-continue)
Now let's implement the LRU cache we discussed

// Files are automatically deduplicated across turns
```

### Deep Thinking Mode
```typescript
// For complex problems requiring deep reasoning
Use sage in think mode with thinking_mode="high" to solve this algorithmic challenge: [problem description]
```

### Smart File Handling
```typescript
// Token-efficient mode for large codebases
Use sage with file_handling_mode="summary" to review the entire project structure

// Reference mode for iterative work
Use sage with file_handling_mode="reference" to start refactoring the database layer
```

## ⚙️ Configuration

### Environment Variables

```bash
# Provider Configuration
DEFAULT_PROVIDER=openai          # Default: auto
DEFAULT_MODEL=gpt-4o            # Default: auto
FALLBACK_MODEL=gpt-4o-mini      # Fallback for errors

# Model Restrictions (optional)
ALLOWED_MODELS=gpt-4o,gpt-4o-mini,claude-3-5-sonnet
DISALLOWED_MODELS=o1-preview,o1  # Expensive models to exclude

# Feature Flags
WEBSEARCH_ENABLED=true          # Enable web search
FILE_SECURITY_CHECK=true        # Validate file paths
AUTO_MODEL_SELECTION=true       # Smart model selection

# Token Limits
MAX_TOKENS_GPT4O=128000
MAX_TOKENS_CLAUDE=200000
MAX_THINKING_TOKENS_O1=100000
```

### Mode-Specific Temperatures

Default temperatures optimized for each mode:
- **chat**: 0.5 - Balanced creativity
- **analyze**: 0.2 - Focused precision
- **review**: 0.3 - Systematic evaluation
- **debug**: 0.1 - Deterministic analysis
- **plan**: 0.4 - Strategic thinking
- **test**: 0.2 - Accurate test generation
- **refactor**: 0.3 - Careful improvements
- **think**: 0.7 - Creative problem solving

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

### Save Output to File

For large outputs that would pollute context, save directly to disk:

```python
# Save analysis directly to file instead of returning in response
sage(mode="analyze",
     files=["/src"],
     prompt="Full codebase analysis",
     output_file="/tmp/analysis.md")
# Returns: "Output saved to /tmp/analysis.md (15.2KB)"

# Great for:
# - Large code reviews
# - Documentation generation
# - Analysis reports
# - Any output you want to process later
```

Features:
- Creates parent directories automatically
- Prevents accidental overwrites (file must not exist)
- Blocks writes to system directories
- Returns human-readable file size confirmation

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

### Supported Models

| Provider | Models | Configuration |
|----------|--------|---------------|
| **OpenAI** | gpt-4o, gpt-4o-mini, o1, o3-mini | OPENAI_API_KEY |
| **Anthropic** | claude-3-5-sonnet, claude-3-5-haiku | ANTHROPIC_API_KEY |
| **Google** | gemini-2.0-flash-exp, gemini-1.5-pro | GOOGLE_API_KEY |
| **OpenRouter** | 100+ models from all providers | OPENROUTER_API_KEY |
| **Custom/Ollama** | llama3.2, mistral, codestral | CUSTOM_API_URL |

### Complete Configuration Reference

| Variable | Description | Example |
|----------|-------------|---------|
| **API Keys** | | |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | `sk-ant-...` |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `OPENROUTER_API_KEY` | OpenRouter API key | `sk-or-...` |
| `XAI_API_KEY` | xAI (Grok) API key | `xai-...` |
| `CUSTOM_API_URL` | Custom/Ollama API endpoint | `http://localhost:11434` |
| `CUSTOM_API_KEY` | Custom API key (if required) | `custom-key` |
| **Model Selection** | | |
| `DEFAULT_MODEL` | Default model (`auto` for selection) | `o3`, `gpt-5`, `auto` |
| **Model Restrictions** | | |
| `OPENAI_ALLOWED_MODELS` | Allowed OpenAI models | `o3,gpt-5` |
| `GOOGLE_ALLOWED_MODELS` | Allowed Google models | `gemini-2.5-pro,gemini-2.5-flash` |
| `ANTHROPIC_ALLOWED_MODELS` | Allowed Anthropic models | `claude-3-5-sonnet` |
| `BLOCKED_MODELS` | Blocked models (any provider) | `gpt-4,o3-mini` |
| `DISABLED_MODEL_PATTERNS` | Disable by pattern | `anthropic,claude,mini` |
| **Limits & Performance** | | |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `5242880` (5MB) |
| `MCP_PROMPT_SIZE_LIMIT` | MCP transport limit | `50000` |
| `MAX_CONVERSATION_TURNS` | Max turns per conversation | `20` |
| `CONVERSATION_TIMEOUT_HOURS` | Conversation timeout | `3` |
| **Memory & Storage** | | |
| `REDIS_URL` | Redis connection for memory | `redis://localhost:6379/0` |
| `REDIS_DB` | Redis database number | `0` |
| **Temperature Overrides** | | |
| `TEMPERATURE_CHAT` | Chat mode temperature | `0.7` |
| `TEMPERATURE_ANALYZE` | Analyze mode temperature | `0.3` |
| `TEMPERATURE_DEBUG` | Debug mode temperature | `0.2` |
| `TEMPERATURE_PLAN` | Plan mode temperature | `0.4` |
| `TEMPERATURE_TEST` | Test mode temperature | `0.3` |
| `TEMPERATURE_REFACTOR` | Refactor mode temperature | `0.4` |
| `TEMPERATURE_REVIEW` | Review mode temperature | `0.5` |
| `TEMPERATURE_THINK` | Think mode temperature | `0.8` |


## 🏗️ Architecture

```
sage-mcp/
├── server.py           # FastMCP server entry point
├── config.py           # Configuration management
├── tools/
│   └── sage.py        # Universal SAGE tool
├── modes/             # Specialized AI modes
│   ├── base.py        # Base mode handler
│   ├── chat.py        # Conversational mode
│   ├── analyze.py     # Code analysis mode
│   ├── debug.py       # Debugging mode
│   └── ...
├── providers/         # AI provider integrations
│   ├── openai.py
│   ├── anthropic.py
│   ├── gemini.py
│   └── openrouter.py
├── models/           # Model management
│   ├── manager.py    # Intelligent model selection
│   └── config.yaml   # Model capabilities
└── utils/            # Utilities
    ├── files.py      # File handling
    ├── memory.py     # Conversation memory
    ├── models.py     # Model restrictions
    └── security.py   # Security validation
```

## 🧪 Advanced Features

### Model Restrictions
Control which models can be used to manage costs:

```bash
# Allow only specific models
export ALLOWED_MODELS="gpt-4o-mini,claude-3-haiku"

# Exclude expensive models
export DISALLOWED_MODELS="o1-preview,claude-3-opus"
```

### Conversation Memory
SAGE maintains conversation context across tool calls:

```python
# Automatically continues conversations
# Previous context and files are preserved
# Smart deduplication prevents re-reading
```

### Custom Providers
Add custom AI providers by implementing the base provider interface:

```python
class CustomProvider(BaseProvider):
    async def generate(self, messages, **kwargs):
        # Your implementation
        pass
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
ruff check .
```



## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built on [FastMCP](https://github.com/jlowin/fastmcp) framework
- Inspired by [zen-mcp-server](https://github.com/punkpeye/zen-mcp-server)
- Powered by Claude MCP protocol

## 🔗 Links

- [GitHub Repository](https://github.com/david-strejc/sage-mcp)
- [Issue Tracker](https://github.com/david-strejc/sage-mcp/issues)
- [MCP Documentation](https://modelcontextprotocol.io)

---

**SAGE-MCP** - Your intelligent AI assistant that adapts to how you work 🧙✨