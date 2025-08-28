"""
Conversation memory with cross-tool continuation support
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """Single turn in a conversation"""

    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    files: List[str]
    tool_name: Optional[str] = None
    model_name: Optional[str] = None
    mode: Optional[str] = None


@dataclass
class ConversationThread:
    """Complete conversation thread"""

    thread_id: str
    tool_name: str
    mode: str
    created_at: str
    last_updated: str
    turns: List[ConversationTurn]
    initial_request: Dict[str, Any]


class ConversationMemory:
    """In-memory conversation storage (Redis integration would go here)"""

    def __init__(self):
        self._threads: Dict[str, ConversationThread] = {}

    def create_thread(
        self, tool_name: str, mode: str = "chat", initial_request: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new conversation thread"""
        thread_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        thread = ConversationThread(
            thread_id=thread_id,
            tool_name=tool_name,
            mode=mode,
            created_at=now,
            last_updated=now,
            turns=[],
            initial_request=initial_request or {},
        )

        self._threads[thread_id] = thread
        logger.info(f"Created conversation thread {thread_id} for {tool_name}/{mode}")
        return thread_id

    def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation thread data"""
        thread = self._threads.get(thread_id)
        if not thread:
            return None

        return {
            "thread_id": thread.thread_id,
            "tool_name": thread.tool_name,
            "mode": thread.mode,
            "created_at": thread.created_at,
            "last_updated": thread.last_updated,
            "turns": [
                {
                    "role": turn.role,
                    "content": turn.content,
                    "timestamp": turn.timestamp,
                    "files": turn.files,
                    "tool_name": turn.tool_name,
                    "model_name": turn.model_name,
                    "mode": turn.mode,
                }
                for turn in thread.turns
            ],
            "initial_request": thread.initial_request,
        }

    def add_turn(
        self,
        thread_id: str,
        role: str,
        content: str,
        files: Optional[List[str]] = None,
        tool_name: Optional[str] = None,
        model_name: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> bool:
        """Add turn to conversation thread"""
        thread = self._threads.get(thread_id)
        if not thread:
            logger.warning(f"Thread {thread_id} not found")
            return False

        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            files=files or [],
            tool_name=tool_name,
            model_name=model_name,
            mode=mode,
        )

        thread.turns.append(turn)
        thread.last_updated = turn.timestamp

        logger.debug(f"Added {role} turn to thread {thread_id}")
        return True


# Singleton instance
_memory = ConversationMemory()


def create_thread(tool_name: str, mode: str = "chat", initial_request: Optional[Dict[str, Any]] = None) -> str:
    """Create new conversation thread"""
    return _memory.create_thread(tool_name, mode, initial_request)


def get_thread(thread_id: str) -> Optional[Dict[str, Any]]:
    """Get conversation thread data"""
    return _memory.get_thread(thread_id)


def add_turn(
    thread_id: str,
    role: str,
    content: str,
    files: Optional[List[str]] = None,
    tool_name: Optional[str] = None,
    model_name: Optional[str] = None,
    mode: Optional[str] = None,
) -> bool:
    """Add turn to conversation thread"""
    return _memory.add_turn(thread_id, role, content, files, tool_name, model_name, mode)
