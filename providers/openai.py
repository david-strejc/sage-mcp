"""
OpenAI AI provider
"""

import os
import logging
from typing import List, Dict, Optional, Any

from openai import AsyncOpenAI
from providers.base import BaseProvider
from models import manager as model_manager

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """OpenAI AI provider"""

    MODELS = [
        # Primary Models - 2025
        "o3",
        "gpt-5",
    ]

    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__(api_key)
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            self.client = None

    async def complete(
        self, model: str, messages: List[Dict[str, str]], temperature: float = 0.5, max_tokens: Optional[int] = None
    ) -> str:
        """Complete using OpenAI with model-specific parameters"""
        if not self.client:
            raise ValueError("OpenAI API key not provided")

        try:
            # Get model-specific API parameters from config
            api_params = model_manager.get_api_parameters(model)
            
            # Handle system messages based on config
            if api_params.get("no_system_messages", False):
                # Convert system messages to user messages for models that don't support them
                converted_messages = []
                for msg in messages:
                    if msg["role"] == "system":
                        converted_messages.append({"role": "user", "content": f"Instructions: {msg['content']}"})
                    else:
                        converted_messages.append(msg)
                messages = converted_messages
            
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
            if "max_completion_tokens" in api_params:
                # Models like o3 use max_completion_tokens
                call_params["max_completion_tokens"] = api_params["max_completion_tokens"]
            elif "max_tokens" in api_params:
                # Standard models use max_tokens
                call_params["max_tokens"] = api_params["max_tokens"]
            elif max_tokens:
                # Use provided max_tokens as fallback
                call_params["max_tokens"] = max_tokens
            else:
                # Default fallback
                call_params["max_tokens"] = 4096

            response = await self.client.chat.completions.create(**call_params)
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI completion error: {e}")
            raise

    def list_models(self) -> List[str]:
        """List available OpenAI models"""
        return self.MODELS

    def validate_api_key(self) -> bool:
        """Check if OpenAI API key is valid"""
        if not self.api_key or not self.client:
            return False

        async def test():
            # Try to list models to validate API key (doesn't require specific model)
            try:
                await self.client.models.list()
                return True
            except Exception:
                # If listing fails, try with gpt-5 which should exist in 2025
                try:
                    await self.client.chat.completions.create(
                        model="gpt-5", messages=[{"role": "user", "content": "test"}], max_tokens=1
                    )
                    return True
                except Exception:
                    return False

        return self._run_async_validation_test(test)
