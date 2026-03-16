"""
RoBERTa Strategy Mapper Module

This module provides strategy mapping functionality:
- Maps detected learning problems to specific teaching strategies
- Uses predefined strategy mappings from configuration

IMPORTANT: Strategies are SPECIFIC and ACTIONABLE - they tell the educator
exactly what to do to address the student's problem.

Note: This implementation uses rule-based lookup for Phase 1.
Future versions may use fine-tuned models for more nuanced mapping.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Import configuration
try:
    from config.settings import ROBERTA_STRATEGY_CONFIG
except ImportError:
    ROBERTA_STRATEGY_CONFIG = {
        "model_name": "roberta-base",
        "strategy_mappings": {
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
                "Proceed to the next topic: [suggest next topic]",
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
    strategies: List[str]
    primary_strategy: str
    is_fallback: bool  # True if no specific mapping found


@dataclass
class FullMappingResult:
    """Full mapping result from problem detection to strategy."""
    text: str
    problem: str
    problem_confidence: float
    strategies: List[str]
    primary_strategy: str


def get_strategy_mappings() -> Dict[str, List[str]]:
    """
    Get the strategy mappings from config.
    
    Returns:
        Dictionary mapping problem to strategies
    """
    return ROBERTA_STRATEGY_CONFIG.get("strategy_mappings", {})


def get_strategies_for_problem(problem: str) -> List[str]:
    """
    Get teaching strategies for a specific problem.
    
    Args:
        problem: Problem category name
        
    Returns:
        List of strategy suggestions
    """
    mappings = get_strategy_mappings()
    
    # Try exact match first
    if problem in mappings:
        return mappings[problem]
    
    # Try case-insensitive match
    for key, strategies in mappings.items():
        if key.lower() == problem.lower():
            return strategies
    
    # Return default strategies if no match
    return [
        "Check for understanding by asking a question",
        "Provide additional clarification",
        "Offer to answer any questions"
    ]


def get_primary_strategy(problem: str) -> str:
    """
    Get the primary (best) strategy for a problem.
    
    For Phase 1, this returns a random strategy from the list.
    Future versions could use ML to select the best one.
    
    Args:
        problem: Problem category name
        
    Returns:
        Primary strategy suggestion
    """
    strategies = get_strategies_for_problem(problem)
    
    if strategies:
        # Return first strategy as primary (most recommended)
        return strategies[0]
    
    return "Provide additional clarification and check for understanding"


def get_all_strategies(problem: str, include_defaults: bool = True) -> StrategyResult:
    """
    Get all strategies for a problem.
    
    Args:
        problem: Problem category name
        include_defaults: Whether to include default strategies if no mapping found
        
    Returns:
        StrategyResult with all strategies
    """
    mappings = get_strategy_mappings()
    
    # Try to find exact match
    strategies = mappings.get(problem, [])
    is_fallback = len(strategies) == 0
    
    if not strategies and include_defaults:
        strategies = [
            "Check for understanding by asking a question",
            "Provide additional clarification",
            "Offer to answer any questions"
        ]
        is_fallback = True
    
    return StrategyResult(
        problem=problem,
        strategies=strategies,
        primary_strategy=strategies[0] if strategies else "Provide additional clarification",
        is_fallback=is_fallback
    )


def map_problem_to_strategy(
    problem: str,
    return_all: bool = False
) -> StrategyResult:
    """
    Map a detected problem to teaching strategies.
    
    Args:
        problem: Problem category name
        return_all: If True, return all strategies; if False, return just primary
        
    Returns:
        StrategyResult
    """
    return get_all_strategies(problem)


def map_problems_to_strategies(
    problems: List[Tuple[str, float]]
) -> List[StrategyResult]:
    """
    Map multiple problems to strategies.
    
    Args:
        problems: List of (problem, confidence) tuples
        
    Returns:
        List of StrategyResult
    """
    results = []
    
    for problem, confidence in problems:
        result = get_all_strategies(problem)
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
        List of FullMappingResult
    """
    if confidences is None:
        confidences = [1.0] * len(texts)
    
    results = []
    
    for text, problem, confidence in zip(texts, problems, confidences):
        strategies = get_strategies_for_problem(problem)
        
        results.append(FullMappingResult(
            text=text,
            problem=problem,
            problem_confidence=confidence,
            strategies=strategies,
            primary_strategy=strategies[0] if strategies else "Provide additional clarification"
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
    
    # Count by first strategy (primary)
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
        "pace_too_slow",
        "need_practical_application",
        "unclear_instruction",
        "technical_difficulty",
    ]
    
    print("=" * 70)
    print("Strategy Mapping Test")
    print("=" * 70)
    print()
    
    for problem in test_problems:
        result = get_all_strategies(problem)
        print(f"Problem: {problem}")
        print(f"Primary Strategy: {result.primary_strategy}")
        print(f"All Strategies ({len(result.strategies)}):")
        for i, strategy in enumerate(result.strategies, 1):
            print(f"  {i}. {strategy}")
        print("-" * 70)
    
    print()
    print("Strategy mapping test completed!")
