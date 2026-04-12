"""
Pipeline Module

This module provides pipeline orchestration:
- run_full_pipeline(): Run complete pipeline on messages

Pipeline Stages (MCP-backed):
1. Preprocessing - Clean and prepare text
2. Classification - Pedagogical vs Nonsensical (MCP)
3. Topic Modeling - Deprecated (moved to MCP/ABSA or external service)
4. Problem Detection - ABSA (aspect/issue/polarity) via MCP
5. Strategy Mapping - Map problems to teaching strategies (MCP-backed)
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
