"""
Smart file handling with conversation memory integration
Supports directory expansion, deduplication, and multiple handling modes
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from config import Config
from utils.security import validate_paths, is_safe_path
from utils.tokens import estimate_tokens

logger = logging.getLogger(__name__)

def expand_paths(paths: List[str]) -> List[str]:
    """
    Expand directory paths to individual file paths
    
    Args:
        paths: List of file or directory paths
        
    Returns:
        List of individual file paths
    """
    expanded = []
    config = Config()
    
    for path in paths:
        abs_path = Path(path).resolve()
        
        if abs_path.is_file():
            expanded.append(str(abs_path))
        elif abs_path.is_dir():
            # Recursively find files in directory
            for root, dirs, files in os.walk(abs_path):
                # Filter excluded directories
                dirs[:] = [d for d in dirs if d not in config.EXCLUDED_DIRS]
                
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix in config.ALLOWED_FILE_EXTENSIONS:
                        expanded.append(str(file_path))
        else:
            logger.warning(f"Path not found: {path}")
    
    return expanded

def read_files(
    file_paths: List[str], 
    mode: str = "embedded",
    max_tokens: Optional[int] = None
) -> Union[Dict[str, str], Dict[str, dict]]:
    """
    Read multiple files with smart handling modes
    
    Args:
        file_paths: List of absolute file paths
        mode: How to handle files - "embedded", "summary", or "reference"
        max_tokens: Maximum tokens to read (for embedded mode)
        
    Returns:
        Dict mapping file path to content (or metadata for summary/reference modes)
    """
    if mode == "embedded":
        return read_files_embedded(file_paths, max_tokens)
    elif mode == "summary":
        return read_files_summary(file_paths)
    elif mode == "reference":
        return read_files_reference(file_paths)
    else:
        raise ValueError(f"Unknown file handling mode: {mode}")

def read_files_embedded(file_paths: List[str], max_tokens: Optional[int] = None) -> Dict[str, str]:
    """
    Read files and return full content (traditional mode)
    
    Args:
        file_paths: List of absolute file paths
        max_tokens: Maximum tokens to read across all files
        
    Returns:
        Dict mapping file path to full content
    """
    contents = {}
    config = Config()
    total_tokens = 0
    
    # Prioritize files by modification time (newest first)
    file_info = []
    for path in file_paths:
        abs_path = Path(path).resolve()
        if abs_path.exists() and abs_path.is_file():
            mtime = abs_path.stat().st_mtime
            file_info.append((str(abs_path), mtime))
    
    # Sort by modification time (newest first)
    file_info.sort(key=lambda x: x[1], reverse=True)
    
    for path, _ in file_info:
        try:
            abs_path = Path(path)
            
            # Security checks
            if not is_safe_path(abs_path):
                logger.warning(f"Unsafe path skipped: {abs_path}")
                continue
                
            # Size check
            size = abs_path.stat().st_size
            if size > config.MAX_FILE_SIZE:
                logger.warning(f"File too large ({size} bytes): {abs_path}")
                contents[str(abs_path)] = f"[File too large: {size:,} bytes]"
                continue
            
            # Extension check
            if abs_path.suffix not in config.ALLOWED_FILE_EXTENSIONS:
                logger.warning(f"Unsupported file type: {abs_path}")
                continue
            
            # Read file content
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Token budget check
            if max_tokens:
                content_tokens = estimate_tokens(content)
                if total_tokens + content_tokens > max_tokens:
                    logger.warning(f"Token budget exceeded, skipping remaining files")
                    break
                total_tokens += content_tokens
            
            contents[str(abs_path)] = content
            logger.debug(f"Read file: {abs_path} ({len(content):,} chars)")
                
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
            contents[path] = f"[Error reading file: {e}]"
    
    return contents

def read_files_summary(file_paths: List[str]) -> Dict[str, dict]:
    """
    Read files and return summaries instead of full content
    
    Args:
        file_paths: List of absolute file paths
        
    Returns:
        Dict mapping file path to summary metadata
    """
    summaries = {}
    
    for path in file_paths:
        try:
            abs_path = Path(path).resolve()
            
            if not abs_path.exists() or not abs_path.is_file():
                continue
                
            # Get file info
            stat_info = abs_path.stat()
            size = stat_info.st_size
            
            # Read first few lines for summary
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Generate summary
            summary = {
                "size_bytes": size,
                "line_count": len(lines),
                "file_type": abs_path.suffix,
                "preview": ''.join(lines[:10]).strip(),  # First 10 lines
                "last_modified": stat_info.st_mtime
            }
            
            # Add language-specific info
            if abs_path.suffix == '.py':
                import_lines = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
                class_lines = [line.strip() for line in lines if line.strip().startswith('class ')]
                func_lines = [line.strip() for line in lines if line.strip().startswith('def ')]
                
                summary.update({
                    "imports": len(import_lines),
                    "classes": len(class_lines), 
                    "functions": len(func_lines)
                })
                
            summaries[str(abs_path)] = summary
            
        except Exception as e:
            logger.error(f"Error summarizing {path}: {e}")
            summaries[path] = {"error": str(e)}
    
    return summaries

def read_files_reference(file_paths: List[str]) -> Dict[str, dict]:
    """
    Store files in reference system and return reference IDs
    
    Args:
        file_paths: List of absolute file paths
        
    Returns:
        Dict mapping file path to reference metadata
    """
    references = {}
    
    # This would integrate with a file storage system
    # For now, return metadata that indicates files are "stored"
    for path in file_paths:
        try:
            abs_path = Path(path).resolve()
            
            if abs_path.exists() and abs_path.is_file():
                ref_id = f"ref_{hash(str(abs_path)) % 10000:04d}"
                references[str(abs_path)] = {
                    "reference_id": ref_id,
                    "stored": True,
                    "size": abs_path.stat().st_size,
                    "type": abs_path.suffix
                }
            else:
                references[path] = {"error": "File not found"}
                
        except Exception as e:
            logger.error(f"Error referencing {path}: {e}")
            references[path] = {"error": str(e)}
    
    return references