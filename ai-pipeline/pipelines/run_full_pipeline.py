"""
Full Pipeline Orchestration

This module orchestrates the complete AI pipeline:
1. Stage 1: Preprocessing - Clean and prepare text
2. Stage 2: Classification - Classify as pedagogical/nonsensical
3. Stage 3: Topic Modeling - Identify themes (BERTopic)
4. Stage 4: Problem Detection - Detect learning problems (RoBERTa)
5. Stage 5: Strategy Mapping - Map problems to teaching strategies

The pipeline processes feedback messages and produces structured output
with classifications, topics, problems, and recommended strategies.

Usage:
    from pipelines.run_full_pipeline import run_pipeline
    
    results = run_pipeline(messages)
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pipeline result dataclass
@dataclass
class PipelineResult:
    """Complete result from the full pipeline."""
    # Stage 1: Original and cleaned text
    original_text: str
    cleaned_text: str
    tokens: List[str] = field(default_factory=list)
    
    # Stage 2: Classification
    is_pedagogical: bool = False
    classification_confidence: float = 0.0
    classification_method: str = ""
    
    # Stage 3: Topic modeling
    topic_id: int = -1
    topic_label: str = ""
    topic_probability: float = 0.0
    
    # Stage 4: Problem detection
    problem: str = ""
    problem_confidence: float = 0.0
    
    # Stage 5: Strategy mapping
    primary_strategy: str = ""
    all_strategies: List[str] = field(default_factory=list)
    
    # Metadata
    processing_time_ms: float = 0.0
    stage_errors: List[str] = field(default_factory=list)


@dataclass
class PipelineSummary:
    """Summary statistics from pipeline execution."""
    total_messages: int = 0
    pedagogical_count: int = 0
    nonsensical_count: int = 0
    unique_topics: int = 0
    unique_problems: int = 0
    processing_time_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)


# Import pipeline stages
from src.preprocessing import preprocess
from src.classification import classify_single, ClassificationLabel
from src.topic_modeling import assign_topics, get_topic_info
from src.problem_detection import detect_problem
from src.strategy_mapping import get_recommended_strategy


# Global topic model state (for incremental processing)
_topic_model_ready = False
_processed_topics = {}


def initialize_topic_model():
    """
    Initialize the topic model for the pipeline.
    
    This is called once at the start of processing.
    """
    global _topic_model_ready, _processed_topics
    
    try:
        # Import here to avoid loading model unnecessarily
        from src.topic_modeling import load_model
        logger.info("Initializing topic model...")
        load_model()
        _topic_model_ready = True
        logger.info("Topic model initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize topic model: {e}")
        _topic_model_ready = False


def process_single_message(
    text: str,
    skip_topics: bool = False
) -> PipelineResult:
    """
    Process a single message through the full pipeline.
    
    Args:
        text: Input message text
        skip_topics: Skip topic modeling (for single messages)
        
    Returns:
        PipelineResult with all analysis results
    """
    import time
    start_time = time.time()
    
    result = PipelineResult(original_text=text, cleaned_text=text)
    errors = []
    
    # Stage 1: Preprocessing
    try:
        preprocess_result = preprocess(text)
        result.cleaned_text = preprocess_result.get("cleaned_text", text)
        result.tokens = preprocess_result.get("tokens", [])
    except Exception as e:
        errors.append(f"Preprocessing error: {e}")
        result.cleaned_text = text
        result.stage_errors.append(f"Stage 1 (Preprocessing): {e}")
    
    # Stage 2: Classification
    try:
        classification = classify_single(result.cleaned_text)
        result.is_pedagogical = classification.label == ClassificationLabel.PEDAGOGICAL
        result.classification_confidence = classification.confidence
        result.classification_method = classification.model_used
    except Exception as e:
        errors.append(f"Classification error: {e}")
        result.stage_errors.append(f"Stage 2 (Classification): {e}")
    
    # Only continue if pedagogical
    if not result.is_pedagogical:
        result.processing_time_ms = (time.time() - start_time) * 1000
        return result
    
    # Stage 3: Topic Modeling (only for pedagogical content)
    if not skip_topics and _topic_model_ready:
        try:
            topic_results = assign_topics([result.cleaned_text])
            if topic_results:
                result.topic_id = topic_results[0].topic_id
                result.topic_label = topic_results[0].topic_label
                result.topic_probability = topic_results[0].topic_probability
        except Exception as e:
            errors.append(f"Topic modeling error: {e}")
            result.stage_errors.append(f"Stage 3 (Topic Modeling): {e}")
    
    # Stage 4: Problem Detection (only for pedagogical content)
    try:
        problem_result = detect_problem(result.cleaned_text)
        result.problem = problem_result.problem
        result.problem_confidence = problem_result.confidence
    except Exception as e:
        errors.append(f"Problem detection error: {e}")
        result.stage_errors.append(f"Stage 4 (Problem Detection): {e}")
    
    # Stage 5: Strategy Mapping
    if result.problem:
        try:
            # Use RoBERTa to get the recommended strategy
            strategy_result = get_recommended_strategy(result.problem, result.cleaned_text)
            result.all_strategies = [strategy_result.strategy]  # Single strategy as list
            result.primary_strategy = strategy_result.strategy
        except Exception as e:
            errors.append(f"Strategy mapping error: {e}")
            result.stage_errors.append(f"Stage 5 (Strategy Mapping): {e}")
    
    result.processing_time_ms = (time.time() - start_time) * 1000
    return result


def run_pipeline(
    messages: List[str],
    return_only_pedagogical: bool = True,
    min_classification_confidence: float = 0.3
) -> List[PipelineResult]:
    """
    Run the full pipeline on a list of messages.
    
    Args:
        messages: List of input messages
        return_only_pedagogical: If True, return only pedagogical results
        min_classification_confidence: Minimum confidence for classification
        
    Returns:
        List of PipelineResult objects
    """
    import time
    start_time = time.time()
    
    # Validate confidence threshold
    if not 0.0 <= min_classification_confidence <= 1.0:
        raise ValueError("min_classification_confidence must be between 0.0 and 1.0")
    
    logger.info(f"Starting pipeline processing for {len(messages)} messages")
    
    # Initialize topic model
    initialize_topic_model()
    
    results = []
    
    for i, message in enumerate(messages):
        if (i + 1) % 10 == 0:
            logger.info(f"Processing message {i + 1}/{len(messages)}")
        
        result = process_single_message(message)
        
        # Filter by pedagogical if requested
        if return_only_pedagogical:
            if result.is_pedagogical and result.classification_confidence >= min_classification_confidence:
                results.append(result)
        else:
            results.append(result)
    
    total_time = time.time() - start_time
    logger.info(f"Pipeline completed in {total_time:.2f} seconds")
    logger.info(f"Processed {len(results)} results")
    
    return results


def get_pipeline_summary(results: List[PipelineResult]) -> PipelineSummary:
    """
    Get summary statistics from pipeline results.
    
    Args:
        results: List of PipelineResult objects
        
    Returns:
        PipelineSummary with statistics
    """
    summary = PipelineSummary(total_messages=len(results))
    
    # Count classifications
    pedagogical_count = sum(1 for r in results if r.is_pedagogical)
    summary.pedagogical_count = pedagogical_count
    summary.nonsensical_count = len(results) - pedagogical_count
    
    # Count unique topics
    topics = set(r.topic_id for r in results if r.topic_id != -1)
    summary.unique_topics = len(topics)
    
    # Count unique problems
    problems = set(r.problem for r in results if r.problem)
    summary.unique_problems = len(problems)
    
    # Collect errors
    all_errors = []
    for result in results:
        all_errors.extend(result.stage_errors)
    summary.errors = list(set(all_errors))
    
    return summary


def export_results_to_json(
    results: List[PipelineResult],
    filepath: str
) -> None:
    """
    Export pipeline results to JSON file.
    
    Args:
        results: List of PipelineResult objects
        filepath: Path to output JSON file
    """
    # Convert dataclasses to dicts
    results_dict = []
    for result in results:
        results_dict.append({
            "original_text": result.original_text,
            "cleaned_text": result.cleaned_text,
            "tokens": result.tokens,
            "is_pedagogical": result.is_pedagogical,
            "classification_confidence": result.classification_confidence,
            "classification_method": result.classification_method,
            "topic_id": result.topic_id,
            "topic_label": result.topic_label,
            "topic_probability": result.topic_probability,
            "problem": result.problem,
            "problem_confidence": result.problem_confidence,
            "primary_strategy": result.primary_strategy,
            "all_strategies": result.all_strategies,
            "processing_time_ms": result.processing_time_ms,
            "stage_errors": result.stage_errors,
        })
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results exported to {filepath}")


# Test function
if __name__ == "__main__":
    # Sample messages for testing
    test_messages = [
        # Pedagogical
        "I don't understand this concept",
        "Can you explain more clearly?",
        "Can you give more examples?",
        "Thank you po for the lesson!",
        "Too fast, please slow down",
        "What formula should I use?",
        
        # Nonsensical
        "http://spam.com click here",
        "OK",
        "hello",
        
        # Mixed
        "The explanation was helpful",
        "Need more practice problems",
    ]
    
    print("=" * 70)
    print("Full Pipeline Test")
    print("=" * 70)
    print()
    
    # Run pipeline
    results = run_pipeline(test_messages, return_only_pedagogical=False)
    
    # Print results
    for result in results:
        print(f"Original: {result.original_text}")
        print(f"Cleaned:  {result.cleaned_text}")
        print(f"Pedagogical: {result.is_pedagogical} (confidence: {result.classification_confidence:.2f})")
        
        if result.is_pedagogical:
            print(f"Topic: {result.topic_label} (ID: {result.topic_id})")
            print(f"Problem: {result.problem} (confidence: {result.problem_confidence:.2f})")
            print(f"Strategy: {result.primary_strategy}")
        
        if result.stage_errors:
            print(f"Errors: {result.stage_errors}")
        
        print(f"Processing time: {result.processing_time_ms:.1f}ms")
        print("-" * 70)
    
    # Summary
    summary = get_pipeline_summary(results)
    print()
    print("Summary:")
    print(f"  Total messages: {summary.total_messages}")
    print(f"  Pedagogical: {summary.pedagogical_count}")
    print(f"  Nonsensical: {summary.nonsensical_count}")
    print(f"  Unique topics: {summary.unique_topics}")
    print(f"  Unique problems: {summary.unique_problems}")
    
    print()
    print("Pipeline test completed!")
