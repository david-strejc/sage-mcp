# SAGE-MCP Testing Suite

Comprehensive testing framework for the SAGE-MCP project, covering all aspects from unit tests to real-world integration scenarios.

## Overview

This testing suite provides thorough validation of:
- **Provider functionality** across OpenAI, Gemini, Anthropic, OpenRouter, and Custom/Ollama
- **File type handling** for text, images, and binary files
- **Folder content processing** with filtering and deduplication  
- **Conversation continuation** and memory management
- **Model restrictions** and cost control
- **End-to-end CLI workflows**
- **Real-world Claude Code integration** scenarios

## Quick Start

### Basic Test Run
```bash
# Run all tests (without API calls)
python tests/run_all_tests.py

# Run with API-dependent tests (requires API keys)
python tests/run_all_tests.py --api-tests

# Verbose output
python tests/run_all_tests.py --verbose --api-tests
```

### Environment Check
```bash
# Check if environment is properly configured
python tests/run_all_tests.py --env-check
```

### Category-Specific Testing
```bash
# Run specific test categories
python tests/run_all_tests.py --unit                # Unit tests only
python tests/run_all_tests.py --providers          # Provider tests only  
python tests/run_all_tests.py --file-types         # File handling tests only
python tests/run_all_tests.py --integration        # Integration tests only
python tests/run_all_tests.py --e2e                # End-to-end tests only
python tests/run_all_tests.py --real-world         # Real-world scenario tests only
```

## Test Structure

```
tests/
├── run_all_tests.py              # Main test runner
├── unit/                          # Unit tests
│   ├── test_conversation_continuation.py
│   └── test_model_restrictions.py
├── providers/                     # Provider-specific tests
│   ├── test_openai_provider.py
│   ├── test_gemini_provider.py
│   ├── test_anthropic_provider.py
│   ├── test_openrouter_provider.py
│   └── test_custom_provider.py
├── file_types/                    # File handling tests
│   ├── test_text_files.py
│   ├── test_binary_files.py
│   └── test_image_handling.py
├── integration/                   # Integration tests
│   └── test_folder_content.py
├── e2e/                          # End-to-end tests
│   └── test_cli_interface.py
└── real_world/                   # Real-world scenarios
    └── test_claude_code_integration.py
```

## Test Categories

### 1. Unit Tests
**Location**: `tests/unit/`

Tests core functionality in isolation:
- **Conversation Continuation** (`test_conversation_continuation.py`)
  - Thread creation and management
  - Turn addition and retrieval
  - Cross-tool conversation memory
  - File deduplication across turns
  - Memory persistence and isolation

- **Model Restrictions** (`test_model_restrictions.py`)
  - Provider-specific model filtering
  - Pattern-based model blocking
  - Cost control through restrictions
  - Environment-specific configurations
  - Integration with model selection

### 2. Provider Tests  
**Location**: `tests/providers/`
**Requires**: API keys (`--api-tests` flag)

Tests each AI provider integration:

#### OpenAI Provider (`test_openai_provider.py`)
- GPT model completions
- o1/o3 reasoning models (special handling)
- Image support with GPT-4o
- Model restrictions validation
- Streaming support
- Error handling

#### Gemini Provider (`test_gemini_provider.py`)  
- Gemini 2.0 Flash and Pro models
- Thinking mode support
- Vision capabilities
- Large context window handling
- JSON mode support
- Model-specific limits

#### Anthropic Provider (`test_anthropic_provider.py`)
- Claude 3.5 Sonnet and Haiku models
- Vision capabilities
- System prompt handling
- Multi-turn conversations
- Large context processing
- Temperature variations

#### OpenRouter Provider (`test_openrouter_provider.py`)
- Model routing capabilities
- Free and premium model access
- Rate limiting handling
- Model aliases
- Conversation context
- System prompt support

#### Custom/Ollama Provider (`test_custom_provider.py`)
- Local model inference
- Ollama connectivity
- Model listing
- Temperature settings
- Performance timing
- Custom endpoint configuration

### 3. File Type Tests
**Location**: `tests/file_types/`

