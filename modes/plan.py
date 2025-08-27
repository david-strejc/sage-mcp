"""
Plan mode - Project planning and task breakdown
"""

from modes.base import BaseMode

class PlanMode(BaseMode):
    """Handle project planning and task breakdown"""
    
    def get_system_prompt(self) -> str:
        return """You are SAGE in planning mode - a project management expert.
        
Your approach to planning:
1. Understand project scope and requirements
2. Break down into manageable phases
3. Identify dependencies and risks
4. Estimate effort and timeline
5. Provide actionable task lists

Create plans with:
- Clear project structure
- Detailed task breakdown
- Priority levels
- Time estimates
- Dependencies
- Risk mitigation
- Success criteria

Be practical and realistic in your planning."""

    async def handle(self, context: dict, provider) -> str:
        """Handle plan mode"""
        messages = self.build_messages(context)
        
        # Add planning-specific prompting
        messages[-1]["content"] += "\n\nCreate a detailed, actionable project plan with phases, tasks, and priorities."
        
        response = await provider.complete(
            model=context["model"],
            messages=messages,
            temperature=context.get("temperature", 0.5)
        )
        
        return response