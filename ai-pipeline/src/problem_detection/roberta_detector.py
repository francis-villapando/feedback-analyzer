"""Wrapper for problem detection that delegates to MCP client."""
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

from src import mcp_client


@dataclass
class ProblemResult:
    text: str
    problem: Optional[str]
    confidence: float
    all_scores: Dict[str, float]


def load_classifier(*args, **kwargs):
    """No-op compatibility shim; models are hosted externally via MCP."""
    return None


def detect_problem(text: str) -> ProblemResult:
    res = mcp_client.absa(text)
    return ProblemResult(
        text=text,
        problem=getattr(res, "issue", None) or getattr(res, "aspect", None),
        confidence=float(getattr(res, "confidence", 0.0) or 0.0),
        all_scores={},
    )


def detect_problems_batch(texts: List[str]) -> List[ProblemResult]:
    return [detect_problem(t) for t in texts]


def filter_by_problem(texts: List[str], problems: Optional[List[str]] = None, min_confidence: float = 0.3) -> Tuple[List[str], List[ProblemResult]]:
    results = detect_problems_batch(texts)
    filtered = []
    for r in results:
        if problems is not None:
            if r.problem in problems and r.confidence >= min_confidence:
                filtered.append(r.text)
        else:
            if r.confidence >= min_confidence:
                filtered.append(r.text)
    return filtered, results


def get_problem_statistics(results: List[ProblemResult]) -> Dict:
    total = len(results)
    if total == 0:
        return {"total": 0}
    problem_counts = {}
    for r in results:
        key = r.problem or "unknown"
        problem_counts[key] = problem_counts.get(key, 0) + 1
    avg_confidence = sum(r.confidence for r in results) / total
    return {
        "total": total,
        "problem_counts": problem_counts,
        "average_confidence": avg_confidence,
    }
