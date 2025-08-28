"""
Debug mode - Troubleshooting and root cause analysis
"""

from modes.base import BaseMode


class DebugMode(BaseMode):
    """Handle debugging and troubleshooting"""

    def get_system_prompt(self) -> str:
        return """You are SAGE in debug mode - an expert debugger and troubleshooter.
        
Your approach:
1. Understand the problem clearly
2. Analyze symptoms and error messages
3. Identify potential root causes
4. Suggest diagnostic steps
5. Provide specific solutions

Focus on:
- Root cause analysis
- Step-by-step debugging approach
- Clear explanation of issues
- Actionable fixes
- Prevention strategies"""

    def _get_mode_enhancement(self) -> str:
        """Add debug-specific prompting structure"""
        return """Provide:
1. Problem analysis
2. Likely root cause
3. Step-by-step solution
4. How to prevent in future"""

    def _get_default_temperature(self) -> float:
        """Debug mode uses very low temperature for precise analysis"""
        return 0.2
