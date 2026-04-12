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
        ("instructional pacing and speed", "too_fast"): "Stop the lecture. Provide a snippet of the current algorithm and ask students to trace the pointer values in the chat before moving to the next traversal step.",
        ("instructional pacing and speed", "too_slow"): "Increase depth. Transition from basic implementation to a big O complexity comparison. Challenge students to calculate the worst-case time complexity of the current structure immediately.",
        ("clarity of examples and slides", "unclear_example"): "Instead of code, use a virtual whiteboard to draw the heap/stack memory layout of the current structure.",
        ("clarity of examples and slides", "need_more_examples"): "Present a non-trivial case, such as deleting the root of a multi-level tree or inserting into an empty list, to demonstrate boundary conditions.",
        ("content difficulty and logic", "not_understand"): "Re-anchor the data structure to a tangible object and use a think-aloud walkthrough of the logic flow.",
        ("content difficulty and logic", "too_complex"): "Break down the complex algorithm into its base cases. Focus exclusively on the divide logic before attempting to explain the merge logic.",
        ("technical connection and audio", "audio_problem"): "Switch to code-only mode. Post the full source code link in chat and provide 1-line logic comments while troubleshooting the audio connection.",
        ("technical connection and audio", "video_problem"): "Disable video. Switch to live-coding via terminal or a lightweight IDE. Ask students for a thumbs-up in chat if the text clarity on the code terminal is readable."
    }
    
    key = (aspect, issue)
    if key in curated_cases:
        return StrategyResult(strategy=curated_cases[key])
    
    # Fallback if not perfectly matched
    return StrategyResult(strategy="Ask clarifying question to pinpoint confusion", reason="local_default")
