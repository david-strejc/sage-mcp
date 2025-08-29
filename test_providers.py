#!/usr/bin/env python3
"""Test provider initialization"""

import os
import sys
sys.path.insert(0, '/home/david/Work/Programming/sage/sage-mcp')

from providers import initialize_providers, PROVIDERS, list_available_models

# Check API keys
print("API Keys present:")
print(f"  GOOGLE_API_KEY: {'✓' if os.getenv('GOOGLE_API_KEY') else '✗'}")
print(f"  OPENAI_API_KEY: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
print(f"  ANTHROPIC_API_KEY: {'✓' if os.getenv('ANTHROPIC_API_KEY') else '✗'}")
print()

# Initialize providers
print("Initializing providers...")
initialize_providers()
print()

print("Available providers:")
for name, provider in PROVIDERS.items():
    models = provider.list_models()
    print(f"  {name}: {len(models)} models - {', '.join(models[:3])}...")
print()

# List all available models
all_models = list_available_models()
print("All available models:")
for model in all_models["available_models"]:
    print(f"  - {model}")
print()

print("Models by provider:")
for provider, models in all_models["models_by_provider"].items():
    print(f"  {provider}: {models}")