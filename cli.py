#!/usr/bin/env python3
"""
SAGE CLI - Command line interface for direct usage
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from tools.sage import SageTool
from providers import list_available_models

async def main():
    parser = argparse.ArgumentParser(
        description="SAGE - Simple AI Guidance Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sage chat "How do I implement OAuth2?"
  sage analyze /path/to/code --prompt "Review this architecture"
  sage debug /path/to/error.log --prompt "Why is this failing?"
  sage review /path/to/file.py --prompt "Security review"
  sage test /path/to/module.py --prompt "Generate unit tests"
  
Available modes:
  chat     - General discussion
  analyze  - Code/architecture analysis
  review   - Code review
  debug    - Troubleshooting
  plan     - Project planning
  test     - Test generation
  refactor - Code improvement
  think    - Deep reasoning
        """
    )
    
    # Positional argument for mode
    parser.add_argument(
        "mode",
        choices=["chat", "analyze", "review", "debug", "plan", "test", "refactor", "think"],
        help="Operation mode"
    )
    
    # Main arguments
    parser.add_argument(
        "prompt",
        help="Your question or request"
    )
    
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to include (optional)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--model",
        default="auto",
        help="AI model to use (default: auto)"
    )
    
    parser.add_argument(
        "--thread",
        help="Conversation thread ID for context"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit"
    )
    
    args = parser.parse_args()
    
    # List models if requested
    if args.list_models:
        models = list_available_models()
        print(json.dumps(models, indent=2))
        return
    
    # Convert file paths to absolute
    files = []
    if args.files:
        for file_path in args.files:
            abs_path = Path(file_path).resolve()
            if abs_path.exists():
                files.append(str(abs_path))
            else:
                print(f"Warning: File not found: {file_path}", file=sys.stderr)
    
    # Prepare arguments
    tool_args = {
        "mode": args.mode,
        "prompt": args.prompt,
        "files": files,
        "model": args.model
    }
    
    if args.thread:
        tool_args["continuation_id"] = args.thread
    
    # Execute tool
    tool = SageTool()
    result = await tool.execute(tool_args)
    
    # Output result
    if args.json:
        # Extract content from TextContent object
        if result and hasattr(result[0], 'text'):
            print(result[0].text)
        else:
            print(json.dumps({"error": "No response"}, indent=2))
    else:
        if result and hasattr(result[0], 'text'):
            content = result[0].text
            try:
                # Try to parse as JSON for pretty output
                parsed = json.loads(content)
                if "error" in parsed:
                    print(f"Error: {parsed['error']}", file=sys.stderr)
                    sys.exit(1)
                else:
                    print(content)
            except json.JSONDecodeError:
                # Not JSON, print as is
                print(content)
        else:
            print("No response", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())