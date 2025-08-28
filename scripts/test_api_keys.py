#!/usr/bin/env python3
"""
Test API keys and provider connectivity
"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from providers import initialize_providers, PROVIDERS


async def test_providers():
    """Test all configured providers"""
    print("🔑 Testing API keys and provider connectivity...")
    print("=" * 50)

    config = Config()
    api_keys = config.get_api_keys()

    # Check which keys are configured
    configured = []
    for name, key in api_keys.items():
        if key:
            configured.append(name)

    print(f"Configured API keys: {', '.join(configured) if configured else 'None'}")
    print()

    # Initialize providers
    try:
        initialize_providers()
        print(f"✓ {len(PROVIDERS)} provider(s) initialized: {list(PROVIDERS.keys())}")
    except Exception as e:
        print(f"❌ Provider initialization failed: {e}")
        return False

    print()

    # Test each provider
    all_passed = True
    for name, provider in PROVIDERS.items():
        print(f"Testing {name} provider...")
        try:
            # Test simple completion
            if name == "gemini":
                response = await provider.complete(
                    model="gemini-1.5-flash",
                    messages=[{"role": "user", "content": "Say 'test passed'"}],
                    temperature=0.1,
                    max_tokens=10,
                )
            elif name == "openai":
                response = await provider.complete(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "Say 'test passed'"}],
                    temperature=0.1,
                    max_tokens=10,
                )
            elif name == "anthropic":
                response = await provider.complete(
                    model="claude-3.5-haiku-20241022",
                    messages=[{"role": "user", "content": "Say 'test passed'"}],
                    temperature=0.1,
                    max_tokens=10,
                )
            elif name == "openrouter":
                response = await provider.complete(
                    model="mistralai/mistral-7b-instruct",
                    messages=[{"role": "user", "content": "Say 'test passed'"}],
                    temperature=0.1,
                    max_tokens=10,
                )
            elif name == "custom":
                response = await provider.complete(
                    model="llama3.2",
                    messages=[{"role": "user", "content": "Say 'test passed'"}],
                    temperature=0.1,
                    max_tokens=10,
                )
            else:
                print(f"  ⚠️  No test case for {name}")
                continue

            if "test passed" in response.lower():
                print(f"  ✓ {name} provider working correctly")
            else:
                print(f"  ⚠️  {name} provider responded but may have issues")
                print(f"  Response: {response[:100]}...")

        except Exception as e:
            print(f"  ❌ {name} provider failed: {e}")
            all_passed = False

    print()
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed - check API keys and network connectivity")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_providers())
    sys.exit(0 if success else 1)
