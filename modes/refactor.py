"""
Refactor mode - Suggest code improvements
"""

from modes.base import BaseMode

class RefactorMode(BaseMode):
    """Handle code refactoring suggestions"""
    
    def get_system_prompt(self) -> str:
        return """You are SAGE in refactor mode - a code improvement specialist.
        
Your refactoring focus:
1. Improve code readability and maintainability
2. Enhance performance where possible
3. Apply design patterns appropriately
4. Reduce code duplication
5. Improve error handling and robustness

Refactoring principles:
- Make small, incremental improvements
- Preserve existing functionality
- Improve code structure and organization
- Enhance testability
- Follow language-specific best practices
- Consider SOLID principles

Provide:
- Specific refactoring suggestions
- Before/after code examples
- Explanation of improvements
- Migration strategy if needed"""

    async def handle(self, context: dict, provider) -> str:
        """Handle refactor mode"""
        messages = self.build_messages(context)
        
        # Add refactoring-specific prompting
        messages[-1]["content"] += "\n\nSuggest specific refactoring improvements with code examples. Focus on maintainability, performance, and best practices."
        
        response = await provider.complete(
            model=context["model"],
            messages=messages,
            temperature=context.get("temperature", 0.4)
        )
        
        return response