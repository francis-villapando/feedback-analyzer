"""
Strategy Mapping Module

This module provides strategy mapping functionality:
- Maps detected problems to specific teaching strategies
- Uses RoBERTa zero-shot to recommend the best strategy

IMPORTANT: Returns ONE strategy per problem detected.
- If 2 problems detected → 2 strategies
- If 1 problem detected → 1 strategy

Main Functions:
- get_recommended_strategy(): Get best strategy for a problem
- map_problem_to_strategy(): Map single problem to strategy
- map_problems_to_strategies(): Map multiple problems to strategies
- create_full_mapping(): Full text->problem->strategy mapping
"""

from .roberta_mapper import (
    StrategyResult,
    FullMappingResult,
    get_strategy_candidates,
    get_strategies_for_problem,
    get_recommended_strategy,
    get_primary_strategy,
    get_all_strategies,
    map_problem_to_strategy,
    map_problems_to_strategies,
    create_full_mapping,
    get_strategy_statistics,
)


__version__ = "1.0.0"
