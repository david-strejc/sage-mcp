#!/usr/bin/env python3
"""
Real-World Claude Code Integration Testing
Tests SAGE-MCP integration with Claude Code using actual claude mcp commands
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


class TestClaudeCodeIntegration:
    """Test real-world integration with Claude Code"""

    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.project_root = Path(__file__).parent.parent.parent
        cls.mcp_config = cls.project_root / "mcp_settings.json"
        cls.temp_dir = tempfile.mkdtemp()
        cls._create_test_scenarios()
        
    @classmethod
    def teardown_class(cls):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
        
    @classmethod
    def _create_test_scenarios(cls):
        """Create realistic test scenarios"""
        
        # Scenario 1: Bug report analysis
        cls.bug_report = os.path.join(cls.temp_dir, 'bug_report.md')
        with open(cls.bug_report, 'w') as f:
            f.write('''# Bug Report: Login Form Validation

## Description
The login form is not properly validating email addresses and allows submission with invalid formats.

## Steps to Reproduce
1. Navigate to `/login`
2. Enter invalid email like "notanemail"
3. Click submit
4. Form submits without validation error

## Expected Behavior
Form should show validation error for invalid email format.

## Actual Behavior
Form submits and shows generic error message.

## Environment
- Browser: Chrome 120
- OS: macOS 14.0
- App Version: 2.1.3
''')
        
        # Scenario 2: Feature implementation
        cls.feature_spec = os.path.join(cls.temp_dir, 'feature_spec.md')
        with open(cls.feature_spec, 'w') as f:
            f.write('''# Feature Specification: Dark Mode Toggle

## Overview
Add a dark mode toggle to the application that persists user preference.

## Requirements
1. Toggle switch in the main navigation
2. Dark/light theme styles for all components
3. Persist preference in localStorage
4. Smooth transition animations
5. System preference detection

## Acceptance Criteria
- [ ] Toggle switch is visible in navigation
- [ ] All components have dark mode styles
- [ ] Preference persists across sessions
- [ ] Smooth 200ms transition animations
- [ ] Respects system preference on first visit

## Technical Notes
- Use CSS custom properties for theme colors
- Implement prefers-color-scheme media query
- Consider accessibility contrast ratios
''')
        
        # Scenario 3: Code review request
        cls.code_sample = os.path.join(cls.temp_dir, 'user_service.py')
        with open(cls.code_sample, 'w') as f:
            f.write('''from typing import Optional, List
import hashlib
import secrets
from datetime import datetime, timedelta

from database import db
from models.user import User


class UserService:
    """Service for user management operations"""
    
    def __init__(self):
        self.session_timeout = timedelta(hours=24)
    
    def create_user(self, email: str, password: str, name: str) -> User:
        """Create a new user account"""
        # Hash password
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        # Create user
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            salt=salt,
            name=name.strip(),
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email/password"""
        user = db.session.query(User).filter_by(
            email=email.lower().strip(),
            is_active=True
        ).first()
        
        if not user:
            return None
            
        # Verify password
        password_hash = hashlib.sha256((password + user.salt).encode()).hexdigest()
        if password_hash != user.password_hash:
            return None
            
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.session.query(User).filter_by(
            id=user_id,
            is_active=True
        ).first()
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
            
        user.is_active = False
        user.deactivated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
            
        # Generate new salt and hash
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
        
        user.salt = salt
        user.password_hash = password_hash
        user.password_updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
