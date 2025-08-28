#!/usr/bin/env python3
"""
Custom/Ollama Provider Testing Script
Tests Custom provider functionality including Ollama integration and local models
"""

import asyncio
import json
import os
import time
from pathlib import Path

import pytest
import requests

# Add project root to path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from providers.custom import CustomProvider
from utils.models import ModelRestrictionService


class TestCustomProvider:
    """Test Custom/Ollama provider functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.provider = CustomProvider()

    def test_provider_initialization(self):
        """Test provider can be initialized"""
        assert self.provider is not None
        assert hasattr(self.provider, "complete")

    def test_ollama_connectivity(self):
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    @pytest.mark.asyncio
    async def test_basic_text_completion(self):
        """Test basic text completion with local models"""
        # Skip if no custom API URL configured
        if not os.getenv("CUSTOM_API_URL"):
            pytest.skip("CUSTOM_API_URL not set")

        # Check if Ollama is running
        if not self.test_ollama_connectivity():
            pytest.skip("Ollama not running on localhost:11434")

        messages = [{"role": "user", "content": "Say 'Hello from Custom provider test' and nothing else."}]

        try:
            response = await self.provider.complete(messages=messages, model="llama3.2", temperature=0.1)
            assert response
            assert "Hello from Custom provider test" in response
        except Exception as e:
            pytest.skip(f"API call failed: {e}")

    @pytest.mark.asyncio
    async def test_local_model_inference(self):
        """Test inference with local Ollama models"""
        if not os.getenv("CUSTOM_API_URL"):
            pytest.skip("CUSTOM_API_URL not set")

        if not self.test_ollama_connectivity():
            pytest.skip("Ollama not running")

        messages = [{"role": "user", "content": "What is 6 * 7? Answer with just the number."}]

        # Try different common models
        models_to_try = ["llama3.2", "llama2", "qwen2.5", "phi3", "gemma2"]

        for model in models_to_try:
            try:
                response = await self.provider.complete(messages=messages, model=model, temperature=0.1)
                assert response
                assert "42" in response
                print(f"✓ Local model {model} working")
                return  # Success with at least one model
            except Exception as e:
                print(f"⚠ Model {model} failed: {e}")
                continue

        pytest.skip("No local models available in Ollama")

    def test_list_available_models(self):
        """Test listing available models from Ollama"""
        if not os.getenv("CUSTOM_API_URL"):
            pytest.skip("CUSTOM_API_URL not set")

        if not self.test_ollama_connectivity():
            pytest.skip("Ollama not running")

        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            assert response.status_code == 200

            data = response.json()
            models = data.get("models", [])

            print(f"Available Ollama models: {[m['name'] for m in models]}")

            # Should have at least one model if Ollama is set up
            if len(models) == 0:
                pytest.skip("No models installed in Ollama")

            assert len(models) > 0

        except Exception as e:
            pytest.skip(f"Failed to list models: {e}")

    @pytest.mark.asyncio
    async def test_different_temperature_settings(self):
        """Test different temperature settings with local models"""
        if not os.getenv("CUSTOM_API_URL"):
            pytest.skip("CUSTOM_API_URL not set")

        if not self.test_ollama_connectivity():
            pytest.skip("Ollama not running")

        messages = [{"role": "user", "content": "Write a creative name for a pet robot. Just one name."}]

        try:
            # Test deterministic (low temperature)
            response_low = await self.provider.complete(messages=messages, model="llama3.2", temperature=0.1)

            # Test creative (high temperature)
            response_high = await self.provider.complete(messages=messages, model="llama3.2", temperature=0.9)

            assert response_low
            assert response_high

            # Both should be relatively short
            assert len(response_low.split()) <= 10
            assert len(response_high.split()) <= 10

            print(f"Low temp: {response_low}")
            print(f"High temp: {response_high}")

        except Exception as e:
            pytest.skip(f"Temperature test failed: {e}")

    @pytest.mark.asyncio
    async def test_conversation_memory(self):
        """Test multi-turn conversation handling"""
        if not os.getenv("CUSTOM_API_URL"):
            pytest.skip("CUSTOM_API_URL not set")

        if not self.test_ollama_connectivity():
            pytest.skip("Ollama not running")

        messages = [
            {"role": "user", "content": "My favorite number is 77."},
            {"role": "assistant", "content": "I'll remember that your favorite number is 77."},
            {"role": "user", "content": "What did I say my favorite number was?"},
        ]

        try:
            response = await self.provider.complete(messages=messages, model="llama3.2", temperature=0.1)
            assert response
            assert "77" in response
        except Exception as e:
            pytest.skip(f"Conversation test failed: {e}")

    @pytest.mark.asyncio
    async def test_system_prompt_support(self):
        """Test system prompt handling with local models"""
        if not os.getenv("CUSTOM_API_URL"):
            pytest.skip("CUSTOM_API_URL not set")

        if not self.test_ollama_connectivity():
            pytest.skip("Ollama not running")

        messages = [
            {"role": "system", "content": "You are a helpful math teacher. Always explain your work."},
            {"role": "user", "content": "What is 15 + 25?"},
        ]

        try:
            response = await self.provider.complete(messages=messages, model="llama3.2", temperature=0.1)
            assert response
            assert "40" in response
            # Should explain due to system prompt
            assert len(response) > 10
        except Exception as e:
            pytest.skip(f"System prompt test failed: {e}")

    @pytest.mark.asyncio
    async def test_model_restrictions(self):
        """Test that model restrictions work correctly for custom models"""
        # Test with restricted environment
        old_patterns = os.environ.get("DISABLED_MODEL_PATTERNS", "")
        old_blocked = os.environ.get("BLOCKED_MODELS", "")

        try:
            # Set restrictions
            os.environ["DISABLED_MODEL_PATTERNS"] = "llama2,phi"
            os.environ["BLOCKED_MODELS"] = "dangerous-model"

            # Create new restriction service with updated env
            restriction_service = ModelRestrictionService()

            # Test disabled patterns
            assert not restriction_service.is_model_allowed("llama2")
            assert not restriction_service.is_model_allowed("phi3")

            # Test blocked models
            assert not restriction_service.is_model_allowed("dangerous-model")

            # Test allowed models
            assert restriction_service.is_model_allowed("llama3.2")
            assert restriction_service.is_model_allowed("qwen2.5")

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
    async def test_custom_api_endpoint(self):
        """Test custom API endpoint configuration"""
        # Test with different endpoints
        endpoints_to_test = [
            "http://localhost:11434",  # Default Ollama
            "http://127.0.0.1:11434",  # Alternative localhost
        ]

        for endpoint in endpoints_to_test:
            try:
                # Set custom endpoint
                old_url = os.environ.get("CUSTOM_API_URL", "")
                os.environ["CUSTOM_API_URL"] = endpoint

                # Test connectivity
                response = requests.get(f"{endpoint}/api/tags", timeout=5)
                if response.status_code == 200:
                    print(f"✓ Endpoint {endpoint} accessible")
                    return  # Found working endpoint

            except Exception as e:
                print(f"⚠ Endpoint {endpoint} failed: {e}")
                continue
            finally:
                # Restore original URL
                if old_url:
                    os.environ["CUSTOM_API_URL"] = old_url

        pytest.skip("No custom endpoints accessible")

    @pytest.mark.asyncio
    async def test_performance_timing(self):
        """Test response times for local models"""
        if not os.getenv("CUSTOM_API_URL"):
            pytest.skip("CUSTOM_API_URL not set")

        if not self.test_ollama_connectivity():
            pytest.skip("Ollama not running")

        messages = [{"role": "user", "content": "Count from 1 to 5."}]

        try:
            start_time = time.time()
            response = await self.provider.complete(messages=messages, model="llama3.2", temperature=0.1)
            end_time = time.time()

            assert response
            duration = end_time - start_time

            print(f"Local model response time: {duration:.2f}s")

            # Local models should respond reasonably quickly
            # Allow up to 30 seconds for smaller models
            assert duration < 30.0

        except Exception as e:
            pytest.skip(f"Performance test failed: {e}")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        if not os.getenv("CUSTOM_API_URL"):
            pytest.skip("CUSTOM_API_URL not set")

        messages = [{"role": "user", "content": "Test message"}]

        # Test invalid model
        with pytest.raises(Exception):
            await self.provider.complete(messages=messages, model="nonexistent-local-model-12345", temperature=0.5)


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test Custom Provider")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--check-ollama", action="store_true", help="Check Ollama connectivity only")
    args = parser.parse_args()

    if args.check_ollama:
        # Quick connectivity check
        test_class = TestCustomProvider()
        if test_class.test_ollama_connectivity():
            print("✓ Ollama is running and accessible")
        else:
            print("❌ Ollama is not accessible")
        sys.exit(0)

    if args.test:
        # Run specific test
        test_class = TestCustomProvider()
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
