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

    async def handle(self, context: dict, provider) -> str:
        """Handle analyze mode"""
        messages = self.build_messages(context)
        
        # Add analysis-specific prompting
        messages[-1]["content"] += "\n\nProvide a comprehensive analysis with actionable insights."
        
        response = await provider.complete(
            model=context["model"],
            messages=messages,
            temperature=context.get("temperature", 0.3)
        )
        
        return response