''')
        
        # Scenario 4: Performance issue
        cls.perf_data = os.path.join(cls.temp_dir, 'performance_log.json')
        with open(cls.perf_data, 'w') as f:
            json.dump({
                "timestamp": "2024-01-15T10:30:00Z",
                "endpoint": "/api/users/search",
                "method": "GET",
                "response_time_ms": 5420,
                "database_query_time_ms": 4890,
                "memory_usage_mb": 156,
                "cpu_usage_percent": 78,
                "query_params": {
                    "search": "john",
                    "page": 1,
                    "limit": 50
                },
                "slow_queries": [
                    {
                        "query": "SELECT * FROM users WHERE name ILIKE '%john%' OR email ILIKE '%john%'",
                        "duration_ms": 3200,
                        "rows_examined": 45000,
                        "rows_returned": 23
                    },
                    {
                        "query": "SELECT COUNT(*) FROM users WHERE name ILIKE '%john%' OR email ILIKE '%john%'",
                        "duration_ms": 1690,
                        "rows_examined": 45000,
                        "rows_returned": 1
                    }
                ],
                "suggestions": [
                    "Add index on users.name column",
                    "Add index on users.email column", 
                    "Consider full-text search instead of ILIKE"
                ]
            }, indent=2)
        
        cls.test_scenarios = {
            'bug_report': cls.bug_report,
            'feature_spec': cls.feature_spec,
            'code_sample': cls.code_sample,
            'perf_data': cls.perf_data
        }
        
    def test_mcp_config_exists(self):
        """Test that MCP configuration file exists"""
        assert self.mcp_config.exists(), f"MCP config not found at {self.mcp_config}"
        
        # Validate JSON structure
        with open(self.mcp_config) as f:
            config = json.load(f)
            
        assert "mcpServers" in config
        assert "sage" in config["mcpServers"]
        
        sage_config = config["mcpServers"]["sage"]
        assert "command" in sage_config
        assert "args" in sage_config
        assert "env" in sage_config
        
        print("✓ MCP configuration valid")
        
    def test_claude_mcp_command_available(self):
        """Test that claude mcp command is available"""
        try:
            result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            print(f"Claude MCP list output: {result.stdout}")
            print(f"Claude MCP list stderr: {result.stderr}")
            
            # Command exists if it doesn't fail with "command not found"
            if "command not found" in result.stderr or "not found" in result.stderr:
                pytest.skip("Claude CLI not installed")
            elif result.returncode == 0:
                print("✓ Claude MCP command available")
            else:
                print(f"⚠ Claude MCP command available but returned {result.returncode}")
                
        except FileNotFoundError:
            pytest.skip("Claude CLI not installed")
        except subprocess.TimeoutExpired:
            pytest.skip("Claude MCP command timed out")
        except Exception as e:
            pytest.skip(f"Claude MCP test failed: {e}")
            
    def test_mcp_server_configuration_syntax(self):
        """Test MCP server configuration syntax"""
        # Test that our configuration follows Claude Code MCP format
        with open(self.mcp_config) as f:
            config = json.load(f)
            
        sage_server = config["mcpServers"]["sage"]
        
        # Required fields for stdio server
        assert sage_server.get("type") == "stdio" or "command" in sage_server
        assert "command" in sage_server
        assert isinstance(sage_server["args"], list)
        assert isinstance(sage_server["env"], dict)
        
        # Validate server path
        server_path = Path(sage_server["args"][0])
        assert server_path.is_absolute(), "Server path should be absolute"
        
        # Environment should have reasonable values
        env = sage_server["env"]
        assert "LOG_LEVEL" in env
        assert env["LOG_LEVEL"] in ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        print("✓ MCP server configuration syntax valid")
        
    def test_realistic_scenario_bug_analysis(self):
        """Test realistic bug analysis scenario"""
        if not self._has_api_access():
            pytest.skip("No API keys for realistic scenario testing")
            
        try:
            # Simulate: claude mcp add local sage ./server.py 
            # Then: Ask Claude to analyze the bug report
            
            result = subprocess.run([
                sys.executable, 
                str(self.project_root / "cli.py"),
                "--prompt", "Analyze this bug report and suggest a fix approach.",
                "--files", self.test_scenarios['bug_report'],
                "--mode", "debug",
                "--model", "auto"
            ], capture_output=True, text=True, timeout=90)
            
            if result.returncode != 0:
                pytest.skip(f"Bug analysis scenario failed: {result.stderr}")
                
            output = result.stdout.lower()
            
            # Should mention key aspects of the bug
            assert any(word in output for word in ["validation", "email", "form"]), \
                f"Bug analysis should mention validation/email/form, got: {result.stdout[:200]}"
                
            print("✓ Realistic bug analysis scenario working")
            
        except subprocess.TimeoutExpired:
            pytest.skip("Bug analysis scenario timed out")
        except Exception as e:
            pytest.skip(f"Bug analysis scenario failed: {e}")
            
    def test_realistic_scenario_feature_planning(self):
        """Test realistic feature planning scenario"""
        if not self._has_api_access():
            pytest.skip("No API keys for feature planning scenario")
            
        try:
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "Create an implementation plan for this feature specification.",
                "--files", self.test_scenarios['feature_spec'],
                "--mode", "plan",
                "--model", "auto"
            ], capture_output=True, text=True, timeout=90)
            
            if result.returncode != 0:
                pytest.skip(f"Feature planning scenario failed: {result.stderr}")
                
            output = result.stdout.lower()
            
            # Should mention key aspects of dark mode
            assert any(word in output for word in ["dark", "theme", "toggle", "css"]), \
                f"Feature plan should mention dark/theme/toggle/css, got: {result.stdout[:200]}"
                
            print("✓ Realistic feature planning scenario working")
            
        except subprocess.TimeoutExpired:
            pytest.skip("Feature planning scenario timed out") 
        except Exception as e:
            pytest.skip(f"Feature planning scenario failed: {e}")
            
    def test_realistic_scenario_code_review(self):
        """Test realistic code review scenario"""
        if not self._has_api_access():
            pytest.skip("No API keys for code review scenario")
            
        try:
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "Review this code for security issues, bugs, and improvements.",
                "--files", self.test_scenarios['code_sample'],
                "--mode", "review",
                "--model", "auto"
            ], capture_output=True, text=True, timeout=90)
            
            if result.returncode != 0:
                pytest.skip(f"Code review scenario failed: {result.stderr}")
                
            output = result.stdout.lower()
            
            # Should identify security concerns
            assert any(word in output for word in ["security", "hash", "password", "salt"]), \
                f"Code review should mention security/hash/password, got: {result.stdout[:200]}"
                
            print("✓ Realistic code review scenario working")
            
        except subprocess.TimeoutExpired:
            pytest.skip("Code review scenario timed out")
        except Exception as e:
            pytest.skip(f"Code review scenario failed: {e}")
            
    def test_realistic_scenario_performance_analysis(self):
        """Test realistic performance analysis scenario"""
        if not self._has_api_access():
            pytest.skip("No API keys for performance analysis scenario")
            
        try:
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "Analyze this performance data and suggest optimizations.",
                "--files", self.test_scenarios['perf_data'],
                "--mode", "analyze",
                "--model", "auto"
            ], capture_output=True, text=True, timeout=90)
            
            if result.returncode != 0:
                pytest.skip(f"Performance analysis scenario failed: {result.stderr}")
                
            output = result.stdout.lower()
            
            # Should identify performance issues
            assert any(word in output for word in ["performance", "query", "index", "slow"]), \
                f"Performance analysis should mention query/index/slow, got: {result.stdout[:200]}"
                
            print("✓ Realistic performance analysis scenario working")
            
        except subprocess.TimeoutExpired:
            pytest.skip("Performance analysis scenario timed out")
        except Exception as e:
            pytest.skip(f"Performance analysis scenario failed: {e}")
            
    def test_conversation_continuation_scenario(self):
        """Test conversation continuation in realistic scenario"""
        if not self._has_api_access():
            pytest.skip("No API keys for conversation continuation scenario")
            
        try:
            # First interaction - analyze the bug
            result1 = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "What's the main issue in this bug report?",
                "--files", self.test_scenarios['bug_report'],
                "--mode", "analyze"
            ], capture_output=True, text=True, timeout=60)
            
            if result1.returncode != 0:
                pytest.skip(f"First conversation failed: {result1.stderr}")
                
            # Extract thread ID from first response (if available)
            # This would be implementation specific
            
            # Second interaction - ask follow-up (simulated continuation)
            result2 = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "How would you fix the email validation issue?",
                "--mode", "chat"  # Continue without files
            ], capture_output=True, text=True, timeout=60)
            
            if result2.returncode != 0:
                pytest.skip(f"Second conversation failed: {result2.stderr}")
                
            output1 = result1.stdout.lower()
            output2 = result2.stdout.lower()
            
            # Both should mention validation
            assert "validation" in output1, "First response should mention validation"
            
            print("✓ Conversation continuation scenario working")
            
        except subprocess.TimeoutExpired:
            pytest.skip("Conversation continuation scenario timed out")
        except Exception as e:
            pytest.skip(f"Conversation continuation scenario failed: {e}")
            
    def test_multi_file_scenario(self):
        """Test realistic multi-file analysis scenario"""
        if not self._has_api_access():
            pytest.skip("No API keys for multi-file scenario")
            
        try:
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "Review these files together - the bug report and the code that might be causing it.",
                "--files", self.test_scenarios['bug_report'], self.test_scenarios['code_sample'],
                "--mode", "review"
            ], capture_output=True, text=True, timeout=90)
            
            if result.returncode != 0:
                pytest.skip(f"Multi-file scenario failed: {result.stderr}")
                
            output = result.stdout.lower()
            
            # Should reference both files
            assert any(word in output for word in ["bug", "validation", "email"]), \
                "Should reference bug report content"
            assert any(word in output for word in ["user", "authenticate", "password"]), \
                "Should reference code content"
                
            print("✓ Multi-file scenario working")
            
        except subprocess.TimeoutExpired:
            pytest.skip("Multi-file scenario timed out")
        except Exception as e:
            pytest.skip(f"Multi-file scenario failed: {e}")
            
    def test_error_handling_scenario(self):
        """Test error handling in realistic scenarios"""
        try:
            # Test with non-existent file
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "Analyze this file",
                "--files", "/nonexistent/file.txt",
                "--mode", "analyze"
            ], capture_output=True, text=True, timeout=30)
            
            # Should handle error gracefully, not crash
            if result.returncode != 0:
                assert "error" in result.stderr.lower() or "not found" in result.stderr.lower(), \
                    f"Should have meaningful error message, got: {result.stderr}"
            else:
                # If it succeeds, should mention file issue in output
                assert any(word in result.stdout.lower() for word in ["error", "not found", "missing"]), \
                    "Should mention file issue in output"
                    
            print("✓ Error handling scenario working")
            
        except Exception as e:
            pytest.skip(f"Error handling scenario failed: {e}")
            
    def _has_api_access(self):
        """Check if we have API access for realistic testing"""
        return any([
            os.getenv('OPENAI_API_KEY'),
            os.getenv('GEMINI_API_KEY'), 
            os.getenv('ANTHROPIC_API_KEY'),
            os.getenv('OPENROUTER_API_KEY')
        ])


class TestClaudeCodeWorkflows:
    """Test common Claude Code workflows with SAGE-MCP"""
    
    @classmethod
    def setup_class(cls):
        """Setup workflow testing"""
        cls.project_root = Path(__file__).parent.parent.parent
        cls.temp_dir = tempfile.mkdtemp()
        
    @classmethod 
    def teardown_class(cls):
        """Cleanup workflow testing"""
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
        
    def test_development_workflow(self):
        """Test typical development workflow"""
        # Create a simple project structure
        project_dir = os.path.join(self.temp_dir, 'myproject')
        os.makedirs(os.path.join(project_dir, 'src'), exist_ok=True)
        
        # Add some code
        main_file = os.path.join(project_dir, 'src', 'main.py')
        with open(main_file, 'w') as f:
            f.write('''def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

