"""
Central configuration for SAGE MCP
All settings in one place
"""

import os
from pathlib import Path

class Config:
    """Central configuration manager"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # Ensure directories exist
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Model configurations
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "auto")
    
    # Temperature settings per mode
    TEMPERATURES = {
        "chat": 0.7,      # Creative discussion
        "analyze": 0.3,   # Analytical precision
        "review": 0.3,    # Methodical review
        "debug": 0.2,     # Precise debugging
        "plan": 0.5,      # Balanced planning
        "test": 0.4,      # Test generation
        "refactor": 0.4,  # Code improvement
        "think": 0.8      # Creative thinking
    }
    
    # Token limits (model-specific context windows)
    MAX_TOKENS = {
        "gemini-2.0-flash-exp": 1_000_000,
        "gemini-2.0-flash-thinking-exp": 32_768,
        "gemini-1.5-pro": 2_000_000,
        "gemini-1.5-flash": 1_000_000,
        "gpt-4o": 128_000,
        "gpt-4o-mini": 128_000,
        "o1": 200_000,
        "o1-mini": 128_000,
        "o3-mini": 200_000,
        "claude-3.5-sonnet": 200_000,
        "default": 100_000
    }
    
    # MCP protocol limits
    MCP_PROMPT_SIZE_LIMIT = int(os.getenv("MCP_PROMPT_SIZE_LIMIT", "50000"))  # 50K chars for MCP transport
    
    # Conversation settings
    MAX_CONVERSATION_TURNS = int(os.getenv("MAX_CONVERSATION_TURNS", "20"))
    CONVERSATION_TIMEOUT_HOURS = int(os.getenv("CONVERSATION_TIMEOUT_HOURS", "3"))
    
    # Model restrictions for cost/security control
    @classmethod
    def get_model_restrictions(cls) -> dict:
        """Get model restriction patterns"""
        return {
            "openai_allowed": os.getenv("OPENAI_ALLOWED_MODELS", "").split(",") if os.getenv("OPENAI_ALLOWED_MODELS") else [],
            "google_allowed": os.getenv("GOOGLE_ALLOWED_MODELS", "").split(",") if os.getenv("GOOGLE_ALLOWED_MODELS") else [],
            "anthropic_allowed": os.getenv("ANTHROPIC_ALLOWED_MODELS", "").split(",") if os.getenv("ANTHROPIC_ALLOWED_MODELS") else [],
            "blocked_models": os.getenv("BLOCKED_MODELS", "").split(",") if os.getenv("BLOCKED_MODELS") else [],
            "disabled_patterns": os.getenv("DISABLED_MODEL_PATTERNS", "").split(",") if os.getenv("DISABLED_MODEL_PATTERNS") else []
        }
    
    # Mode descriptions for help
    MODE_DESCRIPTIONS = {
        "chat": "General development discussion and Q&A",
        "analyze": "Code and architecture analysis", 
        "review": "Code review for bugs, security, and quality",
        "debug": "Debug issues and find root causes",
        "plan": "Project planning and task breakdown",
        "test": "Generate comprehensive tests",
        "refactor": "Suggest code improvements",
        "think": "Deep reasoning for complex problems"
    }
    
    # Provider API keys (from environment)
    @classmethod
    def get_api_keys(cls) -> dict:
        """Get all configured API keys"""
        return {
            "gemini": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openrouter": os.getenv("OPENROUTER_API_KEY"),
            "custom_url": os.getenv("CUSTOM_API_URL"),
            "custom_key": os.getenv("CUSTOM_API_KEY"),
            "xai": os.getenv("XAI_API_KEY")
        }
    
    # File handling settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10000000"))  # 10MB default
    
    # Security settings
    ALLOWED_FILE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h',
        '.cs', '.rb', '.go', '.rs', '.swift', '.kt', '.php', '.sql',
        '.html', '.css', '.scss', '.json', '.xml', '.yaml', '.yml',
        '.md', '.txt', '.log', '.conf', '.ini', '.toml', '.env', '.csv',
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'  # Image support
    }
    
    EXCLUDED_DIRS = {
        '__pycache__', '.git', '.svn', '.hg', 'node_modules',
        '.venv', 'venv', '.env', 'dist', 'build', '.pytest_cache',
        '.mypy_cache', '.tox', 'coverage_html_report'
    }
    
    # Redis configuration for conversation memory
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))