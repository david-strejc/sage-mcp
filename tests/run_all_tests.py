#!/usr/bin/env python3
"""
Comprehensive Test Runner for SAGE-MCP
Runs all types of tests with proper reporting and organization
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))


class TestRunner:
    """Comprehensive test runner for SAGE-MCP"""
    
    def __init__(self, verbose=False, api_tests=False):
        self.verbose = verbose
        self.api_tests = api_tests
        self.project_root = Path(__file__).parent.parent
        self.test_dir = Path(__file__).parent
        
        self.results = {
            'unit': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []},
            'integration': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []},
            'providers': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []},
            'file_types': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []},
            'e2e': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []},
            'real_world': {'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []}
        }
        
    def print_header(self, title):
        """Print formatted test section header"""
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}")
        
    def print_subheader(self, title):
        """Print formatted test subsection header"""
        print(f"\n{'-'*40}")
        print(f"{title}")
        print(f"{'-'*40}")
        
    def run_pytest(self, test_path, category, description):
        """Run pytest on a specific test path"""
        self.print_subheader(f"Running {description}")
        
        cmd = [
            sys.executable, "-m", "pytest", 
            str(test_path),
            "-v" if self.verbose else "",
            "--tb=short"
        ]
        cmd = [arg for arg in cmd if arg]  # Remove empty strings
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per test suite
                cwd=self.project_root
            )
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'passed' in line and 'failed' in line:
                    # Parse summary line like "5 passed, 2 failed, 1 skipped"
                    parts = line.split(',')
                    for part in parts:
                        part = part.strip()
                        if 'passed' in part:
                            self.results[category]['passed'] += int(part.split()[0])
                        elif 'failed' in part:
                            self.results[category]['failed'] += int(part.split()[0])
                        elif 'skipped' in part:
                            self.results[category]['skipped'] += int(part.split()[0])
                            
            if result.returncode == 0:
                print(f"✓ {description} completed successfully")
            else:
                print(f"⚠ {description} completed with issues")
                if result.stderr:
                    self.results[category]['errors'].append(f"{description}: {result.stderr[:200]}")
                    
            if self.verbose:
                print(f"Output:\n{result.stdout}")
                if result.stderr:
                    print(f"Errors:\n{result.stderr}")
                    
        except subprocess.TimeoutExpired:
            print(f"❌ {description} timed out")
            self.results[category]['errors'].append(f"{description}: Timeout")
        except Exception as e:
            print(f"❌ {description} failed: {e}")
            self.results[category]['errors'].append(f"{description}: {e}")
            
    def run_individual_test(self, test_script, category, description):
        """Run an individual test script"""
        self.print_subheader(f"Running {description}")
        
        cmd = [sys.executable, str(test_script)]
        if self.verbose:
            cmd.append("--verbose")
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print(f"✓ {description} completed successfully")
                self.results[category]['passed'] += 1
            else:
                print(f"⚠ {description} completed with issues")
                self.results[category]['failed'] += 1
                if result.stderr:
                    self.results[category]['errors'].append(f"{description}: {result.stderr[:200]}")
                    
            if self.verbose:
                print(f"Output:\n{result.stdout}")
                if result.stderr:
                    print(f"Errors:\n{result.stderr}")
                    
        except subprocess.TimeoutExpired:
            print(f"❌ {description} timed out")
            self.results[category]['failed'] += 1
            self.results[category]['errors'].append(f"{description}: Timeout")
        except Exception as e:
            print(f"❌ {description} failed: {e}")
            self.results[category]['failed'] += 1
            self.results[category]['errors'].append(f"{description}: {e}")
            
    def check_environment(self):
        """Check environment setup"""
        self.print_header("Environment Check")
        
        # Check API keys
        api_keys = {
            'OpenAI': os.getenv('OPENAI_API_KEY'),
            'Gemini': os.getenv('GEMINI_API_KEY'),
            'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'OpenRouter': os.getenv('OPENROUTER_API_KEY'),
            'Custom': os.getenv('CUSTOM_API_URL')
        }
        
        print("API Key Status:")
        available_providers = []
        for provider, key in api_keys.items():
            status = "✓ Available" if key else "❌ Not set"
            print(f"  {provider:12}: {status}")
            if key:
                available_providers.append(provider)
                
        if not available_providers:
            print("\n⚠ Warning: No API keys configured. API-dependent tests will be skipped.")
        else:
            print(f"\n✓ {len(available_providers)} providers configured: {', '.join(available_providers)}")
            
        # Check required files
        required_files = [
            'config.py',
            'server.py', 
            'cli.py',
            'tools/sage.py',
            'providers/__init__.py',
            'modes/__init__.py',
            'utils/__init__.py'
        ]
        
        print("\nRequired Files:")
        missing_files = []
        for file in required_files:
            path = self.project_root / file
            status = "✓ Found" if path.exists() else "❌ Missing"
            print(f"  {file:20}: {status}")
            if not path.exists():
                missing_files.append(file)
                
        if missing_files:
            print(f"\n❌ Missing required files: {', '.join(missing_files)}")
            return False
        else:
            print("\n✓ All required files present")
            
        # Check Python dependencies
        print("\nPython Dependencies:")
        try:
            import pytest
            print("  pytest               : ✓ Available")
        except ImportError:
            print("  pytest               : ❌ Missing (install with: pip install pytest)")
            return False
            
        try:
            from PIL import Image
            print("  Pillow               : ✓ Available")
        except ImportError:
            print("  Pillow               : ❌ Missing (install with: pip install Pillow)")
            
        return True
        
    def run_unit_tests(self):
        """Run unit tests"""
        self.print_header("Unit Tests")
        
        unit_tests = [
            (self.test_dir / "unit" / "test_conversation_continuation.py", "Conversation Continuation"),
            (self.test_dir / "unit" / "test_model_restrictions.py", "Model Restrictions"),
        ]
        
        for test_file, description in unit_tests:
            if test_file.exists():
                self.run_pytest(test_file, 'unit', description)
            else:
                print(f"⚠ Unit test not found: {test_file}")
                
    def run_provider_tests(self):
        """Run provider tests"""
        self.print_header("Provider Tests")
        
        if not self.api_tests:
            print("⚠ Skipping provider tests (use --api-tests to enable)")
            return
            
        provider_tests = [
            (self.test_dir / "providers" / "test_openai_provider.py", "OpenAI Provider"),
            (self.test_dir / "providers" / "test_gemini_provider.py", "Gemini Provider"),
            (self.test_dir / "providers" / "test_anthropic_provider.py", "Anthropic Provider"),
            (self.test_dir / "providers" / "test_openrouter_provider.py", "OpenRouter Provider"),
            (self.test_dir / "providers" / "test_custom_provider.py", "Custom/Ollama Provider"),
        ]
        
        for test_file, description in provider_tests:
            if test_file.exists():
                self.run_pytest(test_file, 'providers', description)
            else:
                print(f"⚠ Provider test not found: {test_file}")
                
    def run_file_type_tests(self):
        """Run file type tests"""
        self.print_header("File Type Tests")
        
        file_type_tests = [
            (self.test_dir / "file_types" / "test_text_files.py", "Text File Handling"),
            (self.test_dir / "file_types" / "test_binary_files.py", "Binary File Handling"),
            (self.test_dir / "file_types" / "test_image_handling.py", "Image File Handling"),
        ]
        
        for test_file, description in file_type_tests:
            if test_file.exists():
                self.run_pytest(test_file, 'file_types', description)
            else:
                print(f"⚠ File type test not found: {test_file}")
                
    def run_integration_tests(self):
        """Run integration tests"""
        self.print_header("Integration Tests")
        
        integration_tests = [
            (self.test_dir / "integration" / "test_folder_content.py", "Folder Content Processing"),
        ]
        
        for test_file, description in integration_tests:
            if test_file.exists():
                self.run_pytest(test_file, 'integration', description)
            else:
                print(f"⚠ Integration test not found: {test_file}")
                
    def run_e2e_tests(self):
        """Run end-to-end tests"""
        self.print_header("End-to-End Tests")
        
        e2e_tests = [
            (self.test_dir / "e2e" / "test_cli_interface.py", "CLI Interface"),
        ]
        
        for test_file, description in e2e_tests:
            if test_file.exists():
                self.run_pytest(test_file, 'e2e', description)
            else:
                print(f"⚠ E2E test not found: {test_file}")
                
    def run_real_world_tests(self):
        """Run real-world scenario tests"""
        self.print_header("Real-World Scenario Tests")
        
        if not self.api_tests:
            print("⚠ Skipping real-world tests (use --api-tests to enable)")
            return
            
        real_world_tests = [
            (self.test_dir / "real_world" / "test_claude_code_integration.py", "Claude Code Integration"),
        ]
        
        for test_file, description in real_world_tests:
            if test_file.exists():
                self.run_pytest(test_file, 'real_world', description)
            else:
                print(f"⚠ Real-world test not found: {test_file}")
                
    def print_summary(self):
        """Print comprehensive test summary"""
        self.print_header("Test Summary")
        
        total_passed = sum(category['passed'] for category in self.results.values())
        total_failed = sum(category['failed'] for category in self.results.values())
        total_skipped = sum(category['skipped'] for category in self.results.values())
        total_tests = total_passed + total_failed + total_skipped
        
        print(f"Overall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed:      {total_passed} ({total_passed/max(total_tests,1)*100:.1f}%)")
        print(f"  Failed:      {total_failed} ({total_failed/max(total_tests,1)*100:.1f}%)")
        print(f"  Skipped:     {total_skipped} ({total_skipped/max(total_tests,1)*100:.1f}%)")
        
        print(f"\nResults by Category:")
        for category, results in self.results.items():
            total_cat = results['passed'] + results['failed'] + results['skipped']
            if total_cat > 0:
                print(f"  {category.title():12}: {results['passed']:3}P {results['failed']:3}F {results['skipped']:3}S")
                
        # Print errors if any
        all_errors = []
        for category, results in self.results.items():
            all_errors.extend(results['errors'])
            
        if all_errors:
            print(f"\nErrors ({len(all_errors)}):")
            for i, error in enumerate(all_errors[:10], 1):  # Show first 10 errors
                print(f"  {i:2}. {error}")
            if len(all_errors) > 10:
                print(f"     ... and {len(all_errors) - 10} more errors")
                
        # Overall status
        if total_failed == 0:
            print(f"\n✓ All tests passed!")
            return True
        else:
            print(f"\n⚠ {total_failed} tests failed")
            return False
            
    def generate_report(self, output_file=None):
        """Generate detailed test report"""
        if not output_file:
            output_file = self.project_root / "test_report.json"
            
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "environment": {
                "python_version": sys.version,
                "project_root": str(self.project_root),
                "api_tests_enabled": self.api_tests,
                "api_keys_configured": [
                    provider for provider, key in {
                        'OpenAI': os.getenv('OPENAI_API_KEY'),
                        'Gemini': os.getenv('GEMINI_API_KEY'),
                        'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
                        'OpenRouter': os.getenv('OPENROUTER_API_KEY')
                    }.items() if key
                ]
            },
            "results": self.results,
            "summary": {
                "total_passed": sum(cat['passed'] for cat in self.results.values()),
                "total_failed": sum(cat['failed'] for cat in self.results.values()),
                "total_skipped": sum(cat['skipped'] for cat in self.results.values()),
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\nDetailed report saved to: {output_file}")
        
    def run_all(self):
        """Run all test suites"""
        start_time = time.time()
        
        # Check environment first
        if not self.check_environment():
            print("\n❌ Environment check failed. Please fix issues before running tests.")
            return False
            
        # Run all test categories
        self.run_unit_tests()
        self.run_provider_tests()
        self.run_file_type_tests()
        self.run_integration_tests()
        self.run_e2e_tests()
        self.run_real_world_tests()
        
        # Print summary
        success = self.print_summary()
        
        # Generate report
        self.generate_report()
        
        end_time = time.time()
        print(f"\nTotal test time: {end_time - start_time:.1f} seconds")
        
        return success


def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(description="SAGE-MCP Comprehensive Test Runner")
    
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--api-tests", action="store_true", help="Run API-dependent tests")
    
    # Test category selection
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--providers", action="store_true", help="Run provider tests only")
    parser.add_argument("--file-types", action="store_true", help="Run file type tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument("--real-world", action="store_true", help="Run real-world tests only")
    
    # Utility options
    parser.add_argument("--env-check", action="store_true", help="Run environment check only")
    parser.add_argument("--report", help="Generate report to specific file")
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose, api_tests=args.api_tests)
    
    if args.env_check:
        success = runner.check_environment()
        sys.exit(0 if success else 1)
        
    # Run specific test categories if specified
    category_selected = any([
        args.unit, args.providers, args.file_types, 
        args.integration, args.e2e, args.real_world
    ])
    
    if category_selected:
        start_time = time.time()
        
        if not runner.check_environment():
            print("\n❌ Environment check failed.")
            sys.exit(1)
            
        if args.unit:
            runner.run_unit_tests()
        if args.providers:
            runner.run_provider_tests()
        if args.file_types:
            runner.run_file_type_tests()
        if args.integration:
            runner.run_integration_tests()
        if args.e2e:
            runner.run_e2e_tests()
        if args.real_world:
            runner.run_real_world_tests()
            
        success = runner.print_summary()
        if args.report:
            runner.generate_report(args.report)
            
        end_time = time.time()
        print(f"\nTest time: {end_time - start_time:.1f} seconds")
        
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        success = runner.run_all()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()