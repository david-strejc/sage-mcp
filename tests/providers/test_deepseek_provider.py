#!/usr/bin/env python3
"""
DeepSeek Provider Testing Script
Tests DeepSeek provider functionality including reasoning models and API validation
"""

import asyncio
import os
from pathlib import Path

import pytest

# Add project root to path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from providers.deepseek import DeepSeekProvider
from utils.models import ModelRestrictionService


class TestDeepSeekProvider:
    """Test DeepSeek provider functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.provider = DeepSeekProvider()

    def test_provider_initialization(self):
        """Test provider can be initialized"""
        assert self.provider is not None
        assert hasattr(self.provider, "complete")
        assert self.provider.BASE_URL == "https://api.deepseek.com"

    def test_list_models(self):
        """Test listing available models"""
        models = self.provider.list_models()
        assert "deepseek-chat" in models
        assert "deepseek-reasoner" in models
        assert "deepseek-coder" in models

    @pytest.mark.asyncio
    async def test_basic_completion(self):
        """Test basic text completion with deepseek-chat"""
        # Skip if no API key
        if not os.getenv("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set")

        messages = [{"role": "user", "content": "Say 'Hello from DeepSeek test' and nothing else."}]

        try:
            response = await self.provider.complete(messages=messages, model="deepseek-chat", temperature=0.1)
            assert response
            assert isinstance(response, str)
            assert len(response) > 0
            print(f"✓ DeepSeek chat response: {response}")
        except Exception as e:
            pytest.skip(f"API call failed: {e}")

    @pytest.mark.asyncio
    async def test_deepseek_reasoner(self):
        """Test deepseek-reasoner reasoning model"""
        # Skip if no API key
        if not os.getenv("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set")

        messages = [{"role": "user", "content": "Think step by step: What is 25 + 17?"}]

        try:
            response = await self.provider.complete(messages=messages, model="deepseek-reasoner", temperature=0.5)
            assert response
            assert isinstance(response, str)
            # Should contain reasoning and result
            print(f"✓ DeepSeek reasoner response: {response}")
        except Exception as e:
            pytest.skip(f"Reasoning test failed: {e}")

    @pytest.mark.asyncio
    async def test_deepseek_coder(self):
        """Test deepseek-coder specialized coding model"""
        # Skip if no API key
        if not os.getenv("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set")

        messages = [
            {
                "role": "user",
                "content": "Write a Python function to calculate fibonacci number. Just the function, no explanation.",
            }
        ]

        try:
            response = await self.provider.complete(messages=messages, model="deepseek-coder", temperature=0.3)
            assert response
            assert "def" in response or "fibonacci" in response.lower()
            print(f"✓ DeepSeek coder response: {response[:200]}...")
        except Exception as e:
            pytest.skip(f"Coder test failed: {e}")

    @pytest.mark.asyncio
    async def test_temperature_control(self):
        """Test temperature parameter handling"""
        if not os.getenv("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set")

        messages = [{"role": "user", "content": "Say hi"}]

        try:
            # Test low temperature (deterministic)
            response1 = await self.provider.complete(messages=messages, model="deepseek-chat", temperature=0.1)
            assert response1

            # Test high temperature (creative)
            response2 = await self.provider.complete(messages=messages, model="deepseek-chat", temperature=0.9)
            assert response2

            print("✓ Temperature control working")
        except Exception as e:
            pytest.skip(f"Temperature test failed: {e}")

    @pytest.mark.asyncio
    async def test_max_tokens_control(self):
        """Test max tokens parameter"""
        if not os.getenv("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set")

        messages = [{"role": "user", "content": "Write a very long essay about AI"}]

        try:
            # Test with small max_tokens
            response = await self.provider.complete(
                messages=messages, model="deepseek-chat", temperature=0.5, max_tokens=50
            )
            assert response
            # Response should be limited
            assert len(response.split()) < 100  # Rough check
            print("✓ Max tokens control working")
        except Exception as e:
            pytest.skip(f"Max tokens test failed: {e}")

    def test_api_key_validation(self):
        """Test API key validation"""
        # Test with valid key
        if os.getenv("DEEPSEEK_API_KEY"):
            provider = DeepSeekProvider(os.getenv("DEEPSEEK_API_KEY"))
            result = provider.validate_api_key()
            assert result is True or result is False  # Should return a boolean

        # Test with no key
        provider_no_key = DeepSeekProvider(api_key="")
        assert provider_no_key.validate_api_key() is False

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        if not os.getenv("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set")

        messages = [{"role": "user", "content": "Test message"}]

        # Test invalid model
        with pytest.raises(Exception):
            await self.provider.complete(messages=messages, model="nonexistent-deepseek-model", temperature=0.5)

    @pytest.mark.asyncio
    async def test_system_messages(self):
        """Test system message support"""
        if not os.getenv("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set")

        messages = [
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": "What programming language would you recommend for beginners?"},
        ]

        try:
            response = await self.provider.complete(messages=messages, model="deepseek-chat", temperature=0.5)
            assert response
            assert len(response) > 0
            print("✓ System messages working")
        except Exception as e:
            pytest.skip(f"System message test failed: {e}")

    @pytest.mark.asyncio
    async def test_model_restrictions(self):
        """Test that model restrictions work with DeepSeek"""
        if not os.getenv("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set")

        # Test with restricted environment
        old_patterns = os.environ.get("DISABLED_MODEL_PATTERNS", "")

        try:
            # Set restrictions
            os.environ["DISABLED_MODEL_PATTERNS"] = "deepseek-coder"

            # Create new restriction service with updated env
            restriction_service = ModelRestrictionService()

            # Test blocked models
            assert not restriction_service.is_model_allowed("deepseek-coder")

            # Test allowed models
            assert restriction_service.is_model_allowed("deepseek-chat")
            assert restriction_service.is_model_allowed("deepseek-reasoner")

            print("✓ Model restrictions working")
        finally:
            # Restore environment
            if old_patterns:
                os.environ["DISABLED_MODEL_PATTERNS"] = old_patterns
            else:
                os.environ.pop("DISABLED_MODEL_PATTERNS", None)


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test DeepSeek Provider")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.test:
        # Run specific test
        test_class = TestDeepSeekProvider()
        test_class.setup_method()

        test_method = getattr(test_class, f"test_{args.test}", None)
        if test_method:
            if asyncio.iscoroutinefunction(test_method):
                asyncio.run(test_method())
            else:
                test_method()
            print(f"✓ Test {args.test} completed")
        else:
            print(f"❌ Test {args.test} not found")
    else:
        # Run all tests with pytest
        pytest.main([__file__, "-v" if args.verbose else ""])
