"""Input validation utilities for RepoRank."""

import re
import os
from typing import Tuple, Optional, List
from pathlib import Path


def validate_github_url(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse and validate GitHub repository URL.
    
    Supports formats:
    - https://github.com/owner/repo
    - http://github.com/owner/repo
    - github.com/owner/repo
    - owner/repo
    
    Args:
        url: GitHub repository URL or owner/repo string
        
    Returns:
        Tuple of (owner, repo_name, error_message)
        If valid: (owner, repo_name, None)
        If invalid: (None, None, error_message)
    """
    if not url or not isinstance(url, str):
        return None, None, "URL cannot be empty"
    
    url = url.strip()
    
    # Pattern to match GitHub URLs
    patterns = [
        r'^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'^github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'^([^/]+)/([^/]+?)(?:\.git)?/?$'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            owner, repo = match.groups()
            
            # Validate owner and repo names
            if not owner or not repo:
                return None, None, "Invalid GitHub URL format: missing owner or repository name"
            
            # Remove .git suffix if present (handle both .git and trailing slashes)
            if repo.endswith('.git'):
                repo = repo[:-4]
            
            # Validate owner and repo name format (GitHub naming rules)
            if not validate_github_name(owner):
                return None, None, f"Invalid GitHub owner name: {owner}"
            
            if not validate_github_name(repo):
                return None, None, f"Invalid GitHub repository name: {repo}"
            
            return owner, repo, None
    
    return None, None, f"Invalid GitHub URL format: {url}. Expected format: github.com/owner/repo"


def validate_github_name(name: str) -> bool:
    """
    Validate GitHub username or repository name.
    
    GitHub names can contain alphanumeric characters and hyphens,
    but cannot start or end with a hyphen.
    
    Args:
        name: Username or repository name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False
    
    # GitHub names: alphanumeric and hyphens, cannot start/end with hyphen
    # Also allow underscores and dots for repo names
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$'
    
    return bool(re.match(pattern, name)) and len(name) <= 100


def validate_directory_path(path: str, create_if_missing: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate that a directory path is valid and accessible.
    
    Args:
        path: Directory path to validate
        create_if_missing: If True, create the directory if it doesn't exist
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path or not isinstance(path, str):
        return False, "Path cannot be empty"
    
    try:
        path_obj = Path(path)
        
        # Check if path exists
        if path_obj.exists():
            if not path_obj.is_dir():
                return False, f"Path exists but is not a directory: {path}"
            
            # Check if writable
            if not os.access(path, os.W_OK):
                return False, f"Directory is not writable: {path}"
            
            return True, None
        
        # Path doesn't exist
        if create_if_missing:
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                return True, None
            except Exception as e:
                return False, f"Failed to create directory: {e}"
        else:
            return False, f"Directory does not exist: {path}"
    
    except Exception as e:
        return False, f"Invalid path: {e}"


def validate_file_path(path: str, must_exist: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Validate that a file path is valid.
    
    Args:
        path: File path to validate
        must_exist: If True, file must exist
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path or not isinstance(path, str):
        return False, "Path cannot be empty"
    
    try:
        path_obj = Path(path)
        
        if must_exist:
            if not path_obj.exists():
                return False, f"File does not exist: {path}"
            
            if not path_obj.is_file():
                return False, f"Path exists but is not a file: {path}"
            
            # Check if readable
            if not os.access(path, os.R_OK):
                return False, f"File is not readable: {path}"
        else:
            # Check if parent directory exists and is writable
            parent = path_obj.parent
            if not parent.exists():
                return False, f"Parent directory does not exist: {parent}"
            
            if not os.access(parent, os.W_OK):
                return False, f"Parent directory is not writable: {parent}"
        
        return True, None
    
    except Exception as e:
        return False, f"Invalid path: {e}"


def validate_log_level(level: str) -> Tuple[bool, Optional[str]]:
    """
    Validate logging level string.
    
    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    if not level or not isinstance(level, str):
        return False, "Log level cannot be empty"
    
    level_upper = level.upper()
    if level_upper not in valid_levels:
        return False, f"Invalid log level: {level}. Must be one of {valid_levels}"
    
    return True, None


def validate_positive_integer(value: int, name: str = "value", min_value: int = 1) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is a positive integer.
    
    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)
        min_value: Minimum allowed value (default: 1)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, int):
        return False, f"{name} must be an integer, got {type(value).__name__}"
    
    if value < min_value:
        return False, f"{name} must be at least {min_value}, got {value}"
    
    return True, None


def validate_float_range(
    value: float,
    name: str = "value",
    min_value: float = 0.0,
    max_value: float = 1.0
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a float value is within a specified range.
    
    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, (int, float)):
        return False, f"{name} must be a number, got {type(value).__name__}"
    
    if not min_value <= value <= max_value:
        return False, f"{name} must be between {min_value} and {max_value}, got {value}"
    
    return True, None


def validate_api_key(api_key: str, provider: str = "API") -> Tuple[bool, Optional[str]]:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        provider: Provider name (for error messages)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key or not isinstance(api_key, str):
        return False, f"{provider} API key cannot be empty"
    
    api_key = api_key.strip()
    
    # Basic validation: must be at least 10 characters
    if len(api_key) < 10:
        return False, f"{provider} API key appears to be invalid (too short)"
    
    # Check for common placeholder values
    placeholder_values = ["your-api-key", "xxx", "test", "placeholder", "changeme"]
    if api_key.lower() in placeholder_values:
        return False, f"{provider} API key appears to be a placeholder value"
    
    return True, None


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Filename to sanitize
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove invalid characters for most filesystems
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Truncate to max length
    if len(sanitized) > max_length:
        # Keep file extension if present
        name, ext = os.path.splitext(sanitized)
        max_name_length = max_length - len(ext)
        sanitized = name[:max_name_length] + ext
    
    # Ensure we have a valid filename
    if not sanitized:
        sanitized = "unnamed"
    
    return sanitized


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a general URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL cannot be empty"
    
    url = url.strip()
    
    # Basic URL pattern
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    
    if not re.match(url_pattern, url, re.IGNORECASE):
        return False, f"Invalid URL format: {url}"
    
    return True, None


def validate_extension_list(extensions: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate a list of file extensions.
    
    Args:
        extensions: List of file extensions (e.g., ['.py', '.js'])
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(extensions, (list, set, tuple)):
        return False, "Extensions must be a list, set, or tuple"
    
    for ext in extensions:
        if not isinstance(ext, str):
            return False, f"Extension must be a string, got {type(ext).__name__}"
        
        if not ext.startswith('.'):
            return False, f"Extension must start with a dot: {ext}"
        
        if len(ext) < 2:
            return False, f"Extension too short: {ext}"
    
    return True, None
