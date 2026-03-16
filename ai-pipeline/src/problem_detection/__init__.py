"""
Problem Detection Module

This module provides problem detection functionality:
- Detect learning problems from pedagogical feedback
- Uses RoBERTa zero-shot classification

Problem categories:
- misconception_about_concept
- difficulty_understanding_explanation
- need_more_examples
- pace_too_fast
- pace_too_slow
- need_practical_application
- unclear_instruction
- technical_difficulty

Main Functions:
- detect_problem(): Detect problem in single text
- detect_problems_batch(): Detect problems in multiple texts
- filter_by_problem(): Filter by specific problems
- get_problem_statistics(): Get detection statistics
"""

from .roberta_detector import (
    ProblemResult,
    get_problem_categories,
    get_problem_display_names,
    load_classifier,
    detect_problem,
    detect_problems_batch,
    filter_by_problem,
    get_problem_statistics,
)


__version__ = "1.0.0"
