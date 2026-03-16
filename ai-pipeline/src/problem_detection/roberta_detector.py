"""
RoBERTa Problem Detector Module

This module provides problem detection using RoBERTa zero-shot classification.

Problem categories:
- misconception_about_concept: Student has wrong understanding
- difficulty_understanding_explanation: Can't follow the explanation
- need_more_examples: Needs additional examples
- pace_too_fast: Teaching pace is too quick
- pace_too_slow: Teaching pace is too slow
- need_practical_application: Wants real-world application
- unclear_instruction: Instructions not clear
- technical_difficulty: Technical issues

Note: This implementation uses ZERO-SHOT classification for Phase 1.
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Import configuration
try:
    from config.settings import ROBERTA_PROBLEM_CONFIG
except ImportError:
    ROBERTA_PROBLEM_CONFIG = {
        "model_name": "roberta-base",
        "max_length": 128,
        "problem_categories": [
            "misconception_about_concept",
            "difficulty_understanding_explanation",
            "need_more_examples",
            "pace_too_fast",
            "pace_too_slow",
            "need_practical_application",
            "unclear_instruction",
            "technical_difficulty",
        ],
    }


# Problem detection result
@dataclass
class ProblemResult:
    """Result from problem detection."""
    text: str
    problem: str
    confidence: float
    all_scores: Dict[str, float]


# Global classifier
_classifier = None


def get_problem_categories() -> List[str]:
    """
    Get the problem categories from config.
    
    Returns:
        List of problem category labels
    """
    return ROBERTA_PROBLEM_CONFIG.get("problem_categories", [])


def get_problem_display_names() -> Dict[str, str]:
    """
    Get human-readable names for problem categories.
    
    Returns:
        Dictionary mapping category to display name
    """
    return {
        "misconception_about_concept": "Misconception About Concept",
        "difficulty_understanding_explanation": "Difficulty Understanding Explanation",
        "need_more_examples": "Need More Examples",
        "pace_too_fast": "Pace Too Fast",
        "pace_too_slow": "Pace Too Slow",
        "need_practical_application": "Need Practical Application",
        "unclear_instruction": "Unclear Instruction",
        "technical_difficulty": "Technical Difficulty",
    }


def load_classifier():
    """
    Load the zero-shot classification pipeline for problem detection.
    
    Returns:
        transformers pipeline
    """
    global _classifier
    
    if _classifier is not None:
        return _classifier
    
    try:
        from transformers import pipeline
        import torch
        
        # Check for GPU
        device = 0 if torch.cuda.is_available() else -1
        device_str = "GPU" if device == 0 else "CPU"
        print(f"Loading RoBERTa problem detector on {device_str}...")
        
        # Use RoBERTa-based NLI model for zero-shot classification
        # NLI models can be used for zero-shot by checking entailment against labels
        _classifier = pipeline(
            "zero-shot-classification",
            model="roberta-base",
            device=device,
        )
        
        print("RoBERTa problem detector loaded successfully!")
        return _classifier
        
    except ImportError as e:
        raise ImportError(
            "transformers library not installed. "
            "Run: pip install transformers"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Failed to load problem detector: {e}"
        ) from e


def detect_problem(text: str) -> ProblemResult:
    """
    Detect learning problem in a single text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        ProblemResult with detected problem and confidence
    """
    classifier = load_classifier()
    
    candidate_labels = get_problem_categories()
    
    # Hypothesis template for better classification
    hypothesis_template = "This is a student problem about {}."
    
    try:
        result = classifier(
            text,
            candidate_labels=candidate_labels,
            hypothesis_template=hypothesis_template,
            multi_label=False,
            max_length=ROBERTA_PROBLEM_CONFIG.get("max_length", 128),
        )
        
        # Get top prediction
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        # Get all scores as dict
        all_scores = {
            label: score 
            for label, score in zip(result["labels"], result["scores"])
        }
        
        return ProblemResult(
            text=text,
            problem=top_label,
            confidence=top_score,
            all_scores=all_scores,
        )
        
    except Exception as e:
        print(f"Warning: Problem detection failed: {e}")
        return ProblemResult(
            text=text,
            problem="unknown",
            confidence=0.0,
            all_scores={},
        )


def detect_problems_batch(texts: List[str]) -> List[ProblemResult]:
    """
    Detect problems in a batch of texts.
    
    Args:
        texts: List of input texts
        
    Returns:
        List of ProblemResult objects
    """
    return [detect_problem(text) for text in texts]


def filter_by_problem(
    texts: List[str],
    problems: Optional[List[str]] = None,
    min_confidence: float = 0.3
) -> Tuple[List[str], List[ProblemResult]]:
    """
    Filter texts by specific problems.
    
    Args:
        texts: List of input texts
        problems: List of problem categories to keep (None = keep all)
        min_confidence: Minimum confidence threshold
        
    Returns:
        Tuple of (filtered_texts, all_results)
    """
    results = detect_problems_batch(texts)
    
    filtered = []
    for result in results:
        if problems is not None:
            if result.problem in problems and result.confidence >= min_confidence:
                filtered.append(result.text)
        else:
            if result.confidence >= min_confidence:
                filtered.append(result.text)
    
    return filtered, results


def get_problem_statistics(results: List[ProblemResult]) -> Dict:
    """
    Get statistics from problem detection results.
    
    Args:
        results: List of ProblemResult objects
        
    Returns:
        Dictionary with statistics
    """
    total = len(results)
    if total == 0:
        return {"total": 0}
    
    # Count by problem
    problem_counts = {}
    for result in results:
        problem_counts[result.problem] = problem_counts.get(result.problem, 0) + 1
    
    # Average confidence
    avg_confidence = sum(r.confidence for r in results) / total
    
    # Get display names
    display_names = get_problem_display_names()
    
    return {
        "total": total,
        "problem_counts": problem_counts,
        "average_confidence": avg_confidence,
        "problem_percentages": {
            problem: (count / total) * 100 
            for problem, count in problem_counts.items()
        },
        "display_names": display_names,
    }


# Test function
if __name__ == "__main__":
    # Sample pedagogical feedback messages
    test_messages = [
        # Misconception
        "I think the formula is wrong",
        "Shouldn't it be division instead?",
        "I believe that's incorrect",
        
        # Difficulty understanding
        "I don't understand what you mean",
        "This is confusing",
        "Can't follow the explanation",
        
        # Need more examples
        "Can you give another example?",
        "Need more examples please",
        "Like the previous example",
        
        # Pace too fast
        "Too fast!",
        "Please slow down",
        "Can't keep up with the speed",
        
        # Pace too slow
        "Can we move faster?",
        "This is too slow",
        "Boring, let's proceed",
        
        # Need practical application
        "When will we use this in real life?",
        "How is this useful?",
        "Can you show practical use?",
        
        # Unclear instruction
        "What are we supposed to do?",
        "The instructions are not clear",
        "I don't know what to do next",
        
        # Technical difficulty
        "The video is not loading",
        "Can't hear the audio",
        "The screen is frozen",
    ]
    
    print("=" * 70)
    print("RoBERTa Problem Detection Test")
    print("=" * 70)
    print()
    
    # Test detection
    results = detect_problems_batch(test_messages)
    
    for result in results:
        print(f"Text: {result.text}")
        print(f"Problem: {result.problem}")
        print(f"Confidence: {result.confidence:.3f}")
        print("-" * 70)
    
    # Statistics
    print()
    stats = get_problem_statistics(results)
    print("Statistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Average confidence: {stats['average_confidence']:.3f}")
    print("  Problem distribution:")
    for problem, count in stats["problem_counts"].items():
        pct = stats["problem_percentages"][problem]
        name = stats["display_names"].get(problem, problem)
        print(f"    {name}: {count} ({pct:.1f}%)")
    
    print()
    print("Problem detection test completed!")
