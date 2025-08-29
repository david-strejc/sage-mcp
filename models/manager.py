"""
Model Manager - Centralized model configuration and selection
"""

import logging
import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model configurations and intelligent selection"""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize with configuration file"""
        if config_file is None:
            config_file = Path(__file__).parent / "config.yaml"

        self.config_file = config_file
        self.config = self._load_config()
        self.models = self.config.get("models", {})
        self.selection_rules = self.config.get("selection_rules", {})
        self.providers = self.config.get("providers", {})

    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load model config: {e}")
            return {}

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific model"""
        return self.models.get(model_name)

    def get_all_models(self) -> List[str]:
        """Get list of all configured models"""
        return list(self.models.keys())

    def get_models_by_provider(self, provider: str) -> List[str]:
        """Get models for a specific provider"""
        return [model_name for model_name, config in self.models.items() if config.get("provider") == provider]

    def get_provider_for_model(self, model_name: str) -> Optional[str]:
        """Get provider name for a model"""
        config = self.get_model_config(model_name)
        return config.get("provider") if config else None
    
    def get_api_parameters(self, model_name: str) -> Dict[str, Any]:
        """Get model-specific API parameters"""
        config = self.get_model_config(model_name)
        if config and "api_parameters" in config:
            return config["api_parameters"]
        return {}  # Return empty dict if no special parameters

    def get_model_hint(self, model_name: str) -> str:
        """Get formatted hint for a model"""
        config = self.get_model_config(model_name)
        if not config:
            return f"{model_name}: No description available"

        emoji = config.get("emoji", "")
        name = config.get("display_name", model_name)
        context = config["capabilities"].get("context_limit", 0)
        speed = config["capabilities"].get("speed", "unknown")
        cost = config["capabilities"].get("cost", "unknown")
        hint = config.get("hint", "")

        # Format context for display
        if context >= 1000000:
            context_str = f"{context // 1000000}M"
        elif context >= 1000:
            context_str = f"{context // 1000}K"
        else:
            context_str = str(context)

        # IMPORTANT: Show the actual model name that should be used
        return f"{emoji} {model_name}: {hint} ({context_str} context, {speed} speed, {cost} cost)"

    def get_tool_description_hints(self, available_models: Optional[List[str]] = None) -> str:
        """Get formatted hints for tool description based on actually available models"""
        # If no available models list provided, use all configured models
        if available_models is None:
            available_models = list(self.models.keys())
        
        # Create compact hints for each model
        model_descriptions = []
        for model_name in sorted(available_models):
            if model_name not in self.models:
                continue  # Skip models not in our config
                
            config = self.models[model_name]
            emoji = config.get("emoji", "")
            hint_text = config.get("hint", "")
            context = config["capabilities"].get("context_limit", 0)
            
            # Format context for display
            if context >= 1000000:
                context_str = f"{context // 1000000}M"
            elif context >= 1000:
                context_str = f"{context // 1000}K"
            else:
                context_str = str(context)
            
            # Compact format for better JSON display
            model_descriptions.append(f"{emoji} {model_name} ({context_str}): {hint_text}")
        
        # Create concise description
        if model_descriptions:
            description = "Available models:\n" + "\n".join(model_descriptions)
            description += f"\n\nUse EXACT names: {', '.join(sorted(available_models))}"
        else:
            description = "No models available. Check API keys."
        
        return description

    def select_model_for_task(
        self,
        mode: str,
        prompt_size: int,
        file_count: int = 0,
        conversation_context: Optional[dict] = None,
        allowed_models: Optional[List[str]] = None,
    ) -> Tuple[str, str]:
        """
        Select best model for a task

        Returns:
            Tuple of (model_name, reasoning)
        """
        # Calculate estimated tokens
        estimated_tokens = prompt_size // 4
        if conversation_context:
            estimated_tokens += len(str(conversation_context)) // 4

        # Determine complexity
        complexity = self._determine_complexity(mode, estimated_tokens, file_count)

        # Filter models by allowed list
        if allowed_models:
            available_models = [m for m in self.models.keys() if m in allowed_models]
        else:
            available_models = list(self.models.keys())

        if not available_models:
            return "gemini-1.5-flash", "No allowed models available, using default"

        # Score each model
        model_scores = {}
        for model_name in available_models:
            score = self._score_model(model_name, mode, complexity, estimated_tokens)
            model_scores[model_name] = score

        # Sort by score (higher is better)
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)

        if sorted_models:
            selected = sorted_models[0][0]
            reasoning = self._generate_selection_reasoning(selected, mode, complexity, estimated_tokens, file_count)
            logger.info(f"Model selection: {selected} - {reasoning}")
            return selected, reasoning

        return "gemini-1.5-flash", "Fallback to default model"

    def _determine_complexity(self, mode: str, tokens: int, files: int) -> str:
        """Determine task complexity"""
        rules = self.selection_rules.get("complexity_indicators", {})

        # Check high complexity indicators
        high = rules.get("high", {})
        if (
            files >= high.get("file_count", 5)
            or tokens >= high.get("token_count", 50000)
            or mode in ["think", "analyze"]
        ):
            return "high"

        # Check medium complexity
        medium = rules.get("medium", {})
        if (
            files >= medium.get("file_count", 2)
            or tokens >= medium.get("token_count", 10000)
            or mode in ["debug", "review", "plan", "refactor", "test"]
        ):
            return "medium"

        return "low"

    def _score_model(self, model_name: str, mode: str, complexity: str, tokens: int) -> float:
        """Score a model for a specific task"""
        config = self.models.get(model_name, {})
        score = 0.0

        # Mode preference scoring
        if mode in config.get("modes", {}).get("preferred", []):
            score += 3.0
        elif mode in config.get("modes", {}).get("suitable", []):
            score += 1.0

        # Complexity matching
        model_complexity = config.get("complexity", {})
        if complexity == model_complexity.get("optimal"):
            score += 2.0
        elif complexity >= model_complexity.get("min", "low"):
            score += 1.0

        # Context capacity check
        context_limit = config.get("capabilities", {}).get("context_limit", 100000)
        if tokens > context_limit:
            score -= 5.0  # Penalize if can't handle context
        elif tokens < context_limit * 0.1:
            # Using a powerful model for tiny context is wasteful
            if config.get("capabilities", {}).get("cost") == "very_high":
                score -= 1.0

        # Selection priority (lower number = higher priority)
        priority = config.get("selection_priority", 5)
        score += (10 - priority) * 0.5

        # Speed preference for simple tasks
        if complexity == "low" and config.get("capabilities", {}).get("speed") == "very_fast":
            score += 1.0

        return score

    def _generate_selection_reasoning(self, model: str, mode: str, complexity: str, tokens: int, files: int) -> str:
        """Generate human-readable reasoning for model selection"""
        parts = [f"mode={mode}", f"complexity={complexity}", f"tokens={tokens}", f"files={files}"]

        config = self.models.get(model, {})
        if mode in config.get("modes", {}).get("preferred", []):
            parts.append("preferred for mode")

        if tokens > 100000:
            parts.append("large context")

        return f"Selected for: {', '.join(parts)}"

    def get_model_enum_with_descriptions(self) -> List[Dict[str, str]]:
        """Get model enum values with descriptions for schema"""
        result = []
        for model_name, config in self.models.items():
            emoji = config.get("emoji", "")
            hint = config.get("hint", "")
            context = config["capabilities"].get("context_limit", 0)

            # Format context
            if context >= 1000000:
                context_str = f"{context // 1000000}M tokens"
            else:
                context_str = f"{context // 1000}K tokens"

            result.append({"value": model_name, "description": f"{emoji} {model_name}: {hint} ({context_str})"})

        return result
