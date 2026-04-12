"""
Local ABSA Module (Aspect-Based Sentiment Analysis)

Extracts aspect, issue, and polarity from pedagogical feedback.
Currently using heuristic-based logic.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ProblemResult:
    aspect: Optional[str]
    issue: Optional[str]
    polarity: Optional[str]
    confidence: float = 0.0

def extract_absa(text: str) -> ProblemResult:
    """
    Extract aspect, issue, and polarity using local heuristics.
    """
    text_lower = text.lower()
    
    # 1. Check for 'examples' aspect
    if "example" in text_lower or "examples" in text_lower:
        return ProblemResult(
            aspect="examples", 
            issue="need_more_examples", 
            polarity="negative", 
            confidence=0.9
        )
    
    # 2. Check for 'pace' aspect
    if "fast" in text_lower or "too fast" in text_lower:
        return ProblemResult(
            aspect="pace", 
            issue="pace_too_fast", 
            polarity="negative", 
            confidence=0.9
        )
    
    # 3. Default (Generic confusion)
    return ProblemResult(
        aspect=None, 
        issue="difficulty_understanding_explanation", 
        polarity="negative", 
        confidence=0.6
    )
