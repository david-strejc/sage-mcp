"""
Analyze mode - Code and architecture analysis
"""

from modes.base import BaseMode

class AnalyzeMode(BaseMode):
    """Handle code and architecture analysis"""
    
    def get_system_prompt(self) -> str:
        return """You are SAGE in analysis mode - a senior software architect.
        
Analyze the provided code/architecture focusing on:
- Design patterns and architectural decisions
- Code quality and maintainability
- Performance characteristics
- Security considerations
- Potential improvements

Provide structured analysis with:
1. Overview
2. Strengths
3. Areas for improvement
4. Specific recommendations
5. Priority actions"""

    def _get_mode_enhancement(self) -> str:
        """Add analysis-specific prompting"""
        return "Provide a comprehensive analysis with actionable insights."
    
    def _get_default_temperature(self) -> float:
        """Analysis mode uses lower temperature for more focused responses"""
        return 0.3