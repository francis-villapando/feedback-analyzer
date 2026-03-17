"""
RoBERTa Strategy Mapper Module

This module provides strategy mapping functionality:
- Maps detected learning problems to specific teaching strategies
- Uses RoBERTa zero-shot classification to recommend the best strategy

IMPORTANT: Returns ONE strategy per problem detected.
- If 2 problems detected → 2 strategies (one per problem)
- If 1 problem detected → 1 strategy

Note: This implementation uses RoBERTa zero-shot classification.
"""

import warnings
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Suppress warnings
warnings.filterwarnings("ignore")

# Import configuration
try:
    from config.settings import ROBERTA_STRATEGY_CONFIG
except ImportError:
    ROBERTA_STRATEGY_CONFIG = {
        "model_name": "roberta-base",
        "max_length": 128,
        # Candidate strategies for each problem (RoBERTa will pick the best one)
        "strategy_candidates": {
            "misconception_about_concept": [
                "Provide a concrete real-world example that illustrates this concept",
                "Create a simple diagram showing how this concept works",
                "Address this misconception directly by explaining why it is incorrect",
                "Use an analogy that relates to everyday life"
            ],
            "difficulty_understanding_explanation": [
                "Break down this explanation into 3 smaller parts and explain each separately",
                "Rephrase this concept using simpler words and shorter sentences",
                "Use a step-by-step approach with visual aids",
                "Ask students what specific part they do not understand"
            ],
            "need_more_examples": [
                "Provide 3 additional worked examples with complete solutions",
                "Show examples from different contexts or applications",
                "Create a practice problem similar to the one just presented",
                "Share links to online resources with more examples"
            ],
            "pace_too_fast": [
                "Pause for 30 seconds and ask if anyone has questions",
                "Repeat the last explanation more slowly",
                "Allow students to take notes before continuing",
                "Check for understanding by asking a quick question"
            ],
            "pace_too_slow": [
                "Proceed to the next topic",
                "Offer optional advanced material for faster learners",
                "Introduce a related side topic that builds on current knowledge",
                "Provide additional optional exercises for practice"
            ],
            "need_practical_application": [
                "Demonstrate how this concept is used in real-world situations",
                "Show a practical example from everyday life",
                "Connect this to a real problem students might encounter",
                "Include a hands-on activity or exercise"
            ],
            "unclear_instruction": [
                "Restate the instruction in a different way",
                "Write the instruction on the screen",
                "Provide a checklist of steps to follow",
                "Give a completed example as reference"
            ],
            "technical_difficulty": [
                "Provide a step-by-step tutorial for using the technical tool",
                "Share a video tutorial demonstrating the process",
                "Offer alternative ways to accomplish the same task",
                "Schedule a brief one-on-one session to help"
            ],
        },
    }


# Strategy mapping result
@dataclass
class StrategyResult:
    """Result from strategy mapping."""
    problem: str
    strategy: str  # Single strategy (not a list)
    confidence: float
    model_used: str = "roberta"


@dataclass
class FullMappingResult:
    """Full mapping result from problem detection to strategy."""
    text: str
    problem: str
    problem_confidence: float
    strategy: str  # Single strategy
    strategy_confidence: float


# Global classifier
_classifier = None


