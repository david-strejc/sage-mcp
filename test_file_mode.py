#!/usr/bin/env python3
"""Test file handling mode functionality"""

import asyncio
import json
from tools.sage import SageTool

async def test_file_handling():
    tool = SageTool()
    
    # Test with summary mode
    print("Testing file_handling_mode='summary'...")
    arguments = {
        "prompt": "What does this file do?",
        "files": ["/home/david/Work/Programming/sage/sage-mcp/tools/sage.py"],
        "file_handling_mode": "summary",
        "mode": "chat"
    }
    
    result = await tool.execute(arguments)
    print("\n=== SUMMARY MODE RESULT ===")
    if isinstance(result, list) and result:
        print(result[0].text if hasattr(result[0], 'text') else str(result[0]))
    else:
        print(str(result))
    
    print("\n" + "="*50 + "\n")
    
    # Test with embedded mode (default)
    print("Testing file_handling_mode='embedded' (default)...")
    arguments = {
        "prompt": "What does this file do?",
        "files": ["/home/david/Work/Programming/sage/sage-mcp/tools/sage.py"],
        "file_handling_mode": "embedded",
        "mode": "chat"
    }
    
    result = await tool.execute(arguments)
    print("\n=== EMBEDDED MODE RESULT ===")
    if isinstance(result, list) and result:
        text = result[0].text if hasattr(result[0], 'text') else str(result[0])
        # Truncate for readability
        if len(text) > 500:
            print(text[:500] + "...[truncated]")
        else:
            print(text)
    else:
        print(str(result))

if __name__ == "__main__":
    asyncio.run(test_file_handling())