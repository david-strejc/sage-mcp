#!/usr/bin/env python3
"""
Test script for DeepSeek API integration
Tests the API key and available models
"""

import asyncio
import os
import sys
from openai import AsyncOpenAI

# DeepSeek API configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# DeepSeek models (as of 2025)
DEEPSEEK_MODELS = [
    "deepseek-reasoner",  # Latest reasoning model (most recent)
    "deepseek-chat",      # General purpose chat model
    "deepseek-coder",     # Code-specialized model
]


async def test_deepseek_api():
    """Test DeepSeek API connection and response"""
    print("=" * 60)
    print("DeepSeek API Test")
    print("=" * 60)

    # Create client (DeepSeek uses OpenAI-compatible API)
    client = AsyncOpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )

    # Test each model
    for model in DEEPSEEK_MODELS:
        print(f"\n📝 Testing model: {model}")
        print("-" * 60)

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello from DeepSeek!' and tell me your model name in one sentence."}
                ],
                max_tokens=100,
                temperature=0.7
            )

            content = response.choices[0].message.content
            print(f"✅ Success!")
            print(f"Response: {content}")
            print(f"Model used: {response.model}")
            print(f"Tokens - Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}")

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)


async def test_model_list():
    """Try to list available models"""
    print("\n📋 Attempting to list available models...")
    print("-" * 60)

    try:
        client = AsyncOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )

        models = await client.models.list()
        print("✅ Available models:")
        for model in models.data:
            print(f"  - {model.id}")
    except Exception as e:
        print(f"❌ Could not list models: {e}")
        print("ℹ️  This is normal - DeepSeek may not support model listing endpoint")


if __name__ == "__main__":
    print("\n🚀 Starting DeepSeek API tests...\n")

    try:
        asyncio.run(test_deepseek_api())
        asyncio.run(test_model_list())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)

    print("\n✨ All tests completed!\n")
