"""
DSPy modules and signatures for LLM-based repository evaluation.

This module defines custom DSPy signatures for various evaluation dimensions
including language detection, code architecture, production readiness,
learning value, and security posture.

IMPORTANT:
As prt of capstone project readers are expected to implement signatures for 
code architecture, production readiness, learning value, and security posture.
Language detection provided as a reference.
"""

import dspy
from typing import List, Dict, Any

# Configure DSPy with Gemini language model
def configure_dspy(model: str = 'gemini/gemini-2.0-flash'):
    """Configure DSPy with the specified language model.
    
    Args:
        model: Model identifier (default: gemini/gemini-2.0-flash)
    """
    lm = dspy.LM(model)
    dspy.configure(lm=lm)


class LanguageDetection(dspy.Signature):
    """Determine programming languages from file extensions.
    
    Analyzes file extension counts to identify programming languages used
    in the repository, determine the dominant language, and provide reasoning.
    """
    
    extension_counts: str = dspy.InputField(
        desc="File extension counts as JSON string (e.g., '{'.py': 150, '.js': 45}')"
    )
    
    languages: str = dspy.OutputField(
        desc="Comma-separated list of programming languages detected"
    )
    
    dominant_language: str = dspy.OutputField(
        desc="Primary/dominant programming language in the repository"
    )
    
    reasoning: str = dspy.OutputField(
        desc="Brief explanation of how languages were determined from extensions"
    )