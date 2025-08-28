"""
Base provider interface for all AI providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseProvider(ABC):
    """Base class for all AI providers"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def complete(
        self, model: str, messages: List[Dict[str, str]], temperature: float = 0.5, max_tokens: Optional[int] = None
    ) -> str:
        """
        Complete a chat conversation

        Args:
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models for this provider"""
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Check if API key is valid"""
        pass

    def _run_async_validation_test(self, test_function) -> bool:
        """
        Helper method to run async validation tests with common error handling

        Args:
            test_function: Async function that performs the validation test

        Returns:
            True if validation succeeds, False otherwise
        """
        try:
            import asyncio

            return asyncio.run(test_function())
        except Exception:
            return False
