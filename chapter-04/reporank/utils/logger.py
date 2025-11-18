"""Logging configuration and utilities."""

import logging
import sys
import json
from typing import Optional, Dict, Any
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that adds structured context to log messages.
    
    Supports both simple string messages and structured logging with extra fields.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with structured context.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string
        """
        # Base format
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage()
        }
        
        # Add structured context if present
        # Check for extra fields added via logger.info(..., extra={...})
        extra_fields = {}
        for key, value in record.__dict__.items():
            # Skip standard logging attributes
            if key not in [
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'message', 'pathname', 'process', 'processName', 'relativeCreated',
                'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info'
            ]:
                extra_fields[key] = value
        
        if extra_fields:
            log_data['context'] = extra_fields
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Format as simple string for console readability
        # For file logging, we could use JSON format
        if hasattr(record, '_use_json') and record._use_json:
            return json.dumps(log_data)
        else:
            # Human-readable format
            base_msg = f"{log_data['timestamp']} - {log_data['logger']} - {log_data['level']} - {log_data['message']}"
            
            if extra_fields:
                context_str = " | ".join(f"{k}={v}" for k, v in extra_fields.items())
                base_msg += f" | {context_str}"
            
            if 'exception' in log_data:
                base_msg += f"\n{log_data['exception']}"
            
            return base_msg


def setup_logger(
    name: str = "reporank",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_structured_logging: bool = True
) -> logging.Logger:
    """
    Set up structured logging with file and console handlers.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        enable_structured_logging: If True, uses structured formatter with context
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    if enable_structured_logging:
        formatter = StructuredFormatter(
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            logger.warning(f"Failed to set up file logging to {log_file}: {e}")
    
    return logger


def get_logger(name: str = "reporank") -> logging.Logger:
    """
    Get an existing logger instance.
    
    If the logger doesn't exist or has no handlers, sets up a basic logger.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set up basic configuration
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter(datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(handler)
    
    return logger


def log_error_with_context(
    logger: logging.Logger,
    message: str,
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an error with structured context information.
    
    Args:
        logger: Logger instance
        message: Error message
        error: Exception object
        context: Optional dictionary of context information
    """
    extra = context or {}
    extra.update({
        'error_type': type(error).__name__,
        'error_message': str(error),
        'timestamp': datetime.now().isoformat()
    })
    
    logger.error(message, extra=extra, exc_info=True)
