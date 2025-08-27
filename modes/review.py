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

    async def handle(self, context: dict, provider) -> str:
        """Handle review mode"""
        messages = self.build_messages(context)
        
        # Add review-specific prompting
        messages[-1]["content"] += "\n\nProvide a thorough code review with specific, actionable feedback."
        
        response = await provider.complete(
            model=context["model"],
            messages=messages,
            temperature=context.get("temperature", 0.3)
        )
        
        return response