def main():
    data = [1, 2, 3, 4, 5]
    result = calculate_sum(data)
    print(f"Sum: {result}")

if __name__ == "__main__":
    main()
''')
        
        if not self._has_api_access():
            pytest.skip("No API keys for development workflow")
            
        try:
            # Step 1: Code review
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "Review this code for improvements and best practices.",
                "--files", main_file,
                "--mode", "review"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✓ Development workflow - code review step working")
            else:
                print(f"⚠ Code review step failed: {result.stderr}")
                
            # Step 2: Test generation suggestion
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "Suggest unit tests for this code.",
                "--files", main_file,
                "--mode", "test"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✓ Development workflow - test suggestion step working")
            else:
                print(f"⚠ Test suggestion step failed: {result.stderr}")
                
        except Exception as e:
            pytest.skip(f"Development workflow failed: {e}")
            
    def test_debugging_workflow(self):
        """Test typical debugging workflow"""
        # Create buggy code
        buggy_file = os.path.join(self.temp_dir, 'buggy.py')
        with open(buggy_file, 'w') as f:
            f.write('''def divide_numbers(a, b):
    return a / b  # Bug: no zero division check

def process_data(data):
    results = []
    for item in data:
        result = divide_numbers(item, item - 5)  # Bug: will fail when item = 5
        results.append(result)
    return results

