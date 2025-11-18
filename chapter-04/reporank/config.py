"""Configuration management for RepoRank."""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class Config:
    """
    Configuration settings for RepoRank.
    
    This is the central configuration class that controls all aspects of the system.
    The LLM model is configured here and impacts all functions that use it.
    
    GitHub token is optional for public repository analysis.
    Public API allows 60 requests/hour without authentication.
    With authentication: 5,000 requests/hour.
    """
    
    # GitHub API (token is optional for public repos)
    github_token: Optional[str] = None
    github_api_base_url: str = "https://api.github.com"
    api_timeout: int = 30
    max_retries: int = 3
    require_authentication: bool = False  # Set to True only for private repos
    
    # LLM Configuration - CENTRAL MODEL CONFIGURATION
    # Change this to use a different model across the entire system
    # Supported formats:
    #   - "gemini/gemini-2.0-flash" (Gemini models)
    #   - "openai/gpt-4" (OpenAI models)
    #   - "openai/gpt-4o-mini" (OpenAI mini models)
    #   - "anthropic/claude-3-opus" (Anthropic models)
    llm_model: str = "gemini/gemini-2.0-flash"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4000
    llm_api_key: Optional[str] = None  # API key for LLM provider
    
    # File Paths
    temp_dir: str = "/tmp/reporank"
    output_dir: str = "./output"
    template_dir: str = "./reporank/report_generation/templates"
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "reporank.log"
    enable_structured_logging: bool = True
    
    # Analysis
    enable_local_clone: bool = True
    clone_timeout: int = 300
    max_repo_size_mb: int = 500
    max_files_for_analysis: int = 5
    
    # Code Analysis
    skip_directories: list = field(default_factory=lambda: [
        '.git', 'node_modules', 'venv', '__pycache__', 
        'dist', 'build', 'target', '.next', 'out'
    ])
    # Added Top N most used languages etc.
    # Good enought for demo purpose
    code_extensions: set = field(default_factory=lambda: {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.java', 
        '.go', '.rs', '.cpp', '.c', '.rb', '.php', 
        '.swift', '.kt', '.cs', '.scala', '.r'
    })
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables.
        
        Environment variables:
        - GITHUB_TOKEN: Optional GitHub API token for higher rate limits
        - GEMINI_API_KEY: API key for Gemini models (if using Gemini)
        - OPENAI_API_KEY: API key for OpenAI models (if using OpenAI)
        - ANTHROPIC_API_KEY: API key for Anthropic models (if using Claude)
        - REPORANK_LLM_MODEL: LLM model to use (e.g., "gemini/gemini-2.0-flash")
        - REPORANK_OUTPUT_DIR: Output directory for reports
        - REPORANK_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
        - REPORANK_LOG_FILE: Log file path (optional, omit for no file logging)
        - REPORANK_TEMP_DIR: Temporary directory for cloning repositories
        - REPORANK_ENABLE_LOCAL_CLONE: Enable/disable local repository cloning (true/false)
        - REPORANK_CLONE_TIMEOUT: Timeout for repository cloning in seconds
        - REPORANK_MAX_REPO_SIZE_MB: Maximum repository size in MB
        """
        # Determine LLM model and API key
        llm_model = os.getenv("REPORANK_LLM_MODEL", "gemini/gemini-2.0-flash")
        
        # Auto-detect API key based on model
        llm_api_key = None
        if "gemini" in llm_model.lower():
            llm_api_key = os.getenv("GEMINI_API_KEY")
        elif "openai" in llm_model.lower() or "gpt" in llm_model.lower():
            llm_api_key = os.getenv("OPENAI_API_KEY")
        elif "anthropic" in llm_model.lower() or "claude" in llm_model.lower():
            llm_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Parse boolean environment variables
        enable_local_clone = os.getenv("REPORANK_ENABLE_LOCAL_CLONE", "true").lower() in ("true", "1", "yes")
        
        # Parse log file (None if empty string)
        log_file = os.getenv("REPORANK_LOG_FILE", "reporank.log")
        if not log_file or log_file.lower() == "none":
            log_file = None
        
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
            llm_model=llm_model,
            llm_api_key=llm_api_key,
            llm_temperature=float(os.getenv("REPORANK_LLM_TEMPERATURE", "0.7")),
            llm_max_tokens=int(os.getenv("REPORANK_LLM_MAX_TOKENS", "1000")),
            output_dir=os.getenv("REPORANK_OUTPUT_DIR", "./output"),
            log_level=os.getenv("REPORANK_LOG_LEVEL", "INFO"),
            log_file=log_file,
            temp_dir=os.getenv("REPORANK_TEMP_DIR", "/tmp/reporank"),
            enable_local_clone=enable_local_clone,
            clone_timeout=int(os.getenv("REPORANK_CLONE_TIMEOUT", "300")),
            max_repo_size_mb=int(os.getenv("REPORANK_MAX_REPO_SIZE_MB", "500")),
        )
    
    def get_llm_api_key(self) -> Optional[str]:
        """
        Get the appropriate API key for the configured LLM model.
        
        Returns:
            API key string or None if not configured
        """
        if self.llm_api_key:
            return self.llm_api_key
        
        # Fallback to environment variables
        if "gemini" in self.llm_model.lower():
            return os.getenv("GEMINI_API_KEY")
        elif "openai" in self.llm_model.lower() or "gpt" in self.llm_model.lower():
            return os.getenv("OPENAI_API_KEY")
        elif "anthropic" in self.llm_model.lower() or "claude" in self.llm_model.lower():
            return os.getenv("ANTHROPIC_API_KEY")
        
        return None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate configuration settings.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check LLM API key
        api_key = self.get_llm_api_key()
        if not api_key:
            return False, f"No API key found for LLM model '{self.llm_model}'. Please set the appropriate environment variable."
        
        # Validate temperature
        if not 0.0 <= self.llm_temperature <= 2.0:
            return False, f"LLM temperature must be between 0.0 and 2.0, got {self.llm_temperature}"
        
        # Validate max tokens
        if self.llm_max_tokens < 1:
            return False, f"LLM max_tokens must be positive, got {self.llm_max_tokens}"
        
        # Validate timeout
        if self.clone_timeout < 1:
            return False, f"Clone timeout must be positive, got {self.clone_timeout}"
        
        # Validate max repo size
        if self.max_repo_size_mb < 1:
            return False, f"Max repo size must be positive, got {self.max_repo_size_mb}"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary (excluding sensitive data).
        
        Returns:
            Dictionary representation of configuration
        """
        config_dict = {
            "github_api_base_url": self.github_api_base_url,
            "api_timeout": self.api_timeout,
            "max_retries": self.max_retries,
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "llm_max_tokens": self.llm_max_tokens,
            "temp_dir": self.temp_dir,
            "output_dir": self.output_dir,
            "log_level": self.log_level,
            "enable_local_clone": self.enable_local_clone,
            "clone_timeout": self.clone_timeout,
            "max_repo_size_mb": self.max_repo_size_mb,
            "max_files_for_analysis": self.max_files_for_analysis,
        }
        
        # Add flags for sensitive data (but not the actual values)
        config_dict["has_github_token"] = bool(self.github_token)
        config_dict["has_llm_api_key"] = bool(self.get_llm_api_key())
        
        return config_dict


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    If not initialized, creates a new configuration from environment variables.
    
    Returns:
        Global Config instance
    """
    global _global_config
    if _global_config is None:
        _global_config = Config.from_env()
    return _global_config


def set_config(config: Config) -> None:
    """
    Set the global configuration instance.
    
    Args:
        config: Configuration instance to set as global
    """
    global _global_config
    _global_config = config


def reset_config() -> None:
    """
    Reset the global configuration instance.
    
    Useful for testing or when configuration needs to be reloaded.
    """
    global _global_config
    _global_config = None
