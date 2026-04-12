"""
Classification Module API
"""
from .xlm_roberta_classifier import classify, classify_batch, ClassificationResult, ClassificationLabel

__all__ = ["classify", "classify_batch", "ClassificationResult", "ClassificationLabel"]
