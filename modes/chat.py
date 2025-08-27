"""
Chat mode - General development discussion
"""

from modes.base import BaseMode

class ChatMode(BaseMode):
    """Handle general chat and discussion"""
    
    def get_system_prompt(self) -> str:
        return """You are SAGE, a wise and helpful development assistant.
        
Your role is to:
- Answer questions clearly and concisely
- Provide practical, actionable advice
- Share relevant examples and best practices
- Help solve problems step by step
- Be friendly but professional

Focus on being helpful while keeping responses focused and relevant."""

    def _get_default_temperature(self) -> float:
        """Chat mode uses default conversational temperature"""
        return 0.7