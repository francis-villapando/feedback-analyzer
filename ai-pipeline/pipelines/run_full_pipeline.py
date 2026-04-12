"""
Full Pipeline Orchestration

This module orchestrates the complete AI pipeline using MCP-backed services:
1. Stage 1: Preprocessing - Clean and prepare text
2. Stage 2: Classification - Pedagogical vs Nonsensical (delegated to MCP)
3. Stage 3: Topic Modeling - Deprecated locally; optional external/MCP ABSA
4. Stage 4: Problem Detection - ABSA (aspect/issue/polarity) via MCP
5. Stage 5: Strategy Mapping - Map problems to teaching strategies (MCP)

The pipeline processes feedback messages and produces structured output
with classifications, ABSA fields, and recommended strategies. Local heavy
model implementations (BERTopic, local RoBERTa/BERT) were replaced by thin
MCP client wrappers; this file documents the updated stages for clarity.

Usage:
    from pipelines.run_full_pipeline import run_pipeline
    
    results = run_pipeline(messages)
"""

# Ensure `src` package can be imported when running this script from the repository root.
# Adds the ai-pipeline directory to sys.path so `import src...` resolves reliably.
import os
import sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
# ai-pipeline root (one level up from pipelines/)
_PROJECT_ROOT = os.path.abspath(os.path.join(_THIS_DIR, ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


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
    
    # Stage 4: Problem detection (ABSA)
    aspect: Optional[str] = None
    problem: str = ""
    polarity: Optional[str] = None
    problem_confidence: float = 0.0
    
    # Stage 5: Cognitive Mapping
    rbt_level: str = ""
    clt_type: str = ""

    # Stage 6: Strategy mapping (CBR)
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
from src.cognitive import get_cognitive_mapping

# Local logic modules
from src.classification import classify
from src.absa import extract_absa
from src.cbr import get_strategy


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
    text: str
) -> Optional[PipelineResult]:
    """
    Process a single message through the full pipeline.
    
    Sequential Logic:
    1. Preprocessing
    2. Classification (Pedagogical vs Nonsensical) -> Discard if False
    3. ABSA (Aspect, Issue, Polarity)
    4. Polarity Filter -> Discard if NOT Negative
    5. Cognitive Mapping (RBT, CLT)
    6. Strategy Mapping (CBR)
    
    Returns:
        PipelineResult with analysis status.
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
        classification = classify(result.cleaned_text)
        result.is_pedagogical = True if classification.label == "pedagogical" else False
        result.classification_confidence = float(classification.confidence or 0.0)
        result.classification_method = getattr(classification, "model_used", "local")
    except Exception as e:
        errors.append(f"Classification error: {e}")
        result.stage_errors.append(f"Stage 2 (Classification): {e}")
    
    # Step 1: Discard if not pedagogical
    if not result.is_pedagogical:
        return result
    
    # Stage 4: Problem Detection (ABSA)
    try:
        problem_result = extract_absa(result.cleaned_text)
        result.aspect = getattr(problem_result, "aspect", None)
        result.polarity = getattr(problem_result, "polarity", "neutral")
        result.problem = getattr(problem_result, "issue", None) or (result.aspect or "")
        result.problem_confidence = float(getattr(problem_result, "confidence", 0.0) or 0.0)
    except Exception as e:
        errors.append(f"Problem detection error: {e}")
        result.stage_errors.append(f"Stage 4 (Problem Detection): {e}")
    
    # Step 2: Discard if NOT negative (Rule: Only negative feedback indicates a need for enhancement)
    if result.polarity != "negative":
        return result
    
    # Stage 5: Cognitive Mapping (RBT + CLT)
    try:
        rbt, clt = get_cognitive_mapping(result.problem, result.aspect)
        result.rbt_level = rbt
        result.clt_type = clt
    except Exception as e:
        errors.append(f"Cognitive mapping error: {e}")
        result.stage_errors.append(f"Stage 5 (Cognitive Mapping): {e}")

    # Stage 6: Strategy Mapping (CBR)
    if result.problem:
        try:
            strategy_result = get_strategy(result.aspect, result.problem, result.cleaned_text)
            result.all_strategies = [strategy_result.strategy] if strategy_result and strategy_result.strategy else []
            result.primary_strategy = strategy_result.strategy if strategy_result and strategy_result.strategy else ""
        except Exception as e:
            errors.append(f"Strategy mapping error: {e}")
            result.stage_errors.append(f"Stage 6 (Strategy Mapping): {e}")
    
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
        
        result = process_single_message(message)
        
        # Only add valid results (pedagogical and negative) to results list
        if result.is_pedagogical and result.polarity == "negative":
            if return_only_pedagogical:
                if result.classification_confidence >= min_classification_confidence:
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
            "aspect": result.aspect,
            "problem": result.problem,
            "problem_confidence": result.problem_confidence,
            "rbt_level": result.rbt_level,
            "clt_type": result.clt_type,
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
    # Sample messages for testing (using clean English to demonstrate baseline NLI capabilities)
    test_messages = [
        "It is too fast sir",
        "The clarity of examples is bad",
        "Hello classmates!",
        "Your slides are beautiful",
        "I do not understand the logic"
    ]
    
    print("=" * 70)
    print("Full Pipeline Test")
    print("=" * 70)
    print()
    
    # Run pipeline and print individually
    for message in test_messages:
        result = process_single_message(message)
        
        print(f"original: {result.original_text}")
        print(f"cleaned: {result.cleaned_text}")
        
        cls_binary = 1 if result.is_pedagogical else 0
        print(f"class: {cls_binary} ({result.classification_confidence:.2f})")
        
        if not result.is_pedagogical:
            print("!!! not pedagogical feedback")
        elif result.polarity != "negative":
            print(f"!!! not negative feedback")
        else:
            print(f"aspect: {result.aspect}")
            print(f"issue: {result.problem}, ({result.rbt_level}, {result.clt_type})")
            print(f"strat: {result.primary_strategy}")
            
        print("-" * 70)
    
    print()
    print("Pipeline test completed!")
