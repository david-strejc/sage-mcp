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

    def _get_mode_enhancement(self) -> str:
        """Add planning-specific prompting"""
        return "Create a detailed, actionable project plan with phases, tasks, and priorities."
    
    def _get_default_temperature(self) -> float:
        """Planning mode uses moderate temperature for structured creativity"""
        return 0.5