Tests file handling across different formats:

#### Text Files (`test_text_files.py`)
- Multiple programming languages (Python, JavaScript, TypeScript)
- Configuration formats (JSON, YAML, CSV, XML)
- Documentation (Markdown)
- UTF-8 encoding and special characters
- Large file handling
- File summary and reference modes
- Multi-file analysis

#### Image Handling (`test_image_handling.py`)
- Provider-specific image support
- Multiple formats (PNG, JPEG, WebP)
- Size limit validation
- Base64 data URL handling
- Concurrent image processing
- Provider-specific size limits
- Error handling for invalid images

#### Binary Files (`test_binary_files.py`)
- Binary file detection
- File signature validation
- Security filtering
- Extension-based blocking
- Mixed content handling
- Large binary file rejection

### 4. Integration Tests
**Location**: `tests/integration/`

Tests component interaction:

#### Folder Content (`test_folder_content.py`)
- Directory traversal and expansion
- File filtering by extension
- Excluded directory handling  
- Nested folder processing
- Large folder management
- Token budget allocation
- Multi-file deduplication
- Project structure analysis

### 5. End-to-End Tests
**Location**: `tests/e2e/`

Tests complete workflows:

#### CLI Interface (`test_cli_interface.py`)
- Command-line argument parsing
- Help and version output
- File input processing
- MCP server startup
- Tool listing and execution
- Environment validation
- Import verification
- Complete workflow testing

### 6. Real-World Scenarios
**Location**: `tests/real_world/`
**Requires**: API keys (`--api-tests` flag)

Tests realistic usage patterns:

#### Claude Code Integration (`test_claude_code_integration.py`)
- MCP configuration validation
- Bug report analysis
- Feature specification planning
- Code review workflows
- Performance analysis
- Multi-file scenarios
- Error handling
- Development workflows
- Debugging workflows
- Refactoring workflows

## Environment Setup

### Required Environment Variables

#### API Keys (for `--api-tests`)
```bash
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENROUTER_API_KEY="your-openrouter-key"
export CUSTOM_API_URL="http://localhost:11434"  # For Ollama
```

#### Model Restrictions (optional)
```bash
export OPENAI_ALLOWED_MODELS="gpt-4o,o1-mini"
export GOOGLE_ALLOWED_MODELS="gemini-2.0-flash,gemini-1.5-pro"
export ANTHROPIC_ALLOWED_MODELS="claude-3-5-sonnet-20241022"
export BLOCKED_MODELS="expensive-model-1,dangerous-model-2"
export DISABLED_MODEL_PATTERNS="old,deprecated,mini"
```

### Dependencies
```bash
pip install pytest pytest-asyncio pillow requests
```

### Optional: Ollama Setup
For local model testing:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull a model
ollama pull llama3.2
```

## Individual Test Execution

### Run Specific Test Files
```bash
# Unit tests
python tests/unit/test_conversation_continuation.py
python tests/unit/test_model_restrictions.py

# Provider tests (requires API keys)
python tests/providers/test_openai_provider.py --test basic_text_completion
python tests/providers/test_gemini_provider.py --verbose
python tests/providers/test_custom_provider.py --check-ollama

# File type tests
python tests/file_types/test_text_files.py --create-only  # Create test files
python tests/file_types/test_image_handling.py --verbose
python tests/file_types/test_binary_files.py

# Integration tests
python tests/integration/test_folder_content.py --test project_structure_created

# E2E tests
python tests/e2e/test_cli_interface.py --test cli_help
python tests/e2e/test_cli_interface.py --e2e  # E2E tests only

# Real-world tests (requires API keys)
python tests/real_world/test_claude_code_integration.py --scenarios
python tests/real_world/test_claude_code_integration.py --workflows
```

### Run with pytest directly
```bash
# Run specific test methods
pytest tests/unit/test_conversation_continuation.py::TestConversationContinuation::test_thread_creation -v

# Run with custom markers
pytest tests/providers/ -m "not slow" -v

# Generate coverage report
pytest tests/ --cov=. --cov-report=html
```

## Test Output and Reporting

### Standard Output
The test runner provides:
- Environment validation
- Progress indicators
- Pass/fail counts per category
- Error summaries
- Performance timing

### JSON Report
```bash
# Generate detailed JSON report
python tests/run_all_tests.py --api-tests --report test_results.json
```

The report includes:
- Test execution timestamps
- Environment configuration
- Detailed results per category
- Error details
- Summary statistics

### Example Output
```
============================================================
                    Environment Check                    
============================================================
API Key Status:
  OpenAI      : ✓ Available
  Gemini      : ✓ Available
  Anthropic   : ❌ Not set
  OpenRouter  : ❌ Not set
  Custom      : ✓ Available

✓ 3 providers configured: OpenAI, Gemini, Custom

============================================================
                      Unit Tests                        
============================================================

----------------------------------------
Running Conversation Continuation
----------------------------------------
✓ Conversation Continuation completed successfully

============================================================
                    Test Summary                        
============================================================
Overall Results:
  Total Tests: 47
  Passed:      42 (89.4%)
  Failed:      2 (4.3%)
  Skipped:     3 (6.4%)

Results by Category:
  Unit        :  12P   0F   0S
  Providers   :  15P   1F   2S
  File_types  :   8P   0F   1S
  Integration :   4P   0F   0S
  E2e         :   3P   1F   0S
  Real_world  :   0P   0F   0S

✓ Test execution completed in 127.3 seconds
```

## Best Practices

### For Test Development
1. **Use descriptive test names** that explain what's being tested
2. **Include setup and teardown** methods for clean test isolation
3. **Mock external dependencies** when not testing integration
4. **Use appropriate timeouts** for async operations
5. **Provide meaningful assertions** with helpful error messages

### For Running Tests  
1. **Start with environment check** to ensure proper setup
2. **Run unit tests first** before integration tests
3. **Use `--api-tests` flag** only when you have API keys configured
4. **Run specific categories** during development for faster feedback
5. **Generate reports** for documentation and CI/CD integration

### For CI/CD Integration
```bash
# Basic validation (no API keys required)
python tests/run_all_tests.py --unit --file-types --integration

# Full validation (with API keys)
python tests/run_all_tests.py --api-tests --report ci_results.json
```

## Troubleshooting

### Common Issues

#### "No API keys set" warnings
- **Solution**: Export required API keys or run without `--api-tests`
- **Skip API tests**: Remove `--api-tests` flag for basic functionality testing

#### "MCP server startup failed"  
- **Check**: Ensure `server.py` exists and is executable
- **Verify**: Python path and dependencies are correct
- **Debug**: Run `python server.py` directly to see error messages

#### "Ollama not accessible"
- **Install**: Follow Ollama installation instructions
- **Start**: Run `ollama serve` in background
- **Test**: Check `curl http://localhost:11434/api/tags`

#### "File permission errors"
- **Solution**: Ensure test files are readable
- **Check**: Directory permissions in temp directories

#### "Import errors"
- **Solution**: Ensure project root is in Python path
- **Install**: Missing dependencies with `pip install -r requirements.txt`

### Getting Help
1. **Check environment**: Run `--env-check` first
2. **Use verbose mode**: Add `--verbose` flag for detailed output
3. **Run individual tests**: Isolate failing components
4. **Check logs**: Look at generated error reports
5. **Verify configuration**: Ensure API keys and settings are correct

## Contributing

When adding new tests:
1. **Follow the existing structure** and naming conventions
2. **Add tests to appropriate category** directory
3. **Update this README** with new test descriptions
4. **Include proper error handling** and cleanup
5. **Test both success and failure cases**
6. **Add to the main test runner** if creating new categories

## Performance Considerations

- **Unit tests**: Should complete in seconds
- **Provider tests**: May take 1-2 minutes with API calls
- **Integration tests**: Can take several minutes for large folders
- **E2E tests**: May take 2-5 minutes for complete workflows
- **Real-world tests**: Can take 5-10 minutes with complex scenarios

Total test suite execution time: **5-15 minutes** depending on API availability and system performance.