def load_classifier():
    """
    Load the RoBERTa zero-shot classification pipeline.
    
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
        print(f"Loading RoBERTa strategy mapper on {device_str}...")
        
        # Use RoBERTa for zero-shot classification
        _classifier = pipeline(
            "zero-shot-classification",
            model="roberta-base",
            device=device,
        )
        
        print("RoBERTa strategy mapper loaded successfully!")
        return _classifier
        
    except ImportError as e:
        raise ImportError(
            "transformers library not installed. "
            "Run: pip install transformers"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Failed to load strategy mapper: {e}"
        ) from e


def get_strategy_candidates() -> Dict[str, List[str]]:
    """
    Get the candidate strategies for each problem.
    
    Returns:
        Dictionary mapping problem to list of candidate strategies
    """
    return ROBERTA_STRATEGY_CONFIG.get("strategy_candidates", {})


def get_strategies_for_problem(problem: str) -> List[str]:
    """
    Get candidate strategies for a problem.
    
    Note: This returns candidates. Use get_recommended_strategy() to get the best one.
    
    Args:
        problem: Problem category name
        
    Returns:
        List of candidate strategies
    """
    candidates = get_strategy_candidates()
    
    # Try exact match
    if problem in candidates:
        return candidates[problem]
    
    # Try case-insensitive match
    for key, strategies in candidates.items():
        if key.lower() == problem.lower():
            return strategies
    
    # Return default strategies if no match
    return [
        "Check for understanding by asking a question",
        "Provide additional clarification",
        "Offer to answer any questions"
    ]


def get_recommended_strategy(problem: str, context: str = "") -> StrategyResult:
    """
    Get the RECOMMENDED (best) strategy for a problem using RoBERTa.
    
    This uses RoBERTa zero-shot to select the BEST strategy from candidates.
    Returns ONE strategy only.
    
    Args:
        problem: Problem category name
        context: Optional context (original feedback message)
        
    Returns:
        StrategyResult with the recommended strategy
    """
    classifier = load_classifier()
    candidates = get_strategies_for_problem(problem)
    
    if not candidates:
        return StrategyResult(
            problem=problem,
            strategy="Provide additional clarification",
            confidence=0.0,
            model_used="fallback"
        )
    
    # Create input for RoBERTa
    # Use context if provided, otherwise just use problem
    input_text = context if context else f"Student has problem: {problem}"
    
    # Create hypothesis template
    hypothesis_template = "The best teaching strategy is: {}."
    
    try:
        result = classifier(
            input_text,
            candidate_labels=candidates,
            hypothesis_template=hypothesis_template,
            multi_label=False,
            max_length=ROBERTA_STRATEGY_CONFIG.get("max_length", 128),
        )
        
        # Get the top strategy
        best_strategy = result["labels"][0]
        confidence = result["scores"][0]
        
        return StrategyResult(
            problem=problem,
            strategy=best_strategy,
            confidence=confidence,
            model_used="roberta"
        )
        
    except Exception as e:
        print(f"Warning: Strategy mapping failed: {e}")
        # Fallback to first candidate
        return StrategyResult(
            problem=problem,
            strategy=candidates[0] if candidates else "Provide additional clarification",
            confidence=0.0,
            model_used="fallback"
        )


def get_primary_strategy(problem: str) -> str:
    """
    Get the primary (best) strategy for a problem.
    
    Args:
        problem: Problem category name
        
    Returns:
        Best strategy string
    """
    result = get_recommended_strategy(problem)
    return result.strategy


def get_all_strategies(problem: str) -> StrategyResult:
    """
    Get the recommended strategy for a problem.
    
    Note: Returns ONE strategy (the best one), not a list.
    
    Args:
        problem: Problem category name
        
    Returns:
        StrategyResult with recommended strategy
    """
    return get_recommended_strategy(problem)


def map_problem_to_strategy(
    problem: str,
    context: str = ""
) -> StrategyResult:
    """
    Map a detected problem to the best teaching strategy.
    
    Returns ONE strategy per problem.
    
    Args:
        problem: Problem category name
        context: Optional context (original feedback message)
        
    Returns:
        StrategyResult with recommended strategy
    """
    return get_recommended_strategy(problem, context)


def map_problems_to_strategies(
    problems: List[Tuple[str, float]],
    contexts: Optional[List[str]] = None
) -> List[StrategyResult]:
    """
    Map multiple problems to strategies.
    
    Returns ONE strategy per problem (so if 2 problems, returns 2 strategies).
    
    Args:
        problems: List of (problem, confidence) tuples
        contexts: Optional list of context strings (original messages)
        
    Returns:
        List of StrategyResult (one per problem)
    """
    results = []
    
    for i, (problem, confidence) in enumerate(problems):
        context = contexts[i] if contexts and i < len(contexts) else ""
        result = get_recommended_strategy(problem, context)
        results.append(result)
    
    return results


def create_full_mapping(
    texts: List[str],
    problems: List[str],
    confidences: Optional[List[float]] = None
) -> List[FullMappingResult]:
    """
    Create full mapping from texts to strategies.
    
    This combines problem detection with strategy mapping.
    
    Args:
        texts: List of input texts
        problems: List of detected problem categories
        confidences: Optional list of confidence scores
        
    Returns:
        List of FullMappingResult (one per problem detected)
    """
    if confidences is None:
        confidences = [1.0] * len(texts)
    
    results = []
    
    for text, problem, confidence in zip(texts, problems, confidences):
        # Get recommended strategy using context
        strategy_result = get_recommended_strategy(problem, text)
        
        results.append(FullMappingResult(
            text=text,
            problem=problem,
            problem_confidence=confidence,
            strategy=strategy_result.strategy,
            strategy_confidence=strategy_result.confidence
        ))
    
    return results


def get_strategy_statistics(strategies: List[str]) -> Dict:
    """
    Get statistics on strategy usage.
    
    Args:
        strategies: List of strategy strings
        
    Returns:
        Dictionary with statistics
    """
    total = len(strategies)
    if total == 0:
        return {"total": 0}
    
    # Count by strategy
    strategy_counts = {}
    for strategy in strategies:
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    return {
        "total": total,
        "unique_strategies": len(strategy_counts),
        "strategy_counts": strategy_counts,
        "strategy_percentages": {
            s: (c / total) * 100 
            for s, c in strategy_counts.items()
        },
    }


# Test function
if __name__ == "__main__":
    # Sample problems to map
    test_problems = [
        "misconception_about_concept",
        "difficulty_understanding_explanation",
        "need_more_examples",
        "pace_too_fast",
    ]
    
    # Sample contexts (original feedback)
    test_contexts = [
        "I think the formula is wrong",
        "I don't understand what you mean",
        "Can you give more examples?",
        "Too fast! Please slow down",
    ]
    
    print("=" * 70)
    print("RoBERTa Strategy Mapping Test")
    print("=" * 70)
    print()
    
    for problem, context in zip(test_problems, test_contexts):
        result = get_recommended_strategy(problem, context)
        print(f"Problem: {problem}")
        print(f"Context: {context}")
        print(f"Recommended Strategy: {result.strategy}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Model: {result.model_used}")
        print("-" * 70)
    
    print()
    print("Strategy mapping test completed!")
