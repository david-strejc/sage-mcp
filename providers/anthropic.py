"""
Anthropic Claude AI provider
"""

import os
import logging
from typing import List, Dict, Optional

from anthropic import AsyncAnthropic
from providers.base import BaseProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(BaseProvider):
    """Anthropic Claude AI provider"""
    
    MODELS = [
        "claude-3.5-sonnet-20241022",
        "claude-3.5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]
    
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        super().__init__(api_key)
        if api_key:
            self.client = AsyncAnthropic(api_key=api_key)
        else:
            self.client = None
    
    async def complete(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: Optional[int] = None
    ) -> str:
        """Complete using Anthropic Claude"""
        if not self.client:
            raise ValueError("Anthropic API key not provided")
            
        try:
            # Extract system message if present
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = await self.client.messages.create(
                model=model,
                system=system_message if system_message else None,
                messages=user_messages,
                temperature=temperature,
                max_tokens=max_tokens or 4096
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic completion error: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """List available Anthropic models"""
        return self.MODELS
    
    def validate_api_key(self) -> bool:
        """Check if Anthropic API key is valid"""
        if not self.api_key or not self.client:
            return False
        try:
            # Simple test request
            import asyncio
            async def test():
                response = await self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                return True
            return asyncio.run(test())
        except Exception:
            return False