"""Utility modules for RepoRank."""

from utils.logger import (
    setup_logger,
    get_logger,
    log_error_with_context,
    StructuredFormatter
)

from utils.validators import (
    validate_github_url,
    validate_github_name,
    validate_directory_path,
    validate_file_path,
    validate_log_level,
    validate_positive_integer,
    validate_float_range,
    validate_api_key,
    validate_url,
    validate_extension_list,
    sanitize_filename
)

from utils.file_utils import (
    ensure_directory,
    create_temp_directory,
    cleanup_directory,
    read_json_file,
    write_json_file,
    read_text_file,
    write_text_file,
    get_file_size,
    get_directory_size,
    format_file_size,
    list_files_recursive,
    count_lines_in_file,
    generate_timestamp_filename,
    safe_filename,
    copy_file,
    move_file,
    file_exists,
    directory_exists
)

from utils.data_utils import (
    normalize_score,
    calculate_percentage,
    safe_divide,
    truncate_string,
    format_number,
    format_date,
    parse_iso_date,
    merge_dicts,
    flatten_dict,
    group_by,
    filter_dict,
    remove_none_values,
    convert_to_serializable,
    to_json_safe,
    extract_nested_value,
    calculate_statistics,
    chunk_list,
    deduplicate_list,
    sort_dict_by_value,
    create_lookup_dict
)

__all__ = [
    # Logger
    'setup_logger',
    'get_logger',
    'log_error_with_context',
    'StructuredFormatter',
    
    # Validators
    'validate_github_url',
    'validate_github_name',
    'validate_directory_path',
    'validate_file_path',
    'validate_log_level',
    'validate_positive_integer',
    'validate_float_range',
    'validate_api_key',
    'validate_url',
    'validate_extension_list',
    'sanitize_filename',
    
    # File utilities
    'ensure_directory',
    'create_temp_directory',
    'cleanup_directory',
    'read_json_file',
    'write_json_file',
    'read_text_file',
    'write_text_file',
    'get_file_size',
    'get_directory_size',
    'format_file_size',
    'list_files_recursive',
    'count_lines_in_file',
    'generate_timestamp_filename',
    'safe_filename',
    'copy_file',
    'move_file',
    'file_exists',
    'directory_exists',
    
    # Data utilities
    'normalize_score',
    'calculate_percentage',
    'safe_divide',
    'truncate_string',
    'format_number',
    'format_date',
    'parse_iso_date',
    'merge_dicts',
    'flatten_dict',
    'group_by',
    'filter_dict',
    'remove_none_values',
    'convert_to_serializable',
    'to_json_safe',
    'extract_nested_value',
    'calculate_statistics',
    'chunk_list',
    'deduplicate_list',
    'sort_dict_by_value',
    'create_lookup_dict',
]
