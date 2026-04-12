"""Thin MCP-backed strategy mapper preserving previous API."""
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

from src import mcp_client


@dataclass
class StrategyResult:
    problem: Optional[str]
    strategy: str
    confidence: float = 0.0
    model_used: str = "mcp"


@dataclass
class FullMappingResult:
    text: str
    problem: str
    problem_confidence: float
    strategy: str
    strategy_confidence: float


def load_classifier(*args, **kwargs):
    return None


def get_recommended_strategy(problem: str, context: str = "") -> StrategyResult:
    res = mcp_client.get_strategy(None, problem, context)
    return StrategyResult(problem=problem, strategy=getattr(res, "strategy", ""), confidence=0.0, model_used=getattr(res, "reason", "mcp"))


def get_primary_strategy(problem: str) -> str:
    return get_recommended_strategy(problem).strategy


def map_problem_to_strategy(problem: str, context: str = "") -> StrategyResult:
    return get_recommended_strategy(problem, context)


def map_problems_to_strategies(problems: List[Tuple[str, float]], contexts: Optional[List[str]] = None) -> List[StrategyResult]:
    results = []
    for i, (problem, _) in enumerate(problems):
        ctx = contexts[i] if contexts and i < len(contexts) else ""
        results.append(get_recommended_strategy(problem, ctx))
    return results


def create_full_mapping(texts: List[str], problems: List[str], confidences: Optional[List[float]] = None) -> List[FullMappingResult]:
    if confidences is None:
        confidences = [1.0] * len(texts)
    results = []
    for text, problem, conf in zip(texts, problems, confidences):
        strat = get_recommended_strategy(problem, text)
        results.append(FullMappingResult(text=text, problem=problem, problem_confidence=conf, strategy=strat.strategy, strategy_confidence=strat.confidence))
    return results


def get_strategy_statistics(strategies: List[str]) -> Dict:
    total = len(strategies)
    if total == 0:
        return {"total": 0}
    counts = {}
    for s in strategies:
        counts[s] = counts.get(s, 0) + 1
    return {"total": total, "unique_strategies": len(counts), "strategy_counts": counts}
