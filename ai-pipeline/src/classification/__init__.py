"""
Classification Module

This module provides classification functionality for the AI Pipeline:
- Rule-based filtering for obvious patterns
- BERT zero-shot classification for pedagogical vs nonsensical

Main Functions:
- classify_single(): Classify a single text
- classify_batch(): Classify multiple texts
- filter_pedagogical(): Filter to only pedagogical feedback
- get_statistics(): Get classification statistics
"""

# Rule-based filter exports
from .rule_based_filter import (
    ClassificationLabel,
    RuleResult,
    classify_with_rules,
    batch_classify,
)

# BERT classifier exports
from .bert_classifier import (
    ClassificationResult,
    classify_single,
    classify_batch,
    filter_pedagogical,
    get_statistics,
    load_classifier,
)


__version__ = "1.0.0"
