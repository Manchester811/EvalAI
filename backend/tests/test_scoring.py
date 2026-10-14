import pytest
from app.services.scoring import (
    evaluate_answer, enforce_score_bounds, RubricCriterion,
    EvaluationStatus, EvaluationResult
)
from app.services.mock_evaluation_provider import MockEvaluationProvider

def test_score_within_bounds():
    criteria = [RubricCriterion(id=1, criterion="Accuracy", max_marks=5)]
    result = evaluate_answer("The answer is accurate.", "Reference answer here.", criteria)
    assert 0 <= result.awarded_marks <= result.max_marks
    assert result.max_marks == 5

def test_out_of_range_raises():
    with pytest.raises(ValueError):
        enforce_score_bounds(10, 5)
    with pytest.raises(ValueError):
        enforce_score_bounds(-1, 5)

def test_rationale_present():
    criteria = [RubricCriterion(id=1, criterion="Clarity", max_marks=3)]
    result = evaluate_answer("Clear explanation provided.", "Ref.", criteria)
    assert result.rationale and len(result.rationale) > 0
    assert "Mock evaluation" in result.rationale or "evidence" in result.rationale.lower()

def test_mock_deterministic():
    provider = MockEvaluationProvider()
    criteria = [RubricCriterion(id=1, criterion="A", max_marks=2)]
    r1 = provider.evaluate("A is here.", "ref", criteria)
    r2 = provider.evaluate("A is here.", "ref", criteria)
    assert r1.awarded_marks == r2.awarded_marks
    assert r1.rationale == r2.rationale
    assert r1.confidence == r2.confidence

def test_unrecognized_flagged():
    criteria = [RubricCriterion(id=1, criterion="X", max_marks=2)]
    result = evaluate_answer("x", "ref", criteria)
    assert result.status == EvaluationStatus.UNRECOGNIZED or result.status == EvaluationStatus.UNANSWERED

def test_evidence_linked():
    criteria = [RubricCriterion(id=1, criterion="Method", max_marks=4, guidance="Show work")]
    result = evaluate_answer("Show work done.", "ref", criteria)
    assert len(result.evidence) > 0
    assert result.criterion_scores.get(1) is not None
