#!/usr/bin/env python3
"""Test error message formatting"""

import asyncio
import json
import sys
sys.path.insert(0, '/home/david/Work/Programming/sage/sage-mcp')

from tools.sage import SageTool

async def test_error_formatting():
    """Test that error messages are properly formatted for JSON"""
    tool = SageTool()
    
    # Test with invalid model
    print("Testing error format with invalid model 'wtf'...")
    try:
        result = await tool.execute({
            "prompt": "Hello",
            "model": "wtf"
        })
    except Exception as e:
        error_msg = str(e)
        print(f"Error message: {error_msg}")
        
        # Try to create JSON response (like MCP would)
        response = {
            "error": f"SAGE execution failed: {error_msg}"
        }
        
        # Check if it's JSON-serializable and single-line friendly
        json_str = json.dumps(response)
        print(f"\nJSON output:\n{json_str}")
        
        # Parse it back to verify it's valid JSON
        parsed = json.loads(json_str)
        print("✓ Valid JSON output")
        
        # Verify it contains helpful info
        assert "Available models:" in error_msg
        assert "gemini" in error_msg or "gpt" in error_msg or "o3" in error_msg
        print("✓ Error message contains available models")
        
        # Verify it's concise (not multi-paragraph)
        assert len(error_msg) < 300, f"Error message too long: {len(error_msg)} chars"
        print("✓ Error message is concise")

if __name__ == "__main__":
    asyncio.run(test_error_formatting())
    print("\nAll formatting tests passed!")