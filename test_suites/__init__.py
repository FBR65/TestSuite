"""
Test Suiten Modul für das TestSuite System
"""
from .base_suite import BaseTestSuite
from .general_llm import GeneralLLMTestSuite
from .coding_model import CodingModelTestSuite
from .audio_model import AudioModelTestSuite
from .vlm_suite import VLMTestSuite

__all__ = [
    'BaseTestSuite',
    'GeneralLLMTestSuite',
    'CodingModelTestSuite', 
    'AudioModelTestSuite',
    'VLMTestSuite'
]