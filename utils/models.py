"""
Model selection and management utilities
"""

import logging
from typing import Optional, List, Dict, Any

from config import Config

logger = logging.getLogger(__name__)

def list_available_models() -> dict:
    """List all available models from all providers"""
    models = {
        "available_models": [],
        "providers": {}
    }
    
    # This will be populated by providers/__init__.py when providers are loaded
    # For now, return a basic structure
    return models

def select_best_model(
    mode: str,
    prompt_size: int,
    file_count: int = 0,
    conversation_context: Optional[dict] = None
) -> str:
    """
    Auto-select the best model for the given context
    
    Args:
        mode: Operation mode
        prompt_size: Size of prompt in characters
        file_count: Number of files included
        conversation_context: Conversation context
        
    Returns:
        Best model name
    """
    config = Config()
    
    # Calculate estimated tokens (rough estimate)
    estimated_tokens = prompt_size // 4
    if conversation_context:
        estimated_tokens += len(str(conversation_context)) // 4
    
    # For now, return a sensible default
    # This will be enhanced when providers are implemented
    if estimated_tokens > 100000:
        # Large context needed
        return "gemini-1.5-pro"
    elif mode == "think":
        # Thinking mode prefers specialized models
        return "gemini-2.0-flash-thinking-exp"
    elif mode in ["analyze", "review", "debug"]:
        # Analytical modes
        return "gemini-2.0-flash-exp"
    else:
        # Default for chat and other modes
        return "gemini-1.5-flash"

def get_model_context_limit(model: str) -> int:
    """Get the context token limit for a model"""
    config = Config()
    
    # Check specific model limits
    for pattern, limit in config.MAX_TOKENS.items():
        if pattern in model:
            return limit
    
    return config.MAX_TOKENS["default"]

class ModelRestrictionService:
    """Enforce model usage restrictions based on environment variables"""
    
    def __init__(self):
        self.load_restrictions()
    
    def load_restrictions(self):
        """Load restrictions from environment variables"""
        from config import Config
        config = Config()
        restrictions = config.get_model_restrictions()
        
        # Provider-specific allowed models
        self.openai_allowed = [m.lower().strip() for m in restrictions["openai_allowed"] if m.strip()]
        self.google_allowed = [m.lower().strip() for m in restrictions["google_allowed"] if m.strip()]
        self.anthropic_allowed = [m.lower().strip() for m in restrictions["anthropic_allowed"] if m.strip()]
        
        # Global blocks
        self.blocked_models = set(m.lower().strip() for m in restrictions["blocked_models"] if m.strip())
        self.disabled_patterns = [p.lower().strip() for p in restrictions["disabled_patterns"] if p.strip()]
        
        if self.blocked_models:
            logger.info(f"Blocked models: {sorted(self.blocked_models)}")
        if self.disabled_patterns:
            logger.info(f"Disabled patterns: {self.disabled_patterns}")
    
    def is_model_allowed(self, model_name: str) -> bool:
        """Check if model is allowed by restrictions"""
        model_lower = model_name.lower()
        
        # Check global blocks first
        if model_lower in self.blocked_models:
            logger.debug(f"Model {model_name} is globally blocked")
            return False
        
        # Check disabled patterns
        for pattern in self.disabled_patterns:
            if pattern in model_lower:
                logger.debug(f"Model {model_name} matches disabled pattern: {pattern}")
                return False
        
        # Check provider-specific restrictions
        if model_lower.startswith(("gpt", "o1", "o3")):
            if self.openai_allowed and model_lower not in self.openai_allowed:
                logger.debug(f"OpenAI model {model_name} not in allowed list")
                return False
                
        elif model_lower.startswith("gemini") or model_lower in ["flash", "pro"]:
            if self.google_allowed and model_lower not in self.google_allowed:
                logger.debug(f"Google model {model_name} not in allowed list")
                return False
                
        elif model_lower.startswith("claude"):
            if self.anthropic_allowed and model_lower not in self.anthropic_allowed:
                logger.debug(f"Anthropic model {model_name} not in allowed list")
                return False
        
        # If we get here, model is allowed
        return True

    def get_restriction_summary(self) -> Dict[str, Any]:
        """Get summary of current restrictions"""
        return {
            "openai_allowed": self.openai_allowed,
            "google_allowed": self.google_allowed,
            "anthropic_allowed": self.anthropic_allowed,
            "blocked_models": list(self.blocked_models),
            "disabled_patterns": self.disabled_patterns
        }