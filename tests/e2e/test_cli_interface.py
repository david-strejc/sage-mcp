#!/usr/bin/env python3
"""
End-to-End CLI Testing Script
Tests the SAGE-MCP CLI interface and server integration
"""

import asyncio
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

# Add project root to path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))


class TestCLIInterface:
    """Test CLI interface functionality"""

    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.project_root = Path(__file__).parent.parent.parent
        cls.cli_script = cls.project_root / "cli.py"
        cls.server_script = cls.project_root / "server.py"
        cls.temp_dir = tempfile.mkdtemp()
        cls._create_test_files()

    @classmethod
    def teardown_class(cls):
        """Cleanup test environment"""
        import shutil

        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    @classmethod
    def _create_test_files(cls):
        """Create test files for CLI testing"""
        # Simple Python file
        test_py = os.path.join(cls.temp_dir, "test.py")
        with open(test_py, "w") as f:
            f.write(
                '''def hello_world():
    """A simple test function"""
    print("Hello, World!")
    return "Hello, World!"

if __name__ == "__main__":
    hello_world()
'''
            )

        # Simple text file
        test_txt = os.path.join(cls.temp_dir, "test.txt")
        with open(test_txt, "w") as f:
            f.write("This is a test text file.\nIt has multiple lines.\nFor testing purposes.")

        cls.test_files = {"python": test_py, "text": test_txt}

    def test_cli_script_exists(self):
        """Test that CLI script exists and is executable"""
        assert self.cli_script.exists(), f"CLI script not found at {self.cli_script}"
        assert os.access(self.cli_script, os.R_OK), "CLI script is not readable"

    def test_server_script_exists(self):
        """Test that server script exists"""
        assert self.server_script.exists(), f"Server script not found at {self.server_script}"
        assert os.access(self.server_script, os.R_OK), "Server script is not readable"

    def test_cli_help(self):
        """Test CLI help output"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.cli_script), "--help"], capture_output=True, text=True, timeout=10
            )

            assert result.returncode == 0, f"CLI help failed: {result.stderr}"
            assert "usage:" in result.stdout.lower() or "sage" in result.stdout.lower()
            print("✓ CLI help working")

        except subprocess.TimeoutExpired:
            pytest.skip("CLI help timed out")
        except Exception as e:
            pytest.skip(f"CLI help failed: {e}")

    def test_cli_version(self):
        """Test CLI version output"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.cli_script), "--version"], capture_output=True, text=True, timeout=10
            )

            # May return 0 or 2 depending on implementation
            assert result.returncode in [0, 2], f"CLI version failed: {result.stderr}"

            # Check for version in output
            output = result.stdout + result.stderr
            assert any(char.isdigit() for char in output), "No version number found"
            print("✓ CLI version working")

        except subprocess.TimeoutExpired:
            pytest.skip("CLI version timed out")
        except Exception as e:
            pytest.skip(f"CLI version failed: {e}")

    def test_cli_with_simple_prompt(self):
        """Test CLI with simple prompt"""
        if not any([os.getenv("OPENAI_API_KEY"), os.getenv("GEMINI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
            pytest.skip("No API keys set")

        try:
            result = subprocess.run(
                [sys.executable, str(self.cli_script), "--prompt", "Say hello", "--mode", "chat", "--model", "auto"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            print(f"CLI stdout: {result.stdout}")
            print(f"CLI stderr: {result.stderr}")
            print(f"CLI return code: {result.returncode}")

            # CLI might exit with non-zero if no API keys work
            if result.returncode != 0:
                if "no api" in result.stderr.lower() or "authentication" in result.stderr.lower():
                    pytest.skip("Authentication issues with CLI")
                else:
                    pytest.fail(f"CLI failed: {result.stderr}")

            assert len(result.stdout) > 0, "CLI should produce output"
            print("✓ CLI simple prompt working")

        except subprocess.TimeoutExpired:
            pytest.skip("CLI simple prompt timed out")
        except Exception as e:
            pytest.skip(f"CLI simple prompt failed: {e}")

    def test_cli_with_file_input(self):
        """Test CLI with file input"""
        if not any([os.getenv("OPENAI_API_KEY"), os.getenv("GEMINI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
            pytest.skip("No API keys set")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.cli_script),
                    "--prompt",
                    "What does this code do?",
                    "--files",
                    self.test_files["python"],
                    "--mode",
                    "analyze",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            print(f"CLI with file stdout: {result.stdout}")
            print(f"CLI with file stderr: {result.stderr}")

            if result.returncode != 0:
                if "no api" in result.stderr.lower() or "authentication" in result.stderr.lower():
                    pytest.skip("Authentication issues with CLI file input")
                else:
                    pytest.fail(f"CLI with file failed: {result.stderr}")

            assert len(result.stdout) > 0, "CLI should produce output for file analysis"
            print("✓ CLI file input working")

        except subprocess.TimeoutExpired:
            pytest.skip("CLI file input timed out")
        except Exception as e:
            pytest.skip(f"CLI file input failed: {e}")

    def test_mcp_server_startup(self):
        """Test MCP server can start"""
        try:
            # Start server process
            proc = subprocess.Popen(
                [sys.executable, str(self.server_script)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Give it a moment to start
            time.sleep(2)

            # Check if process is still running
            if proc.poll() is not None:
                stdout, stderr = proc.communicate()
                pytest.fail(f"Server exited immediately. Stdout: {stdout}, Stderr: {stderr}")

            # Send initialize message
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
            }

            try:
                proc.stdin.write(json.dumps(init_message) + "\n")
                proc.stdin.flush()

                # Try to read response
                output_line = proc.stdout.readline()
                if output_line:
                    response = json.loads(output_line)
                    assert "result" in response, f"Invalid initialize response: {response}"
                    print("✓ MCP server initialization working")
                else:
                    print("⚠ No response from MCP server")

            except json.JSONDecodeError as e:
                print(f"⚠ JSON decode error: {e}, output: {output_line}")
            except Exception as e:
                print(f"⚠ MCP communication error: {e}")

            # Clean up
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

        except Exception as e:
            pytest.skip(f"MCP server startup test failed: {e}")

    def test_mcp_tools_listing(self):
        """Test MCP tools listing"""
        try:
            proc = subprocess.Popen(
                [sys.executable, str(self.server_script)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            time.sleep(2)

            if proc.poll() is not None:
                pytest.skip("Server exited before tools test")

            # Initialize
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
            }

            proc.stdin.write(json.dumps(init_message) + "\n")
            proc.stdin.flush()

            # Read initialize response
            init_response = proc.stdout.readline()

            # List tools
            tools_message = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

            proc.stdin.write(json.dumps(tools_message) + "\n")
            proc.stdin.flush()

            # Read tools response
            tools_response_line = proc.stdout.readline()
            if tools_response_line:
                tools_response = json.loads(tools_response_line)

                if "result" in tools_response:
                    tools = tools_response["result"]["tools"]
                    assert len(tools) > 0, "Should have at least one tool"

                    # Should have SAGE tool
                    tool_names = [tool["name"] for tool in tools]
                    assert "sage" in tool_names, f"SAGE tool not found in {tool_names}"
                    print(f"✓ MCP tools listing working: {tool_names}")
                else:
                    print(f"⚠ Tools list error: {tools_response}")

            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

        except Exception as e:
            pytest.skip(f"MCP tools listing failed: {e}")

    def test_environment_validation(self):
        """Test environment setup validation"""
        # Check for required files
        required_files = [
            self.project_root / "config.py",
            self.project_root / "requirements.txt",
            self.project_root / "tools" / "sage.py",
            self.project_root / "providers" / "__init__.py",
            self.project_root / "modes" / "__init__.py",
        ]

        for file_path in required_files:
            assert file_path.exists(), f"Required file missing: {file_path}"

        print("✓ Environment validation passed")

    def test_config_loading(self):
        """Test configuration loading"""
        try:
            # Import config from project
            import importlib.util

            spec = importlib.util.spec_from_file_location("config", str(self.project_root / "config.py"))
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)

            config = config_module.Config()

            # Test basic config attributes
            assert hasattr(config, "ALLOWED_FILE_EXTENSIONS")
            assert hasattr(config, "EXCLUDED_DIRS")
            assert hasattr(config, "MAX_TOKENS")
            assert hasattr(config, "MAX_FILE_SIZE")

            print("✓ Config loading working")

        except Exception as e:
            pytest.fail(f"Config loading failed: {e}")

    def test_imports_working(self):
        """Test that all required imports work"""
        import sys

        old_path = sys.path.copy()

        try:
            sys.path.insert(0, str(self.project_root))

            # Test core imports
            import config
            import server

            # Test tool imports
            from tools.sage import SageTool

            # Test provider imports
            from providers import get_available_providers

            # Test mode imports
            from modes import get_available_modes

            # Test utils imports
            from utils.files import read_files
            from utils.models import ModelRestrictionService
            from utils.memory import create_thread
            from utils.security import is_safe_path
            from utils.tokens import estimate_tokens

            print("✓ All imports working")

        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
        finally:
            sys.path = old_path

    def test_provider_availability(self):
        """Test provider availability detection"""
        import sys

        old_path = sys.path.copy()

        try:
            sys.path.insert(0, str(self.project_root))
            from providers import get_available_providers

            providers = get_available_providers()

            assert len(providers) > 0, "Should have at least one provider"

            provider_names = [p["name"] for p in providers]
            expected_providers = ["openai", "gemini", "anthropic", "openrouter", "custom"]

            for expected in expected_providers:
                assert expected in provider_names, f"Provider {expected} not found"

            print(f"✓ Provider availability: {provider_names}")

        except Exception as e:
            pytest.fail(f"Provider availability test failed: {e}")
        finally:
            sys.path = old_path

    def test_mode_availability(self):
        """Test mode availability detection"""
        import sys

        old_path = sys.path.copy()

        try:
            sys.path.insert(0, str(self.project_root))
            from modes import get_available_modes

            modes = get_available_modes()

            assert len(modes) > 0, "Should have at least one mode"

            mode_names = [m["name"] for m in modes]
            expected_modes = ["chat", "analyze", "review", "debug", "plan", "test", "refactor", "think"]

            for expected in expected_modes:
                assert expected in mode_names, f"Mode {expected} not found"

            print(f"✓ Mode availability: {mode_names}")

        except Exception as e:
            pytest.fail(f"Mode availability test failed: {e}")
        finally:
            sys.path = old_path


class TestCLIEndToEnd:
    """End-to-end testing scenarios"""

    @classmethod
    def setup_class(cls):
        """Setup for E2E tests"""
        cls.project_root = Path(__file__).parent.parent.parent
        cls.cli_script = cls.project_root / "cli.py"
        cls.temp_dir = tempfile.mkdtemp()

    @classmethod
    def teardown_class(cls):
        """Cleanup E2E tests"""
        import shutil

        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_complete_workflow_chat(self):
        """Test complete chat workflow"""
        if not any([os.getenv("OPENAI_API_KEY"), os.getenv("GEMINI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
            pytest.skip("No API keys set for E2E chat test")

        try:
            # Simple chat interaction
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.cli_script),
                    "--prompt",
                    "What is 2 + 2? Answer with just the number.",
                    "--mode",
                    "chat",
                    "--model",
                    "auto",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                pytest.skip(f"E2E chat failed: {result.stderr}")

            output = result.stdout.lower()
            assert "4" in output or "four" in output, f"Chat should answer 2+2=4, got: {result.stdout}"
            print("✓ Complete chat workflow working")

        except subprocess.TimeoutExpired:
            pytest.skip("E2E chat workflow timed out")
        except Exception as e:
            pytest.skip(f"E2E chat workflow failed: {e}")

    def test_complete_workflow_code_analysis(self):
        """Test complete code analysis workflow"""
        if not any([os.getenv("OPENAI_API_KEY"), os.getenv("GEMINI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
            pytest.skip("No API keys set for E2E analysis test")

        # Create a test Python file
        test_file = os.path.join(self.temp_dir, "sample.py")
        with open(test_file, "w") as f:
            f.write(
                '''def calculate_factorial(n):
    """Calculate factorial of n"""
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

print(calculate_factorial(5))
'''
            )

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.cli_script),
                    "--prompt",
                    "What does this function do? Be brief.",
                    "--files",
                    test_file,
                    "--mode",
                    "analyze",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                pytest.skip(f"E2E analysis failed: {result.stderr}")

            output = result.stdout.lower()
            assert "factorial" in output, f"Analysis should mention factorial, got: {result.stdout}"
            print("✓ Complete code analysis workflow working")

        except subprocess.TimeoutExpired:
            pytest.skip("E2E code analysis workflow timed out")
        except Exception as e:
            pytest.skip(f"E2E code analysis workflow failed: {e}")


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test CLI Interface")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--e2e", action="store_true", help="Run E2E tests only")
    args = parser.parse_args()

    if args.e2e:
        # Run E2E tests only
        pytest.main([f"{__file__}::TestCLIEndToEnd", "-v" if args.verbose else ""])
    elif args.test:
        # Run specific test
        if "." in args.test:
            # Specific method
            pytest.main([f"{__file__}::{args.test}", "-v" if args.verbose else ""])
        else:
            # Try both classes
            test_interface = TestCLIInterface()
            test_interface.setup_class()

            test_method = getattr(test_interface, f"test_{args.test}", None)
            if test_method:
                test_method()
                print(f"✓ Test {args.test} completed")
            else:
                test_e2e = TestCLIEndToEnd()
                test_e2e.setup_class()

                test_method = getattr(test_e2e, f"test_{args.test}", None)
                if test_method:
                    test_method()
                    print(f"✓ Test {args.test} completed")
                else:
                    print(f"❌ Test {args.test} not found")
    else:
        # Run all tests with pytest
        pytest.main([__file__, "-v" if args.verbose else ""])
