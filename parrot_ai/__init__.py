"""
ParrotAI: A package for theological AI reasoning and response generation.

This package provides tools for loading language models, generating responses
with theological prompts, and executing multi-step reasoning chains.
"""

from .core import ParrotAI, ParrotAIHF
from .chains import parrot_chain

__version__ = "0.1.0"
__all__ = ["ParrotAI", "ParrotAIHF", "parrot_chain"]