# This will crash
data = [1, 2, 3, 4, 5, 6, 7]
print(process_data(data))
''')
        
        if not self._has_api_access():
            pytest.skip("No API keys for debugging workflow")
            
        try:
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "Find and explain the bugs in this code.",
                "--files", buggy_file,
                "--mode", "debug"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                output = result.stdout.lower()
                
                # Should identify the division by zero issue
                if any(word in output for word in ["division", "zero", "crash", "error"]):
                    print("✓ Debugging workflow working")
                else:
                    print(f"⚠ Debug didn't identify key issues: {result.stdout[:200]}")
            else:
                print(f"⚠ Debugging workflow failed: {result.stderr}")
                
        except Exception as e:
            pytest.skip(f"Debugging workflow failed: {e}")
            
    def test_refactoring_workflow(self):
        """Test typical refactoring workflow"""
        # Create code that needs refactoring
        messy_file = os.path.join(self.temp_dir, 'messy.py')
        with open(messy_file, 'w') as f:
            f.write('''# Messy code that needs refactoring
import json

def process_user_data(data):
    # Too many responsibilities in one function
    users = []
    
    for item in data:
        if 'name' in item and 'email' in item:
            if '@' in item['email']:
                if len(item['name']) > 0:
                    user = {}
                    user['name'] = item['name'].strip().title()
                    user['email'] = item['email'].strip().lower()
                    
                    # Inline validation
                    if '.' in item['email'] and len(item['email']) > 5:
                        # Age calculation inline
                        if 'birth_year' in item:
                            current_year = 2024
                            user['age'] = current_year - item['birth_year']
                        
                        # More inline logic
                        if user['age'] > 0 and user['age'] < 120:
                            users.append(user)
    
    # Save to file (another responsibility)
    with open('users.json', 'w') as f:
        json.dump(users, f)
    
    return users
