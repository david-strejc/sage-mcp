"""
Base mode handler interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from providers.base import BaseProvider

class BaseMode(ABC):
    """Base class for all mode handlers"""
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get mode-specific system prompt"""
        pass
    
    @abstractmethod
    async def handle(self, context: Dict[str, Any], provider: BaseProvider) -> str:
        """
        Handle the mode execution
        
        Args:
            context: Full context including prompt, files, conversation
            provider: AI provider to use
            
        Returns:
            Response string
        """
        pass
    
    def build_messages(self, context: Dict[str, Any]) -> list[dict]:
        """Build messages for AI provider"""
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": self.get_system_prompt()
        })
        
        # Add conversation history if present
        if context.get("conversation"):
            for turn in context["conversation"]["turns"][-10:]:  # Last 10 turns
                messages.append({
                    "role": turn["role"],
                    "content": turn["content"]
                })
        
        # Build user message
        user_content = context["prompt"]
        
        # Add file contents if present
        if context.get("files"):
            file_section = "\n\n=== FILES ===\n"
            for path, content in context["files"].items():
                file_section += f"\n--- {path} ---\n{content}\n"
            file_section += "\n=== END FILES ===\n"
            user_content = f"{user_content}{file_section}"
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        return messages