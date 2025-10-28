"""
DeepSeek AI provider
"""

import os
import logging
from typing import List, Dict, Optional

from openai import AsyncOpenAI
from providers.base import BaseProvider
from models import manager as model_manager

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseProvider):
    """DeepSeek AI provider - uses OpenAI-compatible API"""

    BASE_URL = "https://api.deepseek.com"

    MODELS = [
        "deepseek-reasoner",  # Latest reasoning model (2025)
        "deepseek-chat",  # General purpose chat model
        "deepseek-coder",  # Code-specialized model
    ]

    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        super().__init__(api_key)
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key, base_url=self.BASE_URL)
        else:
            self.client = None

    async def complete(
        self, model: str, messages: List[Dict[str, str]], temperature: float = 0.5, max_tokens: Optional[int] = None
    ) -> str:
        """Complete using DeepSeek with model-specific parameters"""
        if not self.client:
            raise ValueError("DeepSeek API key not provided")

        try:
            # Get model-specific API parameters from config
            api_params = model_manager.get_api_parameters(model)

            # Build API call parameters
            call_params = {
                "model": model,
                "messages": messages,
            }

            # Use configured temperature or override if specified
            if "temperature" in api_params:
                call_params["temperature"] = api_params["temperature"]
            else:
                call_params["temperature"] = temperature

            # Handle max tokens based on model config
            if max_tokens:
                call_params["max_tokens"] = max_tokens
            elif "max_tokens" in api_params:
                call_params["max_tokens"] = api_params["max_tokens"]
            else:
                # Default fallback
                call_params["max_tokens"] = 4096

            response = await self.client.chat.completions.create(**call_params)
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"DeepSeek completion error: {e}")
            raise

    def list_models(self) -> List[str]:
        """List available DeepSeek models"""
        return self.MODELS

    def validate_api_key(self) -> bool:
        """Check if DeepSeek API key is valid"""
        if not self.api_key or not self.client:
            return False

        async def test():
            try:
                # Try a simple completion with deepseek-chat
                await self.client.chat.completions.create(
                    model="deepseek-chat", messages=[{"role": "user", "content": "test"}], max_tokens=1
                )
                return True
            except Exception:
                return False

        return self._run_async_validation_test(test)
