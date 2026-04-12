"""
Local CBR Module (Case-Based Reasoning)

Maps issues to teaching strategies.
Currently using deterministic mapping logic.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class StrategyResult:
    strategy: str
    reason: str = "local_mapping"

def get_strategy(aspect: Optional[str], issue: Optional[str], context: Optional[str] = None) -> StrategyResult:
    """
    Map an issue to a strategy using local logic.
    """
    if issue == "need_more_examples":
        return StrategyResult(strategy="Provide additional worked examples")
    
    if issue == "pace_too_fast":
        return StrategyResult(strategy="Slow down and check for understanding")
    
    return StrategyResult(strategy="Ask clarifying question to pinpoint confusion", reason="local_default")
