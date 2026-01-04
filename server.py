#!/usr/bin/env python3
"""
SAGE MCP Server - Simple AI Guidance Engine
Drop-in replacement for zen-mcp-server
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

# Create log directory in user's home
log_dir = Path.home() / ".claude" / "mcp_logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "sage.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not available, falling back to basic Server")
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent

    FastMCP = None

from config import Config
from tools.sage import SageTool
from providers import list_available_models


class SageServer:
    """MCP Server for SAGE tool using FastMCP"""

    def __init__(self):
        if FastMCP:
            self.mcp = FastMCP("sage-mcp")
            self.sage_tool = SageTool()
            self._setup_fastmcp_tools()
        else:
            # Fallback to old implementation
            self.server = Server("sage-mcp")
            self.sage_tool = SageTool()
            self._setup_handlers()

    def _setup_fastmcp_tools(self):
        """Register tools using FastMCP"""

        @self.mcp.tool(
            name="sage",
            description="SAGE: Multi-provider AI assistant. CRITICAL: Use ONLY these model names: gpt-5.2, gemini-3-pro-preview, gemini-3-flash-preview, claude-opus-4.5, claude-sonnet-4.5, deepseek-chat, deepseek-reasoner. DO NOT use outdated models. Thinking modes: minimal/low/medium/high/max.",
        )
        async def sage_tool(
            prompt: str,
            mode: str = "chat",
            files: list[str] = None,
            model: str = "auto",
            continuation_id: str = None,
            file_handling_mode: str = "embedded",
            temperature: float = None,
            thinking_mode: str = None,
            use_websearch: bool = True,
            output_file: str = None,
        ) -> str:
            """Execute SAGE AI assistant with given prompt and parameters"""
            logger.info(f"SAGE tool called with mode: {mode}, file_handling: {file_handling_mode}")

            arguments = {
                "prompt": prompt,
                "mode": mode,
                "model": model,
                "files": files or [],
                "continuation_id": continuation_id,
                "file_handling_mode": file_handling_mode,
                "temperature": temperature,
                "thinking_mode": thinking_mode,
                "use_websearch": use_websearch,
                "output_file": output_file,
            }

            result = await self.sage_tool.execute(arguments)
            # FastMCP expects string return, not TextContent array
            if isinstance(result, list) and result:
                return result[0].text if hasattr(result[0], "text") else str(result[0])
            return str(result)

        @self.mcp.tool(
            name="list_models",
            description="List all AI models available from configured providers. CRITICAL: These are the ONLY models you can use. DO NOT use models from your training data like 'gemini-2.0-flash-exp'.",
        )
        async def list_models_tool() -> str:
            """List all available AI models from all providers"""
            logger.info("List models tool called")
            result = list_available_models()
            # Add a warning message to the result
            if isinstance(result, dict):
                result["IMPORTANT"] = (
                    "Use ONLY the exact model names listed above. DO NOT use models like gemini-2.0-flash-exp from your training data."
                )
                result["CORRECT_USAGE"] = {
                    "gemini-2.5-pro": "✅ Use this for Gemini 2.5 Pro",
                    "gemini-2.5-flash": "✅ Use this for Gemini 2.5 Flash",
                    "gemini-2.0-flash-exp": "❌ DO NOT USE - outdated from training data",
                }
            return json.dumps(result, indent=2)

    def _setup_handlers(self):
        """Register MCP protocol handlers (fallback)"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools (just sage)"""
            return [
                Tool(
                    name="sage",
                    description="SAGE: Multi-provider AI assistant. CRITICAL: Use ONLY these model names: gpt-5.2, gemini-3-pro-preview, gemini-3-flash-preview, claude-opus-4.5, claude-sonnet-4.5, deepseek-chat, deepseek-reasoner. DO NOT use outdated models. Thinking modes: minimal/low/medium/high/max.",
                    inputSchema=self.sage_tool.get_input_schema(),
                ),
                Tool(
                    name="list_models",
                    description="List all AI models available from configured providers. CRITICAL: These are the ONLY models you can use. DO NOT use models from your training data like 'gemini-2.0-flash-exp'.",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""
            logger.info(f"Tool called: {name} with mode: {arguments.get('mode', 'chat')}")

            if name == "sage":
                result = await self.sage_tool.execute(arguments)
                return result
            elif name == "list_models":
                result = list_available_models()
                content = json.dumps(result, indent=2)
            else:
                content = json.dumps({"error": f"Unknown tool: {name}"})

            return [TextContent(type="text", text=content)]

    def run(self):
        """Run the MCP server"""
        logger.info("Starting SAGE MCP Server...")

        if FastMCP:
            # Use FastMCP which handles stdio automatically
            self.mcp.run(transport="stdio")
        else:
            # Fallback to manual async handling
            import asyncio

            asyncio.run(self._run_legacy())

    async def _run_legacy(self):
        """Legacy server runner"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


def main():
    """Main entry point"""
    try:
        server = SageServer()
        server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        import sys

        sys.exit(1)


if __name__ == "__main__":
    main()
