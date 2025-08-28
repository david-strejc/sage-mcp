"""
Model selection and management utilities
"""

import logging
import re
from typing import Optional, List, Dict, Any

from config import Config

logger = logging.getLogger(__name__)


def list_available_models() -> dict:
    """List all available models from all providers"""
    models = {"available_models": [], "providers": {}}

    # This will be populated by providers/__init__.py when providers are loaded
    # For now, return a basic structure
    return models


def select_best_model(
    mode: str, prompt_size: int, file_count: int = 0, conversation_context: Optional[dict] = None
) -> str:
    """
    Auto-select the best model for the given context

    Model Selection Strategy:
    - o3: Deep reasoning, complex problems, mathematical proofs
    - gpt-5: Advanced reasoning with tool use capabilities
    - gemini-2.5-pro: Long context (2M tokens), complex analysis, thinking mode
    - gemini-2.5-flash: Fast responses, good balance of speed/capability
    - gemini-1.5-pro: Legacy long context model (fallback)
    - gemini-1.5-flash: Quick responses, simple tasks (cheapest)
    """
    config = Config()
    restriction_service = ModelRestrictionService()

    # Calculate estimated tokens (rough estimate)
    estimated_tokens = prompt_size // 4
    if conversation_context:
        estimated_tokens += len(str(conversation_context)) // 4

    # Model capability hints
    MODEL_HINTS = {
        "o3": {
            "modes": ["think", "debug", "analyze"],
            "min_complexity": "high",
            "context_limit": 500000,
            "use_for": "Deep reasoning, mathematical problems, complex debugging",
        },
        "gpt-5": {
            "modes": ["plan", "refactor", "test"],
            "min_complexity": "medium",
            "context_limit": 500000,
            "use_for": "Planning, code generation, testing strategies",
        },
        "gemini-2.5-pro": {
            "modes": ["analyze", "review", "think"],
            "min_complexity": "medium",
            "context_limit": 2000000,
            "use_for": "Long context analysis, deep thinking, comprehensive reviews",
        },
        "gemini-2.5-flash": {
            "modes": ["chat", "debug", "refactor"],
            "min_complexity": "low",
            "context_limit": 1000000,
            "use_for": "Fast responses with good reasoning, general tasks",
        },
        "gemini-1.5-flash": {
            "modes": ["chat"],
            "min_complexity": "minimal",
            "context_limit": 1000000,
            "use_for": "Simple queries, quick responses, basic tasks",
        },
    }

    # Determine task complexity
    complexity = "minimal"
    if file_count > 5 or estimated_tokens > 50000:
        complexity = "high"
    elif file_count > 2 or estimated_tokens > 10000:
        complexity = "medium"
    elif mode in ["think", "analyze", "debug", "review"]:
        complexity = "medium"
    elif estimated_tokens > 2000:
        complexity = "low"

    # Log the selection reasoning
    logger.info(f"Model selection: mode={mode}, tokens={estimated_tokens}, files={file_count}, complexity={complexity}")

    # Select based on mode and complexity
    selected_model = None

    # Priority 1: Check if we need massive context
    if estimated_tokens > 500000:
        selected_model = "gemini-2.5-pro"  # 2M token context
        logger.info(f"Selected {selected_model} for large context ({estimated_tokens} tokens)")

    # Priority 2: Mode-specific selection for high complexity
    elif complexity == "high":
        if mode in ["think", "debug", "analyze"]:
            selected_model = "o3" if restriction_service.is_model_allowed("o3") else "gemini-2.5-pro"
        else:
            selected_model = "gemini-2.5-pro"
        logger.info(f"Selected {selected_model} for high complexity {mode} task")

    # Priority 3: Mode-specific selection for medium complexity
    elif complexity == "medium":
        if mode in ["think", "analyze", "review"]:
            selected_model = "gemini-2.5-pro"
        elif mode in ["plan", "refactor", "test"]:
            selected_model = "gpt-5" if restriction_service.is_model_allowed("gpt-5") else "gemini-2.5-flash"
        else:
            selected_model = "gemini-2.5-flash"
        logger.info(f"Selected {selected_model} for medium complexity {mode} task")

    # Priority 4: Fast responses for simple tasks
    else:
        if mode == "chat" and estimated_tokens < 1000:
            selected_model = "gemini-1.5-flash"  # Cheapest for simple chats
        else:
            selected_model = "gemini-2.5-flash"  # Good balance
        logger.info(f"Selected {selected_model} for simple {mode} task")

    # Verify the selected model is allowed
    if not restriction_service.is_model_allowed(selected_model):
        # Fallback chain
        fallbacks = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        for fallback in fallbacks:
            if restriction_service.is_model_allowed(fallback):
                logger.warning(f"Model {selected_model} not allowed, falling back to {fallback}")
                selected_model = fallback
                break

    return selected_model


def get_model_hints() -> dict:
    """Get model capability hints for display"""
    return {
        "o3": "🧠 Deep reasoning, complex problems, mathematical proofs (OpenAI)",
        "gpt-5": "🔧 Advanced reasoning with tool use, planning, code generation (OpenAI)",
        "gemini-2.5-pro": "📚 Long context (2M), deep thinking, comprehensive analysis (Google)",
        "gemini-2.5-flash": "⚡ Fast with good reasoning, balanced performance (Google)",
        "gemini-1.5-pro": "📖 Legacy long context, stable performance (Google)",
        "gemini-1.5-flash": "🏃 Quick responses, simple tasks, cheapest option (Google)",
    }


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
            # Use word boundary regex to avoid partial matches like "mini" in "gemini"
            if re.search(r"\b" + re.escape(pattern) + r"\b", model_lower):
                logger.debug(f"Model {model_name} matches disabled pattern: {pattern}")
                return False

        # Check provider-specific restrictions
        if model_lower.startswith(("gpt", "o1", "o3", "text-")):
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
            "disabled_patterns": self.disabled_patterns,
        }
