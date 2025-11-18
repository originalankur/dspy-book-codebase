"""
LLM Evaluator for repository quality assessment using DSPy.

This module provides LLM-powered qualitative analysis of repositories
across multiple dimensions including code architecture, production readiness,
learning value, and security posture.
"""

import time
import json
import statistics
from typing import Dict, List, Any, Optional
from models.repository_data import RepositoryData
from data_analysis.dspy_modules import (
    LanguageDetection,
    CodeArchitectureEvaluation,
    ProductionReadinessEvaluation,
    LearningValueEvaluation,
    SecurityPostureEvaluation,
)
from data_analysis.guardrails import ScoreGuardrail
from utils.logger import get_logger
from config import get_config

import dspy

logger = get_logger(__name__)


class LLMEvaluator:
    """
    LLM-powered evaluator for repository quality assessment.
    
    Uses DSPy with Gemini to perform qualitative analysis across multiple
    dimensions including code architecture, production readiness, learning
    value, and security posture.
    """
    
    def __init__(
        self,
        llm_model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize LLM evaluator with DSPy configuration.
        
        Uses centralized configuration from Config class if parameters not provided.
        
        Args:
            llm_model: Model identifier (uses Config.llm_model if not provided)
            temperature: Sampling temperature for LLM (uses Config.llm_temperature if not provided)
            max_tokens: Maximum tokens for LLM responses (uses Config.llm_max_tokens if not provided)
            api_key: API key for LLM provider (auto-detected from Config if not provided)
        """
        # Import config here to avoid circular imports
        
        config = get_config()
        
        # Use config values if not explicitly provided
        llm_model = llm_model or config.llm_model
        temperature = temperature if temperature is not None else config.llm_temperature
        max_tokens = max_tokens if max_tokens is not None else config.llm_max_tokens
        api_key = api_key or config.get_llm_api_key()
        
        logger.info(f"Initializing LLM evaluator with model: {llm_model}")
        
        # Validate API key
        if not api_key:
            logger.warning(
                f"No API key found for model '{llm_model}'. "
                "LLM evaluations may fail. Please set the appropriate environment variable."
            )
        
        # Configure DSPy with the specified model
        lm = dspy.LM(llm_model, temperature=temperature, max_tokens=max_tokens, api_key=api_key)
        dspy.configure(lm=lm)
        
        # Initialize DSPy modules
        self.language_detector = dspy.Predict(LanguageDetection)

        # PLACEHOLDER DSPy modules that you should create
        self.code_architecture_cot = None
        self.production_readiness_predict = None
        self.learning_value_cot = None
        self.security_posture_cot = None
                
        # Store max retries for LLM calls
        self.max_retries = 3
        
        logger.info("LLM evaluator initialized successfully")