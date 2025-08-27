"""
Review mode - Code review for bugs, security, and quality
"""

from modes.base import BaseMode

class ReviewMode(BaseMode):
    """Handle code review with focus on quality and security"""
    
    def get_system_prompt(self) -> str:
        return """You are SAGE in review mode - an expert code reviewer.
        
Review the provided code focusing on:
- Bugs and logic errors
- Security vulnerabilities
- Code quality and style
- Performance issues
- Best practices adherence
- Test coverage gaps

Provide structured review with:
1. Summary of findings
2. Critical issues (bugs, security)
3. Quality improvements
4. Performance optimizations
5. Recommendations with priorities

Be thorough but constructive. Explain the reasoning behind each finding."""

    def _get_mode_enhancement(self) -> str:
        """Add review-specific prompting"""
        return "Provide a thorough code review with specific, actionable feedback."
    
    def _get_default_temperature(self) -> float:
        """Review mode uses low temperature for consistent evaluation"""
        return 0.3