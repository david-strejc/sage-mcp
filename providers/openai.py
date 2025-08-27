"""
OpenAI AI provider
"""

import os
import logging
from typing import List, Dict, Optional

from openai import AsyncOpenAI
from providers.base import BaseProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseProvider):
    """OpenAI AI provider"""
    
    MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "o1",
        "o1-mini",
        "o3-mini"
    ]
    
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__(api_key)
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            self.client = None
    
    async def complete(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: Optional[int] = None
    ) -> str:
        """Complete using OpenAI"""
        if not self.client:
            raise ValueError("OpenAI API key not provided")
            
        try:
            # Special handling for o1/o3 models (they don't support system messages)
            if model.startswith(("o1", "o3")):
                # Convert system message to user message for o1/o3 models
                converted_messages = []
                for msg in messages:
                    if msg["role"] == "system":
                        converted_messages.append({
                            "role": "user",
                            "content": f"Instructions: {msg['content']}"
                        })
                    else:
                        converted_messages.append(msg)
                messages = converted_messages
                
                # o1/o3 models have fixed temperature
                temperature = 1.0
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 4096
            )
            
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
        try:
            # Simple test request
            import asyncio
            async def test():
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                return True
            return asyncio.run(test())
        except Exception:
            return False