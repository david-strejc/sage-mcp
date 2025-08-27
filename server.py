#!/usr/bin/env python3
"""
SAGE MCP Server - Simple AI Guidance Engine
Drop-in replacement for zen-mcp-server
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from config import Config
from tools.sage import SageTool
from providers import list_available_models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SageServer:
    """MCP Server for SAGE tool"""
    
    def __init__(self):
        self.server = Server("sage-mcp")
        self.sage_tool = SageTool()
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Register MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools (just sage)"""
            return [
                Tool(
                    name="sage",
                    description="Universal AI assistant for development tasks",
                    inputSchema=self.sage_tool.get_input_schema()
                ),
                Tool(
                    name="list_models",
                    description="List available AI models",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
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
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting SAGE MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

def main():
    """Main entry point"""
    try:
        server = SageServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()