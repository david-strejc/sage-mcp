"""
OpenRouter AI provider (unified access to multiple models)
"""

import os
import logging
from typing import List, Dict, Optional

from openai import AsyncOpenAI
from providers.base import BaseProvider

logger = logging.getLogger(__name__)

class OpenRouterProvider(BaseProvider):
    """OpenRouter AI provider for unified model access"""
    
    MODELS = [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3.5-haiku",
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "google/gemini-pro-1.5",
        "google/gemini-flash-1.5",
        "meta-llama/llama-3.1-405b-instruct",
        "meta-llama/llama-3.1-70b-instruct",
        "mistralai/mistral-7b-instruct",
        "x-ai/grok-beta"
    ]
    
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        super().__init__(api_key)
        if api_key:
            # OpenRouter uses OpenAI-compatible API
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        else:
            self.client = None
    
    async def complete(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: Optional[int] = None
    ) -> str:
        """Complete using OpenRouter"""
        if not self.client:
            raise ValueError("OpenRouter API key not provided")
            
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 4096,
                # OpenRouter-specific headers
                extra_headers={
                    "HTTP-Referer": "https://sage-mcp.local",
                    "X-Title": "SAGE MCP Server"
                }
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenRouter completion error: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """List available OpenRouter models"""
        return self.MODELS
    
    def validate_api_key(self) -> bool:
        """Check if OpenRouter API key is valid"""
        if not self.api_key or not self.client:
            return False
        try:
            # Simple test request with a cheap model
            import asyncio
            async def test():
                response = await self.client.chat.completions.create(
                    model="mistralai/mistral-7b-instruct",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1,
                    extra_headers={
                        "HTTP-Referer": "https://sage-mcp.local",
                        "X-Title": "SAGE MCP Server"
                    }
                )
                return True
            return asyncio.run(test())
        except Exception:
            return False