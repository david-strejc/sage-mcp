"""
Model configuration and management system
"""

from .manager import ModelManager

# Singleton instance
_manager = ModelManager()


# Export convenient functions
def get_model_config(model_name: str):
    """Get configuration for a specific model"""
    return _manager.get_model_config(model_name)


def get_all_models():
    """Get list of all configured models"""
    return _manager.get_all_models()


def get_provider_for_model(model_name: str):
    """Get provider name for a model"""
    return _manager.get_provider_for_model(model_name)


def select_model_for_task(
    mode: str, prompt_size: int, file_count: int = 0, conversation_context=None, allowed_models=None
):
    """Select best model for a task"""
    return _manager.select_model_for_task(mode, prompt_size, file_count, conversation_context, allowed_models)


def get_model_hints():
    """Get model hints for display"""
    return {model: _manager.get_model_hint(model) for model in _manager.get_all_models()}


def get_tool_description_hints():
    """Get formatted hints for tool description"""
    return _manager.get_tool_description_hints()


# Export the manager for direct access if needed
manager = _manager

__all__ = [
    "ModelManager",
    "manager",
    "get_model_config",
    "get_all_models",
    "get_provider_for_model",
    "select_model_for_task",
    "get_model_hints",
    "get_tool_description_hints",
]