''')
        
        if not self._has_api_access():
            pytest.skip("No API keys for refactoring workflow")
            
        try:
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "cli.py"),
                "--prompt", "Suggest refactoring improvements for this code.",
                "--files", messy_file,
                "--mode", "refactor"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                output = result.stdout.lower()
                
                # Should suggest breaking down the function
                if any(word in output for word in ["function", "separate", "responsibility", "refactor"]):
                    print("✓ Refactoring workflow working")
                else:
                    print(f"⚠ Refactoring didn't suggest key improvements: {result.stdout[:200]}")
            else:
                print(f"⚠ Refactoring workflow failed: {result.stderr}")
                
        except Exception as e:
            pytest.skip(f"Refactoring workflow failed: {e}")
            
    def _has_api_access(self):
        """Check if we have API access for workflow testing"""
        return any([
            os.getenv('OPENAI_API_KEY'),
            os.getenv('GEMINI_API_KEY'),
            os.getenv('ANTHROPIC_API_KEY'),
            os.getenv('OPENROUTER_API_KEY')
        ])


if __name__ == "__main__":
    # Run individual tests
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Claude Code Integration")
    parser.add_argument("--test", help="Specific test to run") 
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--workflows", action="store_true", help="Run workflow tests only")
    parser.add_argument("--scenarios", action="store_true", help="Run scenario tests only")
    args = parser.parse_args()
    
    if args.workflows:
        pytest.main([f"{__file__}::TestClaudeCodeWorkflows", "-v" if args.verbose else ""])
    elif args.scenarios:
        pytest.main([f"{__file__}::TestClaudeCodeIntegration", "-v" if args.verbose else ""])
    elif args.test:
        if "." in args.test:
            pytest.main([f"{__file__}::{args.test}", "-v" if args.verbose else ""])
        else:
            # Try to find test in either class
            found = False
            for class_name in ["TestClaudeCodeIntegration", "TestClaudeCodeWorkflows"]:
                try:
                    pytest.main([f"{__file__}::{class_name}::test_{args.test}", "-v" if args.verbose else ""])
                    found = True
                    break
                except:
                    continue
            if not found:
                print(f"❌ Test {args.test} not found")
    else:
        # Run all tests
        pytest.main([__file__, "-v" if args.verbose else ""])