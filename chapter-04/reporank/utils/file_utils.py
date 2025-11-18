"""File operation utilities for RepoRank."""

import os
import shutil
import json
import tempfile
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime


def ensure_directory(path: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Absolute path to the directory
        
    Raises:
        OSError: If directory cannot be created
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return str(path_obj.absolute())


def create_temp_directory(prefix: str = "reporank_") -> str:
    """
    Create a temporary directory.
    
    Args:
        prefix: Prefix for the temporary directory name
        
    Returns:
        Path to the created temporary directory
    """
    return tempfile.mkdtemp(prefix=prefix)


def cleanup_directory(path: str, ignore_errors: bool = True) -> bool:
    """
    Remove a directory and all its contents.
    
    Args:
        path: Directory path to remove
        ignore_errors: If True, ignore errors during removal
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=ignore_errors)
        return True
    except Exception as e:
        if not ignore_errors:
            raise
        return False


def read_json_file(path: str) -> Dict[str, Any]:
    """
    Read and parse a JSON file.
    
    Args:
        path: Path to JSON file
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_file(path: str, data: Dict[str, Any], indent: int = 2) -> None:
    """
    Write data to a JSON file.
    
    Args:
        path: Path to JSON file
        data: Data to write
        indent: Indentation level for pretty printing
        
    Raises:
        OSError: If file cannot be written
    """
    # Ensure parent directory exists
    parent = Path(path).parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def read_text_file(path: str, encoding: str = 'utf-8', errors: str = 'ignore') -> str:
    """
    Read a text file with error handling.
    
    Args:
        path: Path to text file
        encoding: File encoding (default: utf-8)
        errors: How to handle encoding errors (default: ignore)
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    with open(path, 'r', encoding=encoding, errors=errors) as f:
        return f.read()


def write_text_file(path: str, content: str, encoding: str = 'utf-8') -> None:
    """
    Write text content to a file.
    
    Args:
        path: Path to text file
        content: Content to write
        encoding: File encoding (default: utf-8)
        
    Raises:
        OSError: If file cannot be written
    """
    # Ensure parent directory exists
    parent = Path(path).parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)


def get_file_size(path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        path: Path to file
        
    Returns:
        File size in bytes
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    return os.path.getsize(path)


def get_directory_size(path: str) -> int:
    """
    Get total size of a directory and all its contents in bytes.
    
    Args:
        path: Path to directory
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                # Skip files that can't be accessed
                continue
    return total_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def list_files_recursive(
    directory: str,
    extensions: Optional[List[str]] = None,
    exclude_dirs: Optional[List[str]] = None
) -> List[str]:
    """
    List all files in a directory recursively.
    
    Args:
        directory: Directory to search
        extensions: Optional list of file extensions to include (e.g., ['.py', '.js'])
        exclude_dirs: Optional list of directory names to exclude
        
    Returns:
        List of file paths relative to the directory
    """
    if exclude_dirs is None:
        exclude_dirs = []
    
    files = []
    for root, dirs, filenames in os.walk(directory):
        # Remove excluded directories from search
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in filenames:
            # Filter by extension if specified
            if extensions:
                if not any(filename.endswith(ext) for ext in extensions):
                    continue
            
            # Get relative path
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, directory)
            files.append(rel_path)
    
    return files


def count_lines_in_file(path: str, encoding: str = 'utf-8', errors: str = 'ignore') -> int:
    """
    Count the number of lines in a file.
    
    Args:
        path: Path to file
        encoding: File encoding (default: utf-8)
        errors: How to handle encoding errors (default: ignore)
        
    Returns:
        Number of lines in the file
    """
    try:
        with open(path, 'r', encoding=encoding, errors=errors) as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def generate_timestamp_filename(base_name: str, extension: str = "") -> str:
    """
    Generate a filename with timestamp.
    
    Args:
        base_name: Base name for the file
        extension: File extension (with or without leading dot)
        
    Returns:
        Filename with timestamp (e.g., "report_20231115_143022.html")
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Ensure extension has leading dot
    if extension and not extension.startswith('.'):
        extension = f".{extension}"
    
    return f"{base_name}_{timestamp}{extension}"


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Create a safe filename by removing invalid characters.
    
    This is a wrapper around validators.sanitize_filename for convenience.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Safe filename
    """
    from utils.validators import sanitize_filename
    return sanitize_filename(filename, max_length)


def copy_file(src: str, dst: str, overwrite: bool = False) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        overwrite: If True, overwrite existing file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not overwrite and os.path.exists(dst):
            return False
        
        # Ensure destination directory exists
        dst_dir = os.path.dirname(dst)
        if dst_dir:
            os.makedirs(dst_dir, exist_ok=True)
        
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def move_file(src: str, dst: str, overwrite: bool = False) -> bool:
    """
    Move a file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        overwrite: If True, overwrite existing file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not overwrite and os.path.exists(dst):
            return False
        
        # Ensure destination directory exists
        dst_dir = os.path.dirname(dst)
        if dst_dir:
            os.makedirs(dst_dir, exist_ok=True)
        
        shutil.move(src, dst)
        return True
    except Exception:
        return False


def file_exists(path: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        path: File path
        
    Returns:
        True if file exists, False otherwise
    """
    return os.path.isfile(path)


def directory_exists(path: str) -> bool:
    """
    Check if a directory exists.
    
    Args:
        path: Directory path
        
    Returns:
        True if directory exists, False otherwise
    """
    return os.path.isdir(path)
