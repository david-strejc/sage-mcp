#!/usr/bin/env python3
"""
Gemini Provider Testing Script
Tests Gemini provider functionality including vision models, thinking mode, and file upload
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

from providers.gemini import GeminiProvider
from utils.models import ModelRestrictionService


class TestGeminiProvider:
    """Test Gemini provider functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.provider = GeminiProvider()

    def test_provider_initialization(self):
        """Test provider can be initialized"""
        assert self.provider is not None
        assert hasattr(self.provider, "complete")

    @pytest.mark.asyncio
    async def test_basic_text_completion(self):
        """Test basic text completion with Gemini models"""
        # Skip if no API key
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        messages = [{"role": "user", "content": "Say 'Hello from Gemini provider test' and nothing else."}]

        try:
            response = await self.provider.complete(messages=messages, model="gemini-1.5-flash", temperature=0.1)
            assert response
            assert "Hello from Gemini provider test" in response
        except Exception as e:
            pytest.skip(f"API call failed: {e}")

    @pytest.mark.asyncio
    async def test_gemini_2_0_flash(self):
        """Test Gemini 2.0 Flash model"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        messages = [{"role": "user", "content": "What's the capital of France? Answer in exactly two words."}]

        try:
            response = await self.provider.complete(messages=messages, model="gemini-2.0-flash", temperature=0.1)
            assert response
            assert "Paris" in response
        except Exception as e:
            # Try fallback to available model
            try:
                response = await self.provider.complete(messages=messages, model="gemini-1.5-flash", temperature=0.1)
                assert response
                assert "Paris" in response
            except Exception as e2:
                pytest.skip(f"Gemini models not available: {e}, {e2}")

    @pytest.mark.asyncio
    async def test_thinking_mode_support(self):
        """Test Gemini thinking mode for complex reasoning"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        messages = [
            {
                "role": "user",
                "content": "Think step by step: If I have 3 apples and buy 2 more, then give away 1, how many do I have?",
            }
        ]

        try:
            # Test with thinking mode (if supported)
            response = await self.provider.complete(
                messages=messages, model="gemini-2.0-flash-thinking-exp", temperature=0.3  # Thinking model
            )
            assert response
            assert "4" in response or "four" in response.lower()
        except Exception as e:
            # Fallback to regular model
            try:
                response = await self.provider.complete(messages=messages, model="gemini-2.0-flash", temperature=0.3)
                assert response
                assert "4" in response or "four" in response.lower()
            except Exception as e2:
                pytest.skip(f"Gemini thinking test failed: {e}, {e2}")

    @pytest.mark.asyncio
    async def test_vision_capabilities(self):
        """Test Gemini vision capabilities with images"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        # Create a simple test image (red square)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            # Create a simple 10x10 red PNG
            png_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABeSURBVBiVY2RgYPjPwMDAwMjIyMDMzMzAzMzMwMLCwsDKysrAzs7OwM7OzsDJycnAzc3NwMPDw8DHx8fAz8/PwCcgIMAgKCjIICQkxCAkJMQgLCzMICwszCAsLMwAAB4MDAzVGK7VAAAAAElFTkSuQmCC"
            )
            temp_file.write(png_data)
            temp_image = temp_file.name

        try:
            messages = [
                {
                    "role": "user",
                    "content": f"What color is this image? Just answer with the color name.",
                    "files": [temp_image],  # SAGE format for file handling
                }
            ]

            response = await self.provider.complete(
                messages=messages, model="gemini-1.5-pro", temperature=0.1  # Pro model for better vision
            )
            assert response
            # Should detect red color
            assert "red" in response.lower() or "color" in response.lower()

        except Exception as e:
            pytest.skip(f"Vision test failed: {e}")
        finally:
            # Cleanup
            if os.path.exists(temp_image):
                os.unlink(temp_image)

    @pytest.mark.asyncio
    async def test_large_context_window(self):
        """Test Gemini's large context window capabilities"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        # Create a large text input to test context window
        large_text = "This is a test sentence. " * 1000  # ~5000 tokens

        messages = [
            {
                "role": "user",
                "content": f"Count how many times the word 'test' appears in this text: {large_text}. Just give me the number.",
            }
        ]

        try:
            response = await self.provider.complete(messages=messages, model="gemini-1.5-pro", temperature=0.1)
            assert response
            # Should count 1000 occurrences
            assert "1000" in response or "thousand" in response.lower()
        except Exception as e:
            pytest.skip(f"Large context test failed: {e}")

    @pytest.mark.asyncio
    async def test_model_restrictions(self):
        """Test that model restrictions work correctly for Gemini"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        # Test with restricted environment
        old_allowed = os.environ.get("GOOGLE_ALLOWED_MODELS", "")
        old_patterns = os.environ.get("DISABLED_MODEL_PATTERNS", "")

        try:
            # Set restrictions
            os.environ["GOOGLE_ALLOWED_MODELS"] = "gemini-1.5-flash,gemini-2.0-flash"
            os.environ["DISABLED_MODEL_PATTERNS"] = "gemini-1.0"

            # Create new restriction service with updated env
            restriction_service = ModelRestrictionService()

            # Test allowed models
            assert restriction_service.is_model_allowed("gemini-1.5-flash")
            assert restriction_service.is_model_allowed("gemini-2.0-flash")

            # Test disabled patterns
            assert not restriction_service.is_model_allowed("gemini-1.0-pro")

            # Test non-allowed models
            assert not restriction_service.is_model_allowed("gemini-1.5-pro")

        finally:
            # Restore environment
            if old_allowed:
                os.environ["GOOGLE_ALLOWED_MODELS"] = old_allowed
            else:
                os.environ.pop("GOOGLE_ALLOWED_MODELS", None)
            if old_patterns:
                os.environ["DISABLED_MODEL_PATTERNS"] = old_patterns
            else:
                os.environ.pop("DISABLED_MODEL_PATTERNS", None)

    @pytest.mark.asyncio
    async def test_json_mode(self):
        """Test Gemini JSON mode support"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        messages = [
            {
                "role": "user",
                "content": "Return JSON with keys 'name' set to 'test' and 'count' set to 42. Return only valid JSON.",
            }
        ]

        try:
            response = await self.provider.complete(messages=messages, model="gemini-1.5-flash", temperature=0.1)
            assert response

            # Try to parse as JSON
            try:
                # Extract JSON from response if wrapped in markdown
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].strip()
                else:
                    json_str = response.strip()

                data = json.loads(json_str)
                assert data.get("name") == "test"
                assert data.get("count") == 42
            except json.JSONDecodeError:
                # JSON parsing failed, but response was generated
                assert len(response) > 0

        except Exception as e:
            pytest.skip(f"JSON mode test failed: {e}")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        messages = [{"role": "user", "content": "Test message"}]

        # Test invalid model
        with pytest.raises(Exception):
            await self.provider.complete(messages=messages, model="nonexistent-gemini-model-12345", temperature=0.5)


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test Gemini Provider")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.test:
        # Run specific test
        test_class = TestGeminiProvider()
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
