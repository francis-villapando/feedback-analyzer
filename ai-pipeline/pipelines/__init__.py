"""
Pipeline Module

This module provides pipeline orchestration:
- run_full_pipeline(): Run complete pipeline on messages

Pipeline Stages:
1. Preprocessing - Clean and prepare text
2. Classification - Pedagogical vs Nonsensical
3. Topic Modeling - BERTopic theme identification
4. Problem Detection - RoBERTa problem detection
5. Strategy Mapping - Map problems to teaching strategies
"""

from .run_full_pipeline import (
    PipelineResult,
    PipelineSummary,
    run_pipeline,
    get_pipeline_summary,
    export_results_to_json,
    initialize_topic_model,
)


__version__ = "1.0.0"
