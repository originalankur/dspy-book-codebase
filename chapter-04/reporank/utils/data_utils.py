"""Data transformation utilities for RepoRank."""

import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal


def normalize_score(score: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
    """
    Normalize a score to be within a specified range.
    
    Args:
        score: Score to normalize
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Normalized score clamped to [min_val, max_val]
    """
    return max(min_val, min(max_val, float(score)))


def calculate_percentage(value: float, total: float, decimals: int = 1) -> float:
    """
    Calculate percentage with safe division.
    
    Args:
        value: Numerator value
        total: Denominator value
        decimals: Number of decimal places
        
    Returns:
        Percentage value (0.0 if total is 0)
    """
    if total == 0:
        return 0.0
    
    percentage = (value / total) * 100
    return round(percentage, decimals)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Perform safe division with default value for zero denominator.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value to return if denominator is 0
        
    Returns:
        Division result or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_number(number: Union[int, float], decimals: int = 0) -> str:
    """
    Format a number with thousands separators.
    
    Args:
        number: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted number string (e.g., "1,234.56")
    """
    if decimals == 0:
        return f"{int(number):,}"
    else:
        return f"{number:,.{decimals}f}"


def format_date(dt: Union[datetime, date, str], format_str: str = "%Y-%m-%d") -> str:
    """
    Format a date or datetime object.
    
    Args:
        dt: Date, datetime, or ISO format string
        format_str: Output format string
        
    Returns:
        Formatted date string
    """
    if isinstance(dt, str):
        # Try to parse ISO format
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return dt
    
    if isinstance(dt, (datetime, date)):
        return dt.strftime(format_str)
    
    return str(dt)


def parse_iso_date(date_str: str) -> Optional[datetime]:
    """
    Parse an ISO format date string.
    
    Args:
        date_str: ISO format date string
        
    Returns:
        Datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    try:
        # Handle various ISO formats
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], deep: bool = False) -> Dict[str, Any]:
    """
    Merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        deep: If True, perform deep merge for nested dicts
        
    Returns:
        Merged dictionary
    """
    if not deep:
        return {**dict1, **dict2}
    
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, deep=True)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def group_by(items: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group a list of dictionaries by a key.
    
    Args:
        items: List of dictionaries
        key: Key to group by
        
    Returns:
        Dictionary mapping key values to lists of items
    """
    groups = {}
    for item in items:
        group_key = item.get(key)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    return groups


def filter_dict(d: Dict[str, Any], keys: List[str], exclude: bool = False) -> Dict[str, Any]:
    """
    Filter dictionary by keys.
    
    Args:
        d: Dictionary to filter
        keys: List of keys to include or exclude
        exclude: If True, exclude the specified keys; if False, include only them
        
    Returns:
        Filtered dictionary
    """
    if exclude:
        return {k: v for k, v in d.items() if k not in keys}
    else:
        return {k: v for k, v in d.items() if k in keys}


def remove_none_values(d: Dict[str, Any], recursive: bool = False) -> Dict[str, Any]:
    """
    Remove None values from a dictionary.
    
    Args:
        d: Dictionary to clean
        recursive: If True, recursively clean nested dictionaries
        
    Returns:
        Dictionary without None values
    """
    result = {}
    for k, v in d.items():
        if v is None:
            continue
        
        if recursive and isinstance(v, dict):
            v = remove_none_values(v, recursive=True)
        
        result[k] = v
    
    return result


def convert_to_serializable(obj: Any) -> Any:
    """
    Convert an object to a JSON-serializable format.
    
    Handles datetime, date, Decimal, and other common types.
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)


def to_json_safe(data: Any) -> Any:
    """
    Recursively convert data to JSON-safe format.
    
    Args:
        data: Data to convert
        
    Returns:
        JSON-safe version of the data
    """
    if isinstance(data, dict):
        return {k: to_json_safe(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [to_json_safe(item) for item in data]
    elif isinstance(data, (datetime, date, Decimal, set, bytes)) or hasattr(data, '__dict__'):
        return convert_to_serializable(data)
    else:
        return data


def extract_nested_value(data: Dict[str, Any], path: str, default: Any = None, sep: str = '.') -> Any:
    """
    Extract a value from a nested dictionary using a path.
    
    Args:
        data: Dictionary to extract from
        path: Dot-separated path (e.g., "user.profile.name")
        default: Default value if path not found
        sep: Path separator
        
    Returns:
        Extracted value or default
    """
    keys = path.split(sep)
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def calculate_statistics(values: List[Union[int, float]]) -> Dict[str, float]:
    """
    Calculate basic statistics for a list of numbers.
    
    Args:
        values: List of numeric values
        
    Returns:
        Dictionary with min, max, mean, median, and sum
    """
    if not values:
        return {
            'min': 0.0,
            'max': 0.0,
            'mean': 0.0,
            'median': 0.0,
            'sum': 0.0,
            'count': 0
        }
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    return {
        'min': float(sorted_values[0]),
        'max': float(sorted_values[-1]),
        'mean': sum(values) / n,
        'median': float(sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2),
        'sum': float(sum(values)),
        'count': n
    }


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def deduplicate_list(items: List[Any], key: Optional[str] = None) -> List[Any]:
    """
    Remove duplicates from a list while preserving order.
    
    Args:
        items: List to deduplicate
        key: Optional key for dictionaries
        
    Returns:
        Deduplicated list
    """
    if not items:
        return []
    
    if key is None:
        # For simple types
        seen = set()
        result = []
        for item in items:
            # Use tuple for unhashable types
            hashable_item = tuple(item) if isinstance(item, list) else item
            if hashable_item not in seen:
                seen.add(hashable_item)
                result.append(item)
        return result
    else:
        # For dictionaries with a key
        seen = set()
        result = []
        for item in items:
            if isinstance(item, dict):
                key_value = item.get(key)
                if key_value not in seen:
                    seen.add(key_value)
                    result.append(item)
        return result


def sort_dict_by_value(d: Dict[str, Any], reverse: bool = False) -> Dict[str, Any]:
    """
    Sort a dictionary by its values.
    
    Args:
        d: Dictionary to sort
        reverse: If True, sort in descending order
        
    Returns:
        Sorted dictionary
    """
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=reverse))


def create_lookup_dict(items: List[Dict[str, Any]], key: str) -> Dict[str, Dict[str, Any]]:
    """
    Create a lookup dictionary from a list of dictionaries.
    
    Args:
        items: List of dictionaries
        key: Key to use for lookup
        
    Returns:
        Dictionary mapping key values to items
    """
    return {item[key]: item for item in items if key in item}
