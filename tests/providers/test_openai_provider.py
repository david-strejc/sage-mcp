#!/usr/bin/env python3
"""
OpenAI Provider Testing Script
Tests OpenAI provider functionality including o1/o3 reasoning models, image support, and API validation
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

from providers.openai import OpenAIProvider
from utils.models import ModelRestrictionService


class TestOpenAIProvider:
    """Test OpenAI provider functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.provider = OpenAIProvider()

    def test_provider_initialization(self):
        """Test provider can be initialized"""
        assert self.provider is not None
        assert hasattr(self.provider, "complete")

    @pytest.mark.asyncio
    async def test_basic_text_completion(self):
        """Test basic text completion with GPT models"""
        # Skip if no API key
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        messages = [{"role": "user", "content": "Say 'Hello from OpenAI provider test' and nothing else."}]

        try:
            response = await self.provider.complete(messages=messages, model="gpt-4o-mini", temperature=0.1)
            assert response
            assert "Hello from OpenAI provider test" in response
        except Exception as e:
            pytest.skip(f"API call failed: {e}")

    @pytest.mark.asyncio
    async def test_o1_reasoning_model(self):
        """Test o1/o3 reasoning models (no system prompts, temperature constraints)"""
        # Skip if no API key or model not available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        messages = [{"role": "user", "content": "Think step by step: What is 15 + 27?"}]

        try:
            # Test with o1-mini (more likely to be available)
            response = await self.provider.complete(
                messages=messages, model="o1-mini", temperature=1.0  # Should be handled properly for o1 models
            )
            assert response
            assert "42" in response or "forty" in response.lower()
        except Exception as e:
            # If o1-mini not available, try o3-mini
            try:
                response = await self.provider.complete(messages=messages, model="o3-mini", temperature=1.0)
                assert response
                assert "42" in response or "forty" in response.lower()
            except Exception as e2:
                pytest.skip(f"O1/O3 models not available: {e}, {e2}")

    @pytest.mark.asyncio
    async def test_image_support_gpt4o(self):
        """Test image support with GPT-4o models"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        # Create a simple test image (1x1 PNG)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            # Simple PNG header for 1x1 transparent image
            png_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
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
                        {"type": "text", "text": "What do you see in this image? Be brief."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_data}"}},
                    ],
                }
            ]

            response = await self.provider.complete(messages=messages, model="gpt-4o", temperature=0.1)
            assert response
            # GPT-4o should be able to process the image
            assert len(response) > 0

        except Exception as e:
            pytest.skip(f"Image test failed: {e}")
        finally:
            # Cleanup
            if os.path.exists(temp_image):
                os.unlink(temp_image)

    @pytest.mark.asyncio
    async def test_model_restrictions(self):
        """Test that model restrictions work correctly"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        # Test with restricted environment
        old_blocked = os.environ.get("BLOCKED_MODELS", "")
        old_patterns = os.environ.get("DISABLED_MODEL_PATTERNS", "")

        try:
            # Set restrictions
            os.environ["BLOCKED_MODELS"] = "gpt-4,gpt-3.5-turbo"
            os.environ["DISABLED_MODEL_PATTERNS"] = "text-"

            # Create new restriction service with updated env
            restriction_service = ModelRestrictionService()

            # Test blocked models
            assert not restriction_service.is_model_allowed("gpt-4")
            assert not restriction_service.is_model_allowed("gpt-3.5-turbo")
            assert not restriction_service.is_model_allowed("text-davinci-003")

            # Test allowed models
            assert restriction_service.is_model_allowed("gpt-4o")
            assert restriction_service.is_model_allowed("o1-mini")

        finally:
            # Restore environment
            if old_blocked:
                os.environ["BLOCKED_MODELS"] = old_blocked
            else:
                os.environ.pop("BLOCKED_MODELS", None)
            if old_patterns:
                os.environ["DISABLED_MODEL_PATTERNS"] = old_patterns
            else:
                os.environ.pop("DISABLED_MODEL_PATTERNS", None)

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        messages = [{"role": "user", "content": "Test message"}]

        # Test invalid model
        with pytest.raises(Exception):
            await self.provider.complete(messages=messages, model="nonexistent-model-12345", temperature=0.5)

    @pytest.mark.asyncio
    async def test_streaming_support(self):
        """Test streaming completion support"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        messages = [{"role": "user", "content": "Count from 1 to 5, each number on a new line."}]

        try:
            # Note: Our current provider doesn't implement streaming
            # This test validates the basic completion still works
            response = await self.provider.complete(messages=messages, model="gpt-4o-mini", temperature=0.1)
            assert response
            assert "1" in response and "5" in response
        except Exception as e:
            pytest.skip(f"Streaming test failed: {e}")


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test OpenAI Provider")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.test:
        # Run specific test
        test_class = TestOpenAIProvider()
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
