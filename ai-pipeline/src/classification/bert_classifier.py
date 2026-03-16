"""
BERT Classifier Module

This module provides hybrid classification for feedback messages:
1. First applies rule-based filter for obvious patterns
2. If unclear, uses RoBERTa zero-shot classification

Classification categories:
- pedagogical: Feedback related to learning/teaching
- nonsensical: Spam, random text, or meaningless content

Note: This implementation uses ZERO-SHOT classification for Phase 1.
Accuracy improvements will come in Phase 2 with fine-tuning.
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Import configuration
try:
    from config.settings import BERT_CONFIG
except ImportError:
    # Fallback if config not available
    BERT_CONFIG = {
        "model_name": "roberta-base",
        "max_length": 128,
        "batch_size": 16,
        "use_rule_based_first": True,
    }

# Import rule-based filter
from .rule_based_filter import (
    ClassificationLabel,
    RuleResult,
    classify_with_rules,
    PEDAGOGICAL_PATTERNS,
    NONSENSICAL_PATTERNS,
)


# Classification result dataclass
@dataclass
class ClassificationResult:
    """Result from BERT classification."""
    text: str
    label: str  # "pedagogical" or "nonsensical"
    confidence: float  # 0.0 to 1.0
    rule_based_used: bool
    rule_result: Optional[RuleResult]
    model_used: str


# Global classifier instance (lazy loading)
_classifier = None


def load_classifier():
    """
    Load the zero-shot classification pipeline.
    
    Uses Hugging Face transformers zero-shot-classification pipeline.
    This is a lazy loader - model is only loaded when first needed.
    
    Returns:
        transformers pipeline for zero-shot classification
    """
    global _classifier
    
    if _classifier is not None:
        return _classifier
    
    try:
        from transformers import pipeline
        import torch
        
        # Check for GPU
        device = 0 if torch.cuda.is_available() else -1
        device_str = "GPU" if device == 0 else "CPU"
        print(f"Loading RoBERTa classifier on {device_str}...")
        
        # Create zero-shot classification pipeline using RoBERTa
        # RoBERTa provides strong zero-shot classification performance
        _classifier = pipeline(
            "zero-shot-classification",
            model="roberta-base",
            device=device,
        )
        
        print("RoBERTa classifier loaded successfully!")
        return _classifier
        
    except ImportError as e:
        raise ImportError(
            "transformers library not installed. "
            "Run: pip install transformers"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Failed to load BERT classifier: {e}"
        ) from e


def get_candidate_labels() -> List[str]:
    """
    Get the candidate labels for classification.
    
    Returns:
        List of classification labels
    """
    return ["pedagogical", "nonsensical"]


def classify_with_roberta(text: str) -> Tuple[str, float]:
    """
    Classify text using RoBERTa zero-shot classification.
    
    Args:
        text: Input text to classify
        
    Returns:
        Tuple of (label, confidence)
    """
    classifier = load_classifier()
    
    candidate_labels = get_candidate_labels()
    
    # Hypothesis template for better zero-shot performance
    hypothesis_template = "This is {} feedback about learning from a student."
    
    try:
        result = classifier(
            text,
            candidate_labels=candidate_labels,
            hypothesis_template=hypothesis_template,
            multi_label=False,
            max_length=BERT_CONFIG.get("max_length", 128),
        )
        
        # Return the top prediction
        return result["labels"][0], result["scores"][0]
        
    except Exception as e:
        print(f"Warning: BERT classification failed: {e}")
        # Fallback to nonsensical if BERT fails
        return ClassificationLabel.NONSENSICAL, 0.0


def classify_single(
    text: str,
    use_rule_based_first: bool = True,
    rule_confidence_threshold: float = 0.6
) -> ClassificationResult:
    """
    Classify a single text using hybrid approach.
    
    Pipeline:
    1. If use_rule_based_first: Apply rules first
       - If clear match (confidence >= threshold): return immediately
       - If unclear: proceed to BERT
    2. Use BERT zero-shot classification
    3. Return combined result
    
    Args:
        text: Input text to classify
        use_rule_based_first: Whether to apply rules before BERT
        rule_confidence_threshold: Minimum confidence to accept rule-based result
        
    Returns:
        ClassificationResult with label, confidence, and metadata
    """
    if not text or not text.strip():
        return ClassificationResult(
            text=text,
            label=ClassificationLabel.NONSENSICAL,
            confidence=1.0,
            rule_based_used=True,
            rule_result=RuleResult(
                label=ClassificationLabel.NONSENSICAL,
                confidence=1.0,
                reason="empty input",
                is_clear=True
            ),
            model_used="rule_based"
        )
    
    # Validate confidence threshold
    if not 0.0 <= rule_confidence_threshold <= 1.0:
        raise ValueError("rule_confidence_threshold must be between 0.0 and 1.0")
    
    # Step 1: Apply rule-based filter
    if use_rule_based_first:
        rule_result = classify_with_rules(text)
        
        # If rules are confident enough, return immediately
        if rule_result.is_clear and rule_result.confidence >= rule_confidence_threshold:
            return ClassificationResult(
                text=text,
                label=rule_result.label,
                confidence=rule_result.confidence,
                rule_based_used=True,
                rule_result=rule_result,
                model_used="rule_based"
            )
    
    # Step 2: Use RoBERTa for classification
    label, confidence = classify_with_roberta(text)
    
    return ClassificationResult(
        text=text,
        label=label,
        confidence=confidence,
        rule_based_used=False,
        rule_result=classify_with_rules(text) if use_rule_based_first else None,
        model_used="roberta_zero_shot"
    )


def classify_batch(
    texts: List[str],
    use_rule_based_first: bool = True,
    rule_confidence_threshold: float = 0.6,
    batch_size: int = 16
) -> List[ClassificationResult]:
    """
    Classify a batch of texts.
    
    Args:
        texts: List of input texts
        use_rule_based_first: Whether to apply rules before BERT
        rule_confidence_threshold: Minimum confidence for rule-based result
        batch_size: Number of texts to process at once (for BERT)
        
    Returns:
        List of ClassificationResult objects
    """
    results = []
    
    # Process texts
    for text in texts:
        result = classify_single(
            text,
            use_rule_based_first=use_rule_based_first,
            rule_confidence_threshold=rule_confidence_threshold
        )
        results.append(result)
    
    return results


def filter_pedagogical(
    texts: List[str],
    min_confidence: float = 0.5
) -> Tuple[List[str], List[ClassificationResult]]:
    """
    Filter texts to only return pedagogical ones.
    
    This is a convenience function for getting only the learning-related
    feedback from a list of messages.
    
    Args:
        texts: List of input texts
        min_confidence: Minimum confidence threshold for inclusion
        
    Returns:
        Tuple of (pedagogical_texts, all_results)
    """
    results = classify_batch(texts)
    
    pedagogical = []
    for result in results:
        if result.label == ClassificationLabel.PEDAGOGICAL and result.confidence >= min_confidence:
            pedagogical.append(result.text)
    
    return pedagogical, results


def get_statistics(results: List[ClassificationResult]) -> Dict:
    """
    Get statistics from classification results.
    
    Args:
        results: List of ClassificationResult objects
        
    Returns:
        Dictionary with statistics
    """
    total = len(results)
    if total == 0:
        return {"total": 0}
    
    pedagogical_count = sum(1 for r in results if r.label == ClassificationLabel.PEDAGOGICAL)
    nonsensical_count = sum(1 for r in results if r.label == ClassificationLabel.NONSENSICAL)
    
    rule_based_count = sum(1 for r in results if r.rule_based_used)
    bert_count = total - rule_based_count
    
    avg_confidence = sum(r.confidence for r in results) / total
    
    return {
        "total": total,
        "pedagogical": pedagogical_count,
        "nonsensical": nonsensical_count,
        "rule_based_used": rule_based_count,
        "bert_used": bert_count,
        "average_confidence": avg_confidence,
        "pedagogical_percentage": (pedagogical_count / total) * 100,
        "nonsensical_percentage": (nonsensical_count / total) * 100,
    }


# Test function
if __name__ == "__main__":
    test_messages = [
        # Should be pedagogical
        "I don't understand the concept",
        "Can you explain more clearly?",
        "Can you give more examples?",
        "Thank you po for the lesson!",
        "Mas mabilis pa yung pace ng teaching",
        "What's the formula for this equation?",
        "I have a question about the topic",
        "The explanation was very helpful",
        
        # Should be nonsensical
        "http://spam.com click here now",
        "asdfghjkl qwerty",
        "OK",
        "",
        "😀👍🎉",
        "hello world",
        
        # Unclear - BERT will decide
        "interesting",
        "hmm",
        "that's cool",
    ]
    
    print("=" * 70)
    print("BERT Classifier Test Results")
    print("=" * 70)
    print("(Using zero-shot classification - Phase 1)")
    print()
    
    results = classify_batch(test_messages)
    
    for result in results:
        print(f"Text:     '{result.text}'")
        print(f"Label:    {result.label}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Model:    {result.model_used}")
        if result.rule_result:
            print(f"Rule reason: {result.rule_result.reason}")
        print("-" * 70)
    
    # Print statistics
    stats = get_statistics(results)
    print()
    print("=" * 70)
    print("Statistics")
    print("=" * 70)
    print(f"Total messages: {stats['total']}")
    print(f"Pedagogical: {stats['pedagogical']} ({stats['pedagogical_percentage']:.1f}%)")
    print(f"Nonsensical: {stats['nonsensical']} ({stats['nonsensical_percentage']:.1f}%)")
    print(f"Rule-based used: {stats['rule_based_used']}")
    print(f"BERT used: {stats['bert_used']}")
    print(f"Average confidence: {stats['average_confidence']:.3f}")
