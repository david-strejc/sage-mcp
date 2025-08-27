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

    async def handle(self, context: dict, provider) -> str:
        """Handle debug mode"""
        messages = self.build_messages(context)
        
        # Enhance for debugging
        messages[-1]["content"] = f"""Debug this issue:
{messages[-1]["content"]}

Provide:
1. Problem analysis
2. Likely root cause
3. Step-by-step solution
4. How to prevent in future"""
        
        response = await provider.complete(
            model=context["model"],
            messages=messages,
            temperature=context.get("temperature", 0.2)
        )
        
        return response