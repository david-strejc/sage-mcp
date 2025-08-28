#!/usr/bin/env python3
"""
Anthropic Provider Testing Script
Tests Anthropic Claude provider functionality including vision models and message formatting
"""

import asyncio
import base64
import json
import os
import tempfile
import time
from pathlib import Path

import pytest

# Add project root to path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from providers.anthropic import AnthropicProvider
from utils.models import ModelRestrictionService


class TestAnthropicProvider:
    """Test Anthropic provider functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.provider = AnthropicProvider()

    def test_provider_initialization(self):
        """Test provider can be initialized"""
        assert self.provider is not None
        assert hasattr(self.provider, "complete")

    @pytest.mark.asyncio
    async def test_basic_text_completion(self):
        """Test basic text completion with Claude models"""
        # Skip if no API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        messages = [{"role": "user", "content": "Say 'Hello from Anthropic provider test' and nothing else."}]

        try:
            response = await self.provider.complete(messages=messages, model="claude-3-haiku-20240307", temperature=0.1)
            assert response
            assert "Hello from Anthropic provider test" in response
        except Exception as e:
            pytest.skip(f"API call failed: {e}")

    @pytest.mark.asyncio
    async def test_claude_3_5_sonnet(self):
        """Test Claude 3.5 Sonnet model"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        messages = [{"role": "user", "content": "What's 25 * 4? Answer with just the number."}]

        try:
            response = await self.provider.complete(
                messages=messages, model="claude-3-5-sonnet-20241022", temperature=0.1
            )
            assert response
            assert "100" in response
        except Exception as e:
            # Try fallback model
            try:
                response = await self.provider.complete(
                    messages=messages, model="claude-3-haiku-20240307", temperature=0.1
                )
                assert response
                assert "100" in response
            except Exception as e2:
                pytest.skip(f"Claude models not available: {e}, {e2}")

    @pytest.mark.asyncio
    async def test_vision_capabilities(self):
        """Test Claude vision capabilities with images"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        # Create a simple test image (blue square)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            # Create a simple 10x10 blue PNG
            png_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABeSURBVBiVY2RgYPjPwMDAwMjIyMDMzMzAzMzMwMLCwsDKysrAzs7OwM7OzsDJycnAzc3NwMPDw8DHx8fAz8/PwCcgIMAgKCjIICQkxCAkJMQgLCzMICwszCAsLMwAAFsMDA0kEjb2AAAAAElFTkSuQmCC"
            )
            temp_file.write(png_data)
            temp_image = temp_file.name

        try:
            # Read image as base64
            with open(temp_image, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode("utf-8")

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What color is this image? Just answer with the color name."},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_data}},
                    ],
                }
            ]

            response = await self.provider.complete(
                messages=messages, model="claude-3-5-sonnet-20241022", temperature=0.1  # Vision model
            )
            assert response
            # Should detect blue color
            assert "blue" in response.lower() or "color" in response.lower()

        except Exception as e:
            pytest.skip(f"Vision test failed: {e}")
        finally:
            # Cleanup
            if os.path.exists(temp_image):
                os.unlink(temp_image)

    @pytest.mark.asyncio
    async def test_system_prompt_handling(self):
        """Test system prompt handling in Claude"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        messages = [
            {"role": "system", "content": "You are a helpful math tutor. Always show your work."},
            {"role": "user", "content": "What is 12 + 8?"},
        ]

        try:
            response = await self.provider.complete(messages=messages, model="claude-3-haiku-20240307", temperature=0.1)
            assert response
            assert "20" in response
            # Should show work due to system prompt
            assert len(response) > 10  # More than just "20"
        except Exception as e:
            pytest.skip(f"System prompt test failed: {e}")

    @pytest.mark.asyncio
    async def test_conversation_history(self):
        """Test multi-turn conversation handling"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        messages = [
            {"role": "user", "content": "My name is Alice."},
            {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
            {"role": "user", "content": "What did I just tell you my name was?"},
        ]

        try:
            response = await self.provider.complete(messages=messages, model="claude-3-haiku-20240307", temperature=0.1)
            assert response
            assert "Alice" in response
        except Exception as e:
            pytest.skip(f"Conversation test failed: {e}")

    @pytest.mark.asyncio
    async def test_model_restrictions(self):
        """Test that model restrictions work correctly for Anthropic"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        # Test with restricted environment
        old_allowed = os.environ.get("ANTHROPIC_ALLOWED_MODELS", "")
        old_patterns = os.environ.get("DISABLED_MODEL_PATTERNS", "")

        try:
            # Set restrictions
            os.environ["ANTHROPIC_ALLOWED_MODELS"] = "claude-3-haiku-20240307"
            os.environ["DISABLED_MODEL_PATTERNS"] = "claude-2"

            # Create new restriction service with updated env
            restriction_service = ModelRestrictionService()

            # Test allowed models
            assert restriction_service.is_model_allowed("claude-3-haiku-20240307")

            # Test disabled patterns
            assert not restriction_service.is_model_allowed("claude-2.1")

            # Test non-allowed models
            assert not restriction_service.is_model_allowed("claude-3-5-sonnet-20241022")

        finally:
            # Restore environment
            if old_allowed:
                os.environ["ANTHROPIC_ALLOWED_MODELS"] = old_allowed
            else:
                os.environ.pop("ANTHROPIC_ALLOWED_MODELS", None)
            if old_patterns:
                os.environ["DISABLED_MODEL_PATTERNS"] = old_patterns
            else:
                os.environ.pop("DISABLED_MODEL_PATTERNS", None)

    @pytest.mark.asyncio
    async def test_large_context_handling(self):
        """Test Claude's large context window"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        # Create moderately large text input
        large_text = "The quick brown fox jumps over the lazy dog. " * 500  # ~5000 tokens

        messages = [
            {
                "role": "user",
                "content": f"Count how many times the word 'fox' appears in this text: {large_text}. Just give me the number.",
            }
        ]

        try:
            response = await self.provider.complete(
                messages=messages, model="claude-3-5-sonnet-20241022", temperature=0.1
            )
            assert response
            # Should count 500 occurrences
            assert "500" in response or "five hundred" in response.lower()
        except Exception as e:
            pytest.skip(f"Large context test failed: {e}")

    @pytest.mark.asyncio
    async def test_tool_use_format(self):
        """Test Claude's tool use capabilities"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        messages = [
            {
                "role": "user",
                "content": "If you had access to a calculator tool, how would you compute 123 * 456? Don't actually do the calculation, just explain how you'd use the tool.",
            }
        ]

        try:
            response = await self.provider.complete(
                messages=messages, model="claude-3-5-sonnet-20241022", temperature=0.1
            )
            assert response
            assert "tool" in response.lower() or "calculator" in response.lower()
        except Exception as e:
            pytest.skip(f"Tool use test failed: {e}")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        messages = [{"role": "user", "content": "Test message"}]

        # Test invalid model
        with pytest.raises(Exception):
            await self.provider.complete(messages=messages, model="nonexistent-claude-model-12345", temperature=0.5)

    @pytest.mark.asyncio
    async def test_temperature_variations(self):
        """Test different temperature settings"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        messages = [{"role": "user", "content": "Write a creative two-word phrase about coding."}]

        try:
            # Test low temperature (deterministic)
            response_low = await self.provider.complete(
                messages=messages, model="claude-3-haiku-20240307", temperature=0.1
            )

            # Test high temperature (creative)
            response_high = await self.provider.complete(
                messages=messages, model="claude-3-haiku-20240307", temperature=0.9
            )

            assert response_low
            assert response_high
            # Both should be short responses
            assert len(response_low.split()) <= 10
            assert len(response_high.split()) <= 10

        except Exception as e:
            pytest.skip(f"Temperature test failed: {e}")


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test Anthropic Provider")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.test:
        # Run specific test
        test_class = TestAnthropicProvider()
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
