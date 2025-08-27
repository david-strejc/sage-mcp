#!/usr/bin/env python3
"""
Real-world Claude + MCP integration tests
Tests actual claude command with MCP server configuration
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

class TestClaudeMCPIntegration:
    """Test real Claude CLI with MCP server"""
    
    @classmethod
    def setup_class(cls):
        """Setup for integration tests"""
        cls.project_root = Path(__file__).parent.parent.parent
        cls.server_script = cls.project_root / "server.py"
        cls.claude_binary = "/usr/bin/claude"
        
        # Create MCP config for testing
        cls.mcp_config = {
            "mcpServers": {
                "sage": {
                    "command": sys.executable,
                    "args": [str(cls.server_script)],
                    "env": {}
                }
            }
        }
        
        # Write config to temp file
        cls.config_file = cls.project_root / "test_mcp_config.json"
        with open(cls.config_file, 'w') as f:
            json.dump(cls.mcp_config, f, indent=2)
    
    @classmethod
    def teardown_class(cls):
        """Cleanup"""
        if cls.config_file.exists():
            cls.config_file.unlink()
    
    def test_mcp_server_connection(self):
        """Test that Claude can connect to our MCP server"""
        if not os.path.exists(self.claude_binary):
            pytest.skip("Claude binary not found at /usr/bin/claude")
        
        # Test with a simple echo to check connection
        result = subprocess.run([
            self.claude_binary,
            "--strict-mcp-config",
            "--mcp-config", str(self.config_file),
            "--dangerously-skip-permissions",
            "-p", "List available tools"
        ], capture_output=True, text=True, timeout=30)
        
        # Check that sage tools are mentioned
        output = result.stdout + result.stderr
        assert "sage" in output.lower() or "mcp__sage" in output.lower(), \
            f"SAGE MCP tools not found in output: {output}"
        
        print("✓ Claude connected to SAGE MCP server")
    
    def test_sage_tool_invocation(self):
        """Test that Claude can invoke the sage tool"""
        if not os.path.exists(self.claude_binary):
            pytest.skip("Claude binary not found")
        
        # Test invoking the sage tool
        result = subprocess.run([
            self.claude_binary,
            "--strict-mcp-config",
            "--mcp-config", str(self.config_file),
            "--dangerously-skip-permissions",
            "-p", "Use the sage tool to calculate 2+2"
        ], capture_output=True, text=True, timeout=30)
        
        output = result.stdout.lower()
        assert "4" in output or "four" in output, \
            f"Expected answer to 2+2, got: {result.stdout}"
        
        print("✓ Claude successfully invoked SAGE tool")
    
    def test_list_models_tool(self):
        """Test the list_models MCP tool"""
        if not os.path.exists(self.claude_binary):
            pytest.skip("Claude binary not found")
        
        result = subprocess.run([
            self.claude_binary,
            "--strict-mcp-config",
            "--mcp-config", str(self.config_file),
            "--dangerously-skip-permissions",
            "-p", "Use the list_models tool to show available AI models"
        ], capture_output=True, text=True, timeout=30)
        
        output = result.stdout
        # Check for provider names or model indicators
        assert any(provider in output.lower() for provider in ["gemini", "openai", "anthropic", "gpt", "claude"]), \
            f"No model providers found in output: {output}"
        
        print("✓ list_models tool working")
    
    def test_sage_with_mode(self):
        """Test sage tool with different modes"""
        if not os.path.exists(self.claude_binary):
            pytest.skip("Claude binary not found")
        
        # Test with analyze mode
        result = subprocess.run([
            self.claude_binary, 
            "--strict-mcp-config",
            "--mcp-config", str(self.config_file),
            "--dangerously-skip-permissions",
            "-p", "Use the sage tool with mode 'analyze' to explain what a Python decorator is"
        ], capture_output=True, text=True, timeout=30)
        
        output = result.stdout
        assert "decorator" in output.lower() or "function" in output.lower(), \
            f"Expected explanation of decorators, got: {output}"
        
        print("✓ SAGE tool with mode parameter working")
    
    def test_mcp_error_handling(self):
        """Test MCP server error handling"""
        if not os.path.exists(self.claude_binary):
            pytest.skip("Claude binary not found")
        
        # Test with invalid tool call
        result = subprocess.run([
            self.claude_binary,
            "--strict-mcp-config",
            "--mcp-config", str(self.config_file),
            "--dangerously-skip-permissions",
            "-p", "Use a tool called 'nonexistent_tool' to do something"
        ], capture_output=True, text=True, timeout=30)
        
        # Should gracefully handle or mention tool doesn't exist
        assert result.returncode == 0 or "not available" in result.stdout.lower() or \
               "don't have" in result.stdout.lower() or "cannot" in result.stdout.lower(), \
            f"Unexpected error handling: {result.stdout}"
        
        print("✓ MCP error handling working")

if __name__ == "__main__":
    # Allow running specific test
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", help="Specific test to run")
    args = parser.parse_args()
    
    test_class = TestClaudeMCPIntegration()
    test_class.setup_class()
    
    try:
        if args.test:
            test_method = getattr(test_class, f"test_{args.test}", None)
            if test_method:
                test_method()
                print(f"✓ Test {args.test} completed")
            else:
                print(f"Test {args.test} not found")
        else:
            # Run all tests
            for attr_name in dir(test_class):
                if attr_name.startswith("test_"):
                    test_method = getattr(test_class, attr_name)
                    print(f"Running {attr_name}...")
                    try:
                        test_method()
                    except Exception as e:
                        print(f"✗ {attr_name} failed: {e}")
    finally:
        test_class.teardown_class()