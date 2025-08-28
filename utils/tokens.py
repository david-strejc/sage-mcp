"""
Token counting utilities for managing context windows
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text (rough approximation)

    Args:
        text: Text to count tokens for

    Returns:
        Estimated token count
    """
    if not text:
        return 0

    # Rough approximation: 1 token ~= 4 characters for English text
    # This is a simplified estimate; real tokenizers vary by model
    return len(text) // 4


def estimate_tokens_for_messages(messages: list) -> int:
    """
    Estimate tokens for a list of messages

    Args:
        messages: List of message dictionaries

    Returns:
        Estimated token count
    """
    total_tokens = 0

    for message in messages:
        if isinstance(message, dict) and "content" in message:
            total_tokens += estimate_tokens(message["content"])
            # Add small overhead for role and structure
            total_tokens += 10

    return total_tokens


def estimate_tokens_for_files(files: Dict[str, Any]) -> int:
    """
    Estimate tokens for file contents

    Args:
        files: Dictionary mapping file paths to content

    Returns:
        Estimated token count
    """
    total_tokens = 0

    for path, content in files.items():
        if isinstance(content, str):
            total_tokens += estimate_tokens(content)
            # Add overhead for file markers
            total_tokens += estimate_tokens(f"--- {path} ---")

    return total_tokens


def calculate_remaining_tokens(current_tokens: int, max_tokens: int, response_reserve: float = 0.3) -> int:
    """
    Calculate remaining tokens available for additional content

    Args:
        current_tokens: Current token usage
        max_tokens: Maximum context window size
        response_reserve: Fraction to reserve for response (default 30%)

    Returns:
        Available tokens for additional content
    """
    reserve_tokens = int(max_tokens * response_reserve)
    available = max_tokens - current_tokens - reserve_tokens

    return max(0, available)


def fits_in_context(base_tokens: int, additional_tokens: int, max_tokens: int, response_reserve: float = 0.3) -> bool:
    """
    Check if additional content fits in context window

    Args:
        base_tokens: Current token usage
        additional_tokens: Tokens to add
        max_tokens: Maximum context window size
        response_reserve: Fraction to reserve for response

    Returns:
        True if content fits, False otherwise
    """
    remaining = calculate_remaining_tokens(base_tokens, max_tokens, response_reserve)
    return additional_tokens <= remaining
