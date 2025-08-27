"""
Custom/Ollama AI provider for local models
"""

import os
import logging
from typing import List, Dict, Optional

from openai import AsyncOpenAI
from providers.base import BaseProvider

logger = logging.getLogger(__name__)

class CustomProvider(BaseProvider):
    """Custom/Ollama AI provider for local models"""
    
    MODELS = [
        "llama3.2",
        "llama3.1:8b",
        "llama3.1:70b",
        "mistral:7b",
        "mixtral:8x7b",
        "codellama:7b",
        "codellama:13b"
    ]
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv("CUSTOM_API_URL", "http://localhost:11434")
        api_key = api_key or os.getenv("CUSTOM_API_KEY", "")
        super().__init__(api_key)
        
        # For Ollama, API key is often not needed
        self.client = AsyncOpenAI(
            api_key=api_key or "ollama",  # Ollama doesn't require a real API key
            base_url=f"{self.base_url}/v1"
        )
    
    async def complete(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: Optional[int] = None
    ) -> str:
        """Complete using custom/Ollama endpoint"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 2048
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Custom/Ollama completion error: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """List available custom models"""
        # In a real implementation, this could query the Ollama API
        # for available models
        return self.MODELS
    
    def validate_api_key(self) -> bool:
        """Check if custom endpoint is accessible"""
        async def test():
            await self.client.chat.completions.create(
                model="llama3.2",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
            
        return self._run_async_validation_test(test)