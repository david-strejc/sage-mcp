"""
Mode registry and initialization
"""

import logging
from typing import Optional, Dict

from modes.base import BaseMode
from modes.chat import ChatMode
from modes.analyze import AnalyzeMode
from modes.review import ReviewMode
from modes.debug import DebugMode
from modes.plan import PlanMode
from modes.test import TestMode
from modes.refactor import RefactorMode
from modes.think import ThinkMode

logger = logging.getLogger(__name__)

# Mode registry
MODES: Dict[str, BaseMode] = {
    "chat": ChatMode(),
    "analyze": AnalyzeMode(),
    "review": ReviewMode(),
    "debug": DebugMode(),
    "plan": PlanMode(),
    "test": TestMode(),
    "refactor": RefactorMode(),
    "think": ThinkMode()
}

def get_mode_handler(mode: str) -> Optional[BaseMode]:
    """Get mode handler by name"""
    return MODES.get(mode)

def list_available_modes() -> list[str]:
    """List all available mode names"""
    return list(MODES.keys())

def get_available_modes() -> list:
    """Get all available modes with descriptions"""
    from config import Config
    config = Config()
    return [{"name": mode, "description": config.MODE_DESCRIPTIONS.get(mode, "No description")} 
            for mode in MODES.keys()]

def get_mode_description(mode: str) -> Optional[str]:
    """Get description for a mode"""
    from config import Config
    config = Config()
    return config.MODE_DESCRIPTIONS.get(mode)

def get_all_mode_descriptions() -> Dict[str, str]:
    """Get all mode descriptions"""
    from config import Config
    config = Config()
    return config.MODE_DESCRIPTIONS

# Validate that all modes are properly registered
def validate_modes():
    """Validate that all modes are properly implemented"""
    for mode_name, mode_instance in MODES.items():
        try:
            # Test that system prompt can be generated
            prompt = mode_instance.get_system_prompt()
            if not prompt or not isinstance(prompt, str):
                logger.error(f"Mode {mode_name} has invalid system prompt")
            else:
                logger.debug(f"Mode {mode_name} validated successfully")
        except Exception as e:
            logger.error(f"Mode {mode_name} validation failed: {e}")

# Validate on import
validate_modes()

__all__ = [
    "get_mode_handler",
    "list_available_modes",
    "get_available_modes", 
    "get_mode_description",
    "get_all_mode_descriptions",
    "MODES"
]