"""
Rule-Based Filter Module

This module provides rule-based classification for obvious patterns
in feedback messages. Used as a pre-filter before BERT classification.

The hybrid approach:
- If rules clearly classify: return immediately
- If unclear: defer to BERT for classification

Note: This is for Phase 1 (Zero-Shot Development). The rules are simple
and designed to catch obvious cases. Accuracy will be improved in Phase 2.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# Classification labels
class ClassificationLabel:
    PEDAGOGICAL = "pedagogical"
    NONSENSICAL = "nonsensical"
    UNCLEAR = "unclear"


@dataclass
class RuleResult:
    """Result from rule-based classification."""
    label: str
    confidence: float  # 0.0 to 1.0
    reason: str
    is_clear: bool  # True if confident enough to return directly


# Patterns that indicate PEDAGOGICAL feedback (learning-related)
PEDAGOGICAL_PATTERNS = [
    # Understanding indicators
    (r"\b(understand|understanding|understood)\b", 0.8, "explicit understanding"),
    (r"\b(not understand|don't understand|dont understand|don't get|not clear|confused)\b", 0.7, "confusion about concept"),
    (r"\b(explain|explain more|explain again|clarify|clarification)\b", 0.8, "request for explanation"),
    (r"\b(example|examples|like an example|more example)\b", 0.7, "request for examples"),
    (r"\b(question|ask|asking|may question)\b", 0.6, "question about content"),
    (r"\b(learn|learning|learned|lesson)\b", 0.8, "learning related"),
    (r"\b(teach|teaching|teacher|tutor)\b", 0.7, "teaching related"),
    (r"\b(concept|topic|subtopic|lesson)\b", 0.7, "content related"),
    (r"\b(difficult|hard|easy|simple|complicated)\b", 0.5, "difficulty feedback"),
    (r"\b(fast|slow|quick|speed|pace)\b", 0.6, "pace feedback"),
    (r"\b(thanks?|thank you|maraming salamat|salamat po)\b", 0.6, "gratitude (positive engagement)"),
    (r"\b(good|great|excellent|nice|helpful|useful)\b", 0.6, "positive feedback"),
    (r"\b(wrong|incorrect|mistake|error|misconception)\b", 0.7, "correction/issue"),
    (r"\b(step|steps|procedure|process|how to)\b", 0.6, "procedure related"),
    (r"\b(formula|equation|solution|answer|calculate|compute)\b", 0.7, "math/calculation"),
    (r"\b(pwede|puede|can i|may I|allowed|permission)\b", 0.5, "permission/request"),
    
    # Tagalog-English codeswitching pedagogical patterns
    (r"\b(po|ako|siya|kami|tayo|kayo|sila)\b", 0.3, "Filipino pronouns (context)"),
    (r"\b(yung|ang|ng|mga|sa|saan|ano|paano|bakit)\b", 0.4, "Filipino question words"),
]

# Patterns that indicate NONSENSICAL or LOW-VALUE feedback
NONSENSICAL_PATTERNS = [
    # Spam/junk
    (r"\b(http|www\.|\.com|\.net)\b", 0.9, "contains URL/link"),
    (r"\b(buy|sell|discount|free money|win prize|lottery)\b", 0.9, "spam content"),
    (r"\b(click here|subscribe|follow me|join now)\b", 0.9, "solicitation"),
    
    # Random/unintelligible
    (r"^[a-zA-Z]{1,3}$", 0.8, "too short/meaningless"),
    (r"^[\W]+$", 0.9, "only symbols"),
    (r"\b(asdf|qwerty|12345|abcde)\b", 0.9, "random keyboard smash"),
    (r"(.)\1{5,}", 0.8, "repeated characters"),
    
    # Non-feedback
    (r"\b(hi|hello|hey|yo|sup|what's up)\b", 0.7, "greeting only"),
    (r"\b(ok|okay|yes|no|yeah|nope)\b", 0.6, "minimal response"),
    (r"^\s*$", 1.0, "empty/whitespace only"),
    
    # Emotion/expression only (may or may not be pedagogical)
    (r"^[😀😂🤣😊😍🎉👍👏💯]+$", 0.4, "emoji only"),
]


def check_pedagogical_patterns(text: str) -> Tuple[bool, float, str]:
    """
    Check if text matches pedagogical patterns.
    
    Args:
        text: Input text to check
        
    Returns:
        Tuple of (is_pedagogical, confidence, reason)
    """
    text_lower = text.lower()
    
    for pattern, confidence, reason in PEDAGOGICAL_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True, confidence, reason
    
    return False, 0.0, ""


def check_nonsensical_patterns(text: str) -> Tuple[bool, float, str]:
    """
    Check if text matches nonsensical patterns.
    
    Args:
        text: Input text to check
        
    Returns:
        Tuple of (is_nonsensical, confidence, reason)
    """
    text_lower = text.lower()
    
    for pattern, confidence, reason in NONSENSICAL_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True, confidence, reason
    
    return False, 0.0, ""


def classify_with_rules(text: str) -> RuleResult:
    """
    Main rule-based classification function.
    
    Applies rules in order of confidence:
    1. Check for nonsensical patterns (high confidence = return immediately)
    2. Check for pedagogical patterns (high confidence = return immediately)
    3. If neither clearly matches, return unclear
    
    Args:
        text: Input text to classify
        
    Returns:
        RuleResult with classification
    """
    if not text or not text.strip():
        return RuleResult(
            label=ClassificationLabel.NONSENSICAL,
            confidence=1.0,
            reason="empty or whitespace input",
            is_clear=True
        )
    
    # Check nonsensical patterns first (higher priority for spam/junk)
    is_nonsensical, nonsens_confidence, nonsens_reason = check_nonsensical_patterns(text)
    if is_nonsensical and nonsens_confidence >= 0.7:  # Lowered from 0.8 to catch greetings
        return RuleResult(
            label=ClassificationLabel.NONSENSICAL,
            confidence=nonsens_confidence,
            reason=nonsens_reason,
            is_clear=True
        )
    
    # Check pedagogical patterns
    is_pedagogical, pedag_confidence, pedag_reason = check_pedagogical_patterns(text)
    if is_pedagogical and pedag_confidence >= 0.6:
        return RuleResult(
            label=ClassificationLabel.PEDAGOGICAL,
            confidence=pedag_confidence,
            reason=pedag_reason,
            is_clear=True
        )
    
    # If we have moderate confidence in either direction, return with lower confidence
    if is_nonsensical:
        return RuleResult(
            label=ClassificationLabel.NONSENSICAL,
            confidence=nonsens_confidence,
            reason=nonsens_reason,
            is_clear=False  # Not confident enough, let BERT decide
        )
    
    if is_pedagogical:
        return RuleResult(
            label=ClassificationLabel.PEDAGOGICAL,
            confidence=pedag_confidence,
            reason=pedag_reason,
            is_clear=False  # Not confident enough, let BERT decide
        )
    
    # No clear pattern matched - defer to BERT
    return RuleResult(
        label=ClassificationLabel.UNCLEAR,
        confidence=0.0,
        reason="no clear pattern matched",
        is_clear=False
    )


def batch_classify(texts: List[str]) -> List[RuleResult]:
    """
    Apply rule-based classification to a batch of texts.
    
    Args:
        texts: List of input texts
        
    Returns:
        List of RuleResult objects
    """
    return [classify_with_rules(text) for text in texts]


# Test function
if __name__ == "__main__":
    test_messages = [
        # Pedagogical examples
        "I don't understand the concept",
        "Can you explain more clearly?",
        "Can you give more examples?",
        "Thank you po!",
        "Mas mabilis pa yung pace",
        "I learned a lot from this lesson",
        "What's the formula for this?",
        "I have a question about the topic",
        
        # Nonsensical examples
        "http://spam.com click here",
        "asdfghjkl",
        "OK",
        "hello",
        "",
        "😀👍🎉",
        
        # Unclear - needs BERT
        "interesting",
        "okay then",
        "hmm",
    ]
    
    print("=" * 70)
    print("Rule-Based Filter Test Results")
    print("=" * 70)
    
    for msg in test_messages:
        result = classify_with_rules(msg)
        print(f"Input:    '{msg}'")
        print(f"Label:    {result.label}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Reason:   {result.reason}")
        print(f"Clear:    {result.is_clear}")
        print("-" * 70)
