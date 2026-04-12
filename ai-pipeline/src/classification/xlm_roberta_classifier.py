"""
Local Classification Module (XLM-RoBERTa based)

This module handles pedagogical relevance classification. 
Currently using heuristic-based logic as a placeholder for the fine-tuned XLM-RoBERTa model.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ClassificationResult:
    label: str
    confidence: float
    model_used: str = "local_heuristic"

class ClassificationLabel:
    PEDAGOGICAL = "pedagogical"
    NONSENSICAL = "nonsensical"

def classify(text: str) -> ClassificationResult:
    """
    Classify feedback as pedagogical or nonsensical.
    
    Heuristic:
    - Pedagogical if length > 20 or contains a question mark.
    """
    if not text or not text.strip():
        return ClassificationResult(label=ClassificationLabel.NONSENSICAL, confidence=1.0)
    
    # Simple heuristic logic migrated from mcp_client.py
    is_pedagogical = len(text) > 20 or "?" in text
    
    label = ClassificationLabel.PEDAGOGICAL if is_pedagogical else ClassificationLabel.NONSENSICAL
    confidence = 0.85 if is_pedagogical else 0.2
    
    return ClassificationResult(label=label, confidence=confidence)

def classify_batch(texts: List[str]) -> List[ClassificationResult]:
    return [classify(t) for t in texts]
