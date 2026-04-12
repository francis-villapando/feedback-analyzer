"""
Local Classification Module (XLM-RoBERTa based)

This module handles pedagogical relevance classification. 
Using zero-shot classification as a prototype for the fine-tuned XLM-RoBERTa model.
"""

from dataclasses import dataclass
from typing import List, Optional
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

@dataclass
class ClassificationResult:
    label: str
    confidence: float
    model_used: str = "zero_shot_xlm_roberta"

class ClassificationLabel:
    PEDAGOGICAL = "pedagogical"
    NONSENSICAL = "nonsensical"

# Global pipeline to avoid reloading
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        logger.info("Loading Zero-Shot XLM-RoBERTa classifier (this may take a while)...")
        # MoritzLaurer/mDeBERTa-v3-base-mnli-xnli is a multilingual zero-shot NLI model
        import sys
        
        # Suppress warnings
        import warnings
        warnings.filterwarnings("ignore")
        
        _classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli", device=-1)
    return _classifier

def classify(text: str) -> ClassificationResult:
    """
    Classify feedback as pedagogical or nonsensical using zero-shot.
    """
    if not text or not text.strip():
        return ClassificationResult(label=ClassificationLabel.NONSENSICAL, confidence=1.0)
    
    try:
        classifier = get_classifier()
        labels = ["student having trouble learning", "social conversation"]
        result = classifier(text, labels)
        
        top_label = result['labels'][0]
        top_score = result['scores'][0]
        
        if top_label == "student having trouble learning" and top_score > 0.5:
            label = ClassificationLabel.PEDAGOGICAL
            confidence = top_score
        else:
            label = ClassificationLabel.NONSENSICAL
            confidence = top_score if top_label == "social conversation" else (1.0 - top_score)
            
        return ClassificationResult(label=label, confidence=confidence)
    except Exception as e:
        logger.error(f"Zero-shot classification failed: {e}")
        # Fallback heuristic
        is_pedagogical = len(text) > 20 or "?" in text
        return ClassificationResult(
            label=ClassificationLabel.PEDAGOGICAL if is_pedagogical else ClassificationLabel.NONSENSICAL,
            confidence=0.5,
            model_used="fallback_heuristic"
        )

def classify_batch(texts: List[str]) -> List[ClassificationResult]:
    return [classify(t) for t in texts]

