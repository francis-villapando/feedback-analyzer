"""
Strategy Mapping Module

This module provides strategy mapping functionality:
- Maps detected problems to specific teaching strategies
- Strategies are specific and actionable

Problem -> Strategy mappings are predefined in configuration.

Main Functions:
- get_strategies_for_problem(): Get strategies for a problem
- get_primary_strategy(): Get the best strategy
- map_problem_to_strategy(): Map single problem
- map_problems_to_strategies(): Map multiple problems
- create_full_mapping(): Full text->problem->strategy mapping
"""

from .roberta_mapper import (
    StrategyResult,
    FullMappingResult,
    get_strategy_mappings,
    get_strategies_for_problem,
    get_primary_strategy,
    get_all_strategies,
    map_problem_to_strategy,
    map_problems_to_strategies,
    create_full_mapping,
    get_strategy_statistics,
)


__version__ = "1.0.0"
