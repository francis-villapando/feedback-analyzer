"""
Cognitive Mapping Module (RBT + CLT)

This module maps detected issues to pedagogical frameworks:
- Revised Bloom's Taxonomy (RBT)
- Cognitive Load Theory (CLT)
"""

from typing import Dict, Optional, Tuple

class RBTLevel:
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

class CLTType:
    INTRINSIC = "intrinsic"
    EXTRANEOUS = "extraneous"

# Mapping logic: (Issue, Aspect) -> RBT Level
_RBT_MAPPING = {
    ("misconception", "explanation"): RBTLevel.UNDERSTAND,
    ("unclear", "explanation"): RBTLevel.UNDERSTAND,
    ("too_complex", "explanation"): RBTLevel.ANALYZE,
    ("need_practical_application", "examples"): RBTLevel.APPLY,
    ("not_enough", "examples"): RBTLevel.APPLY,
    ("too_fast", "pace"): RBTLevel.ANALYZE,
    ("too_slow", "pace"): RBTLevel.EVALUATE,
}

# Mapping logic: (Issue, Aspect) -> CLT Type
_CLT_MAPPING = {
    ("too_complex", "explanation"): CLTType.INTRINSIC,
    ("misconception", "difficulty"): CLTType.INTRINSIC,
    ("unclear", "instruction"): CLTType.EXTRANEOUS,
    ("too_fast", "pace"): CLTType.EXTRANEOUS,
    ("not_enough", "examples"): CLTType.INTRINSIC, # Germane-like but restricted to Intrinsic/Extraneous
}

def map_to_rbt(issue: str, aspect: str) -> str:
    """Map an issue to an RBT cognitive level."""
    # Look for exact match
    level = _RBT_MAPPING.get((issue, aspect))
    if level:
        return level
    
    # Heuristic fallbacks if exact match fails
    issue_lower = issue.lower()
    if "understand" in issue_lower or "unclear" in issue_lower:
        return RBTLevel.UNDERSTAND
    if "example" in issue_lower or "apply" in issue_lower:
        return RBTLevel.APPLY
    if "fast" in issue_lower or "complex" in issue_lower:
        return RBTLevel.ANALYZE
    
    return RBTLevel.UNDERSTAND # Default

def map_to_clt(issue: str, aspect: str) -> str:
    """Map an issue to a CLT load type."""
    # Look for exact match
    clt_type = _CLT_MAPPING.get((issue, aspect))
    if clt_type:
        return clt_type
    
    # Heuristic fallbacks
    issue_lower = issue.lower()
    # Extraneous: Poorly designed instruction
    if any(kw in issue_lower for kw in ["fast", "slow", "unclear", "instruction", "technical", "platform"]):
        return CLTType.EXTRANEOUS
    
    # Intrinsic: Complex content
    return CLTType.INTRINSIC # Default

def get_cognitive_mapping(issue: Optional[str], aspect: Optional[str]) -> Tuple[str, str]:
    """Get both RBT and CLT mappings for an issue."""
    if not issue:
        return (RBTLevel.UNDERSTAND, CLTType.INTRINSIC)
    
    safe_aspect = aspect or "general"
    return (map_to_rbt(issue, safe_aspect), map_to_clt(issue, safe_aspect))
