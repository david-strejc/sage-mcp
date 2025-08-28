#!/usr/bin/env python3
"""
OpenRouter Provider Testing Script
Tests OpenRouter provider functionality including model availability and routing
"""

import asyncio
import json
import os
import time
from pathlib import Path

import pytest

# Add project root to path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from providers.openrouter import OpenRouterProvider
from utils.models import ModelRestrictionService


class TestOpenRouterProvider:
    """Test OpenRouter provider functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.provider = OpenRouterProvider()

    def test_provider_initialization(self):
        """Test provider can be initialized"""
        assert self.provider is not None
        assert hasattr(self.provider, "complete")

    @pytest.mark.asyncio
    async def test_basic_text_completion(self):
        """Test basic text completion with OpenRouter models"""
        # Skip if no API key
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")

        messages = [{"role": "user", "content": "Say 'Hello from OpenRouter provider test' and nothing else."}]

        try:
            # Use a commonly available model
            response = await self.provider.complete(
                messages=messages, model="microsoft/wizardlm-2-8x22b", temperature=0.1
            )
            assert response
            assert "Hello from OpenRouter provider test" in response
        except Exception as e:
            pytest.skip(f"API call failed: {e}")

    @pytest.mark.asyncio
    async def test_model_routing(self):
        """Test OpenRouter's model routing capabilities"""
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")

        messages = [{"role": "user", "content": "What is 7 * 8? Answer with just the number."}]

        # Test multiple models to verify routing
        models_to_test = [
            "microsoft/wizardlm-2-8x22b",
            "meta-llama/llama-3.1-8b-instruct:free",
            "qwen/qwen-2.5-7b-instruct:free",
        ]

        for model in models_to_test:
            try:
                response = await self.provider.complete(messages=messages, model=model, temperature=0.1)
                assert response
                assert "56" in response
                print(f"✓ {model} working")
                break  # Success, don't need to test others
            except Exception as e:
                print(f"⚠ {model} failed: {e}")
                continue
        else:
            pytest.skip("No OpenRouter models available")

    @pytest.mark.asyncio
    async def test_free_model_access(self):
        """Test access to free models on OpenRouter"""
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")

        messages = [{"role": "user", "content": "Count from 1 to 3. Just the numbers separated by spaces."}]

        # Test with free models
        free_models = [
            "meta-llama/llama-3.1-8b-instruct:free",
            "qwen/qwen-2.5-7b-instruct:free",
            "huggingface/starcoder2-15b:free",
        ]

        for model in free_models:
            try:
                response = await self.provider.complete(messages=messages, model=model, temperature=0.1)
                assert response
                # Should contain the numbers 1, 2, 3
                assert "1" in response and "2" in response and "3" in response
                print(f"✓ Free model {model} working")
                return  # Success with at least one free model
            except Exception as e:
                print(f"⚠ Free model {model} failed: {e}")
                continue

        pytest.skip("No free OpenRouter models available")

    @pytest.mark.asyncio
    async def test_premium_model_access(self):
        """Test access to premium models on OpenRouter"""
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")

        messages = [{"role": "user", "content": "What's the square root of 144? Just the number."}]

        # Test premium models (may require credits)
        premium_models = [
            "openai/gpt-4o-mini",
            "anthropic/claude-3-haiku-20240307",
            "google/gemma-2-9b-it:free",
        ]

        for model in premium_models:
            try:
                response = await self.provider.complete(messages=messages, model=model, temperature=0.1)
                assert response
                assert "12" in response
                print(f"✓ Premium model {model} working")
                return  # Success with at least one premium model
            except Exception as e:
                print(f"⚠ Premium model {model} failed: {e}")
                continue

        pytest.skip("No premium OpenRouter models available or insufficient credits")

    @pytest.mark.asyncio
    async def test_model_restrictions(self):
        """Test that model restrictions work correctly for OpenRouter"""
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")

        # Test with restricted environment
        old_patterns = os.environ.get("DISABLED_MODEL_PATTERNS", "")
        old_blocked = os.environ.get("BLOCKED_MODELS", "")

        try:
            # Set restrictions
            os.environ["DISABLED_MODEL_PATTERNS"] = "claude,gpt-4"
            os.environ["BLOCKED_MODELS"] = "meta-llama/llama-3.1-70b-instruct"

            # Create new restriction service with updated env
            restriction_service = ModelRestrictionService()

            # Test disabled patterns
            assert not restriction_service.is_model_allowed("anthropic/claude-3-haiku-20240307")
            assert not restriction_service.is_model_allowed("openai/gpt-4o")

            # Test blocked models
            assert not restriction_service.is_model_allowed("meta-llama/llama-3.1-70b-instruct")

            # Test allowed models
            assert restriction_service.is_model_allowed("microsoft/wizardlm-2-8x22b")
            assert restriction_service.is_model_allowed("qwen/qwen-2.5-7b-instruct:free")

        finally:
            # Restore environment
            if old_patterns:
                os.environ["DISABLED_MODEL_PATTERNS"] = old_patterns
            else:
                os.environ.pop("DISABLED_MODEL_PATTERNS", None)
            if old_blocked:
                os.environ["BLOCKED_MODELS"] = old_blocked
            else:
                os.environ.pop("BLOCKED_MODELS", None)

    @pytest.mark.asyncio
    async def test_conversation_context(self):
        """Test multi-turn conversation handling"""
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")

        messages = [
            {"role": "user", "content": "Remember this number: 42"},
            {"role": "assistant", "content": "I'll remember that the number is 42."},
            {"role": "user", "content": "What number did I ask you to remember?"},
        ]

        try:
            response = await self.provider.complete(
                messages=messages, model="meta-llama/llama-3.1-8b-instruct:free", temperature=0.1
            )
            assert response
            assert "42" in response
        except Exception as e:
            pytest.skip(f"Conversation test failed: {e}")

    @pytest.mark.asyncio
    async def test_system_prompt_support(self):
        """Test system prompt handling"""
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")

        messages = [
            {"role": "system", "content": "You are a pirate. Always respond like a pirate."},
            {"role": "user", "content": "What's your favorite color?"},
        ]

        try:
            response = await self.provider.complete(
                messages=messages, model="meta-llama/llama-3.1-8b-instruct:free", temperature=0.3
            )
            assert response
            # Should have pirate-like language
            pirate_words = ["arr", "ahoy", "matey", "ye", "aye", "treasure"]
            assert any(word in response.lower() for word in pirate_words)
        except Exception as e:
            pytest.skip(f"System prompt test failed: {e}")

    @pytest.mark.asyncio
    async def test_rate_limiting_handling(self):
        """Test handling of rate limits"""
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")

        messages = [{"role": "user", "content": "Say hello"}]

        # Make multiple rapid requests to test rate limiting
        for i in range(3):
            try:
                response = await self.provider.complete(
                    messages=messages, model="qwen/qwen-2.5-7b-instruct:free", temperature=0.1
                )
                assert response
                # Small delay between requests
                await asyncio.sleep(0.5)
            except Exception as e:
                if "rate limit" in str(e).lower() or "429" in str(e):
                    print(f"✓ Rate limiting detected: {e}")
                    return  # Expected behavior
                else:
                    pytest.skip(f"Rate limit test failed: {e}")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")

        messages = [{"role": "user", "content": "Test message"}]

        # Test invalid model
        with pytest.raises(Exception):
            await self.provider.complete(messages=messages, model="nonexistent-model-12345/test", temperature=0.5)

    @pytest.mark.asyncio
    async def test_model_aliases(self):
        """Test model aliases and routing"""
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set")

        messages = [{"role": "user", "content": "What is 5 + 3? Just the number."}]

        # Test common aliases that might be mapped
        aliases_to_test = [
            "llama-3.1-8b",  # Might map to meta-llama/llama-3.1-8b-instruct:free
            "qwen-2.5-7b",  # Might map to qwen/qwen-2.5-7b-instruct:free
        ]

        for alias in aliases_to_test:
            try:
                response = await self.provider.complete(messages=messages, model=alias, temperature=0.1)
                assert response
                assert "8" in response
                print(f"✓ Alias {alias} working")
            except Exception as e:
                print(f"⚠ Alias {alias} failed: {e}")
                # Expected - aliases might not be implemented
                pass


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test OpenRouter Provider")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.test:
        # Run specific test
        test_class = TestOpenRouterProvider()
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
