"""
Provider registry and initialization
"""

import logging
from typing import Optional

from config import Config
from providers.base import BaseProvider
from providers.gemini import GeminiProvider
from providers.openai import OpenAIProvider
from providers.anthropic import AnthropicProvider
from providers.openrouter import OpenRouterProvider
from providers.custom import CustomProvider

logger = logging.getLogger(__name__)

# Provider registry
PROVIDERS = {}

def initialize_providers():
    """Initialize all available providers based on API keys"""
    global PROVIDERS
    config = Config()
    api_keys = config.get_api_keys()
    
    # Initialize Gemini
    if api_keys.get("gemini"):
        try:
            provider = GeminiProvider(api_keys["gemini"])
            if provider.validate_api_key():
                PROVIDERS["gemini"] = provider
                logger.info("✓ Gemini provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}")
    
    # Initialize OpenAI
    if api_keys.get("openai"):
        try:
            provider = OpenAIProvider(api_keys["openai"])
            if provider.validate_api_key():
                PROVIDERS["openai"] = provider
                logger.info("✓ OpenAI provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI: {e}")
    
    # Initialize Anthropic
    if api_keys.get("anthropic"):
        try:
            provider = AnthropicProvider(api_keys["anthropic"])
            if provider.validate_api_key():
                PROVIDERS["anthropic"] = provider
                logger.info("✓ Anthropic provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic: {e}")
    
    # Initialize OpenRouter
    if api_keys.get("openrouter"):
        try:
            provider = OpenRouterProvider(api_keys["openrouter"])
            if provider.validate_api_key():
                PROVIDERS["openrouter"] = provider
                logger.info("✓ OpenRouter provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenRouter: {e}")
    
    # Initialize Custom/Ollama
    if api_keys.get("custom_url"):
        try:
            provider = CustomProvider(
                base_url=api_keys["custom_url"],
                api_key=api_keys.get("custom_key", "")
            )
            if provider.validate_api_key():
                PROVIDERS["custom"] = provider
                logger.info("✓ Custom provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Custom: {e}")
    
    if not PROVIDERS:
        logger.warning("No AI providers available! Please set API keys in .env")
    else:
        logger.info(f"Initialized {len(PROVIDERS)} provider(s): {list(PROVIDERS.keys())}")

def get_provider(model: str) -> Optional[BaseProvider]:
    """Get provider for a specific model"""
    
    # Initialize providers if not done
    if not PROVIDERS:
        initialize_providers()
    
    # Model to provider mapping
    if model.startswith("gemini") or model.startswith("models/gemini"):
        return PROVIDERS.get("gemini")
    elif model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
        return PROVIDERS.get("openai")
    elif model.startswith("claude"):
        return PROVIDERS.get("anthropic")
    elif "/" in model:  # OpenRouter format: provider/model
        return PROVIDERS.get("openrouter")
    elif model.startswith("llama") or model.startswith("mixtral"):
        return PROVIDERS.get("custom")  # Ollama/local models
    
    # Try to find any provider that supports this model
    for provider in PROVIDERS.values():
        if model in provider.list_models():
            return provider
    
    return None

def list_available_models() -> dict:
    """List all available models from all providers"""
    if not PROVIDERS:
        initialize_providers()
        
    models = {
        "available_models": [],
        "providers": {}
    }
    
    for name, provider in PROVIDERS.items():
        provider_models = provider.list_models()
        models["providers"][name] = provider_models
        models["available_models"].extend(provider_models)
    
    return models

# Auto-initialize on import
try:
    initialize_providers()
except Exception as e:
    logger.warning(f"Provider auto-initialization failed: {e}")