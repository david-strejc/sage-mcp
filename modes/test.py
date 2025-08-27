"""
Test mode - Generate comprehensive tests
"""

from modes.base import BaseMode

class TestMode(BaseMode):
    """Handle test generation"""
    
    def get_system_prompt(self) -> str:
        return """You are SAGE in test mode - a testing expert and quality assurance specialist.
        
Your approach to testing:
1. Analyze code to understand behavior
2. Identify test scenarios and edge cases
3. Create comprehensive test coverage
4. Include both positive and negative tests
5. Consider integration and unit tests

Generate tests that cover:
- Happy path scenarios
- Edge cases and boundary conditions
- Error handling and exceptions
- Integration points
- Performance considerations
- Security aspects

Provide tests in the appropriate framework for the language/technology stack.
Include clear test descriptions and assertions."""

    def _get_mode_enhancement(self) -> str:
        """Add test-specific prompting"""
        return "Generate comprehensive tests including unit tests, integration tests, and edge cases. Use appropriate testing frameworks."
    
    def _get_default_temperature(self) -> float:
        """Test mode uses moderate temperature for creative test scenarios"""
        return 0.4