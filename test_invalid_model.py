#!/usr/bin/env python3
"""Test invalid model name handling"""

import asyncio
import sys
sys.path.insert(0, '/home/david/Work/Programming/sage/sage-mcp')

from tools.sage import SageTool

async def test_invalid_model():
    """Test that invalid model names provide helpful error messages"""
    tool = SageTool()
    
    # Test with completely invalid model name
    print("Testing with invalid model 'wtf'...")
    try:
        result = await tool.execute({
            "prompt": "Hello",
            "model": "wtf"
        })
        print("ERROR: Should have raised an error!")
    except ValueError as e:
        print(f"Got expected error:\n{e}\n")
        # Check that error contains helpful info
        error_str = str(e)
        assert "wtf" in error_str, "Error should mention the invalid model"
        assert "AVAILABLE MODELS" in error_str or "gemini" in error_str, "Error should list available models"
        print("✓ Error message contains helpful information\n")
    
    # Test with a model that looks real but doesn't exist
    print("Testing with non-existent model 'o3-mini'...")
    try:
        result = await tool.execute({
            "prompt": "Hello",
            "model": "o3-mini"
        })
        print("ERROR: Should have raised an error!")
    except ValueError as e:
        print(f"Got expected error:\n{e}\n")
        error_str = str(e)
        assert "o3-mini" in error_str, "Error should mention the invalid model"
        assert "does NOT exist" in error_str or "not recognized" in error_str, "Error should explain model doesn't exist"
        print("✓ Error message warns about non-existent model\n")
    
    # Test with valid model (should work or give API key error)
    print("Testing with valid model 'gemini-2.5-flash'...")
    try:
        result = await tool.execute({
            "prompt": "Say just 'Hello'",
            "model": "gemini-2.5-flash"
        })
        print(f"Success: {result[0].text[:100]}...")
        print("✓ Valid model works correctly\n")
    except Exception as e:
        print(f"Got error (might be API key issue): {e}")
        if "API" in str(e) or "key" in str(e).lower():
            print("✓ Valid model recognized but API key issue\n")
        else:
            raise

if __name__ == "__main__":
    asyncio.run(test_invalid_model())
    print("All tests passed!")