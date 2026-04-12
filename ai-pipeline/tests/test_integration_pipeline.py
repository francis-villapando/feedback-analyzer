import pytest

from pipelines.run_full_pipeline import run_pipeline


def test_pipeline_runs_and_returns_results():
    messages = [
        "I don't understand this concept",
        "Too fast, please slow down",
        "Can you give more examples?",
    ]

    results = run_pipeline(messages, return_only_pedagogical=False)

    assert isinstance(results, list)
    assert len(results) == len(messages)

    # Check that classification field exists and is boolean-like
    for r in results:
        assert hasattr(r, "is_pedagogical")
        assert hasattr(r, "classification_confidence")
        assert hasattr(r, "primary_strategy")

    # At least one message should be marked pedagogical by the stub
    assert any(r.is_pedagogical for r in results)
