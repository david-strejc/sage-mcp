"""
Security utilities for path validation and access control
"""

import os
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


def is_safe_path(path: Path) -> bool:
    """
    Check if path is safe (no path traversal, within allowed areas)

    Args:
        path: Path to check

    Returns:
        True if safe, False otherwise
    """
    try:
        # Resolve to absolute path
        abs_path = path.resolve()

        # Check for path traversal attempts
        if ".." in str(path) or str(abs_path) != str(path.resolve()):
            return False

        # Check if path exists and is a file
        if not abs_path.exists():
            return False

        if not abs_path.is_file():
            return False

        # Additional security checks can be added here
        # For now, allow all files that pass basic checks
        return True

    except Exception as e:
        logger.warning(f"Security check failed for path {path}: {e}")
        return False


def validate_paths(paths: List[str]) -> Tuple[bool, str]:
    """
    Validate a list of file paths for security

    Args:
        paths: List of file paths to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        for path_str in paths:
            path = Path(path_str)

            # Check if path is safe
            if not is_safe_path(path):
                return False, f"Unsafe path: {path_str}"

        return True, ""

    except Exception as e:
        return False, f"Path validation error: {str(e)}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path components
    name = os.path.basename(filename)

    # Remove dangerous characters
    dangerous_chars = ["..", "/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    for char in dangerous_chars:
        name = name.replace(char, "_")

    return name


def check_file_permissions(path: Path) -> bool:
    """
    Check if file has appropriate read permissions

    Args:
        path: File path to check

    Returns:
        True if readable, False otherwise
    """
    try:
        return os.access(path, os.R_OK)
    except Exception:
        return False
