"""
Google Gemini AI provider
"""

import os
import logging
from typing import List, Dict, Optional

import google.generativeai as genai
from providers.base import BaseProvider

logger = logging.getLogger(__name__)

class GeminiProvider(BaseProvider):
    """Google Gemini AI provider"""
    
    MODELS = [
        # Gemini 2.5 Generation (Latest - 2025)
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-preview",
        
        # Gemini 2.0 Generation
        "gemini-2.0-flash",
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash-thinking-exp",
        
        # Gemini 1.5 Generation (Legacy)
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b"
    ]
    
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        super().__init__(api_key)
        if api_key:
            genai.configure(api_key=api_key)
    
    async def complete(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        max_tokens: Optional[int] = None
    ) -> str:
        """Complete using Gemini"""
        try:
            # Initialize model
            gemini_model = genai.GenerativeModel(model)
            
            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                gemini_messages.append({
                    "role": role,
                    "parts": [msg["content"]]
                })
            
            # Generate response
            response = await gemini_model.generate_content_async(
                gemini_messages,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens or 8192,
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini completion error: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """List available Gemini models"""
        return self.MODELS
    
    def validate_api_key(self) -> bool:
        """Check if Gemini API key is valid"""
        if not self.api_key:
            return False
        try:
            # Try to list models as validation
            list(genai.list_models())
            return True
        except Exception:
            return False