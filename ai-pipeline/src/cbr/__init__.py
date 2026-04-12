"""
Local CBR Module (Case-Based Reasoning)

Maps issues to teaching strategies.
Prototype uses Curated CBR Database with strict Aspect+Issue matching.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class StrategyResult:
    strategy: str
    reason: str = "curated_database"

def get_strategy(aspect: Optional[str], issue: Optional[str], context: Optional[str] = None) -> StrategyResult:
    """
    Map an aspect and issue to a strategy using the Curated CBR Database.
    """
    curated_cases = {
        ("pace of session", "too_fast"): "Pause technical delivery. Ask students which specific part was missed and recap slowly.",
        ("pace of session", "too_slow"): "Summarize current points and move to the next activity/example immediately.",
        ("clarity of examples", "unclear_example"): "Use a physical analogy or a real-world scenario to visualize the current concept.",
        ("clarity of examples", "need_more_examples"): "Provide 2 more distinct examples before proceeding to the next topic.",
        ("content difficulty", "not_understand"): "Check for missing prerequisites. Ask: 'Did we understand [Prior Concept]?'",
        ("content difficulty", "too_complex"): "Break down the concept into smaller, digestible segments.",
        ("technical issues", "audio_problem"): "Verify microphone settings. Use the Jitsi chat to provide written summaries while fixing.",
        ("technical issues", "video_problem"): "Turn off video to save bandwidth or switch to screen sharing only.",
        ("instruction quality", "unclear_instructions"): "Re-state the instructions in 3 simple steps on the screen."
    }
    
    key = (aspect, issue)
    if key in curated_cases:
        return StrategyResult(strategy=curated_cases[key])
    
    # Fallback if not perfectly matched
    return StrategyResult(strategy="Ask clarifying question to pinpoint confusion", reason="local_default")
