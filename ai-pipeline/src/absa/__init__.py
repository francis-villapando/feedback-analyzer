"""
Local ABSA Module (Aspect-Based Sentiment Analysis)

Extracts aspect, issue, and polarity from pedagogical feedback.
Using zero-shot classification prototype.
"""

from dataclasses import dataclass
from typing import Optional
import logging
from src.classification.xlm_roberta_classifier import get_classifier

logger = logging.getLogger(__name__)

@dataclass
class ProblemResult:
    aspect: Optional[str]
    issue: Optional[str]
    polarity: Optional[str]
    confidence: float = 0.0

def extract_absa(text: str) -> ProblemResult:
    """
    Extract aspect, issue, and polarity using zero-shot classification.
    """
    try:
        classifier = get_classifier()
        
        # Use mDeBERTa zero-shot for prototype
        model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
        
        # Stage B: Polarity Verification
        polarity_labels = ["student expressing difficulty or negative feedback", "student giving praise or positive feedback"]
        pol_result = classifier(text, polarity_labels)
        top_pol = pol_result['labels'][0]
        polarity = "negative" if "negative feedback" in top_pol else "positive"
        
        if polarity != "negative":
            return ProblemResult(aspect=None, issue=None, polarity=polarity, confidence=pol_result['scores'][0])

        # Stage A: Aspect Identification
        aspect_labels = [
            "instructional pacing and speed", 
            "content difficulty and logic", 
            "clarity of examples and slides", 
            "technical connection and audio", 
            "social conversation"
        ]
        asp_result = classifier(text, aspect_labels)
        aspect = asp_result['labels'][0]
        
        # Stage C: Issue Identification
        issue_map = {
            "instructional pacing and speed": ["too fast", "too slow"],
            "clarity of examples and slides": ["unclear example", "need more examples"],
            "content difficulty and logic": ["not understand", "too complex"],
            "technical connection and audio": ["audio problem", "video problem"],
            "social conversation": ["off topic"]
        }
        
        possible_issues = issue_map.get(aspect, [])
        issue = None
        if possible_issues:
            iss_result = classifier(text, possible_issues)
            best_issue = iss_result['labels'][0]
            # map back (e.g. 'too fast' -> 'too_fast')
            issue = best_issue.replace(" ", "_")
            
        return ProblemResult(
            aspect=aspect,
            issue=issue,
            polarity=polarity,
            confidence=asp_result['scores'][0]
        )
    except Exception as e:
        logger.error(f"Zero-shot ABSA failed: {e}")
        # Fallback to current simple heuristic
        text_lower = text.lower()
        if "example" in text_lower or "examples" in text_lower:
            return ProblemResult(aspect="clarity of examples", issue="need_more_examples", polarity="negative", confidence=0.5)
        if "fast" in text_lower or "too fast" in text_lower:
            return ProblemResult(aspect="pace of session", issue="too_fast", polarity="negative", confidence=0.5)
        return ProblemResult(aspect="content difficulty", issue="not_understand", polarity="negative", confidence=0.5)

