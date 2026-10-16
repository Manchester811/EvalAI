"""Tests for corrected scoring — mock only, deterministic, never pretends semantic grading."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.scoring import (
    evaluate_answer, enforce_score_bounds, EvaluationStatus, RubricCriterion
)
import math


def make_criteria():
    return [
        RubricCriterion(id=1, criterion="Definition accuracy", max_marks=5, guidance="Correct terminology"),
        RubricCriterion(id=2, criterion="Example quality", max_marks=5, guidance="Relevant examples"),
    ]


def test_blank_answer():
    result = evaluate_answer("", "ref", make_criteria())
    assert result.status == EvaluationStatus.UNANSWERED
    assert result.awarded_marks == 0.0
    assert result.is_mock is True
    assert result.requires_review is True
    assert result.flags.get("unanswered") is True


def test_unrecognized_answer():
    result = evaluate_answer("x", "ref", make_criteria())
    assert result.status == EvaluationStatus.UNRECOGNIZED
    assert result.awarded_marks == 0.0


def test_incorrect_answer_low_score():
    # Incorrect reasoning: repeats keywords but no valid explanation
    result = evaluate_answer("correct correct correct wrong reasoning bad", "ref answer", make_criteria())
    assert result.awarded_marks < result.max_marks  # partial, never full
    assert result.status in (EvaluationStatus.PARTIAL, EvaluationStatus.INCORRECT)
    assert result.is_mock is True
    assert result.flags.get("mock_provider") is True or result.flags.get("requires_review") is True


def test_adversarial_keyword_repetition():
    # Repeats keywords but wrong reasoning — must not get full marks
    result = evaluate_answer("definition true correct yes right perfect", "ref answer", make_criteria())
    assert result.awarded_marks < result.max_marks  # never full; reduced by adversarial logic
    assert result.flags.get("keyword_repetition_without_reasoning") is True


def test_partially_correct():
    # Reasonable length, some keyword match
    result = evaluate_answer("The algorithm uses recursion and has O(n) time complexity with examples.", "ref answer", make_criteria())
    assert 0 < result.awarded_marks <= 10.0
    assert result.status in (EvaluationStatus.PARTIAL, EvaluationStatus.ANSWERED)


def test_correct_answer_still_mock_not_full():
    # Even correct answer must NOT get max — mock policy
    result = evaluate_answer("A complete and correct explanation with accurate definition and examples.", "ref answer", make_criteria())
    assert result.awarded_marks < 10.0  # mock never awards full
    assert result.is_mock is True
    assert result.confidence < 0.5


def test_provider_failure_no_silent_full():
    # If provider raises / returns bad output, system must not award full
    # Verify enforce_score_bounds raises for bad values
    with pytest.raises(ValueError):
        enforce_score_bounds(100.0, 10.0)  # over max
    with pytest.raises(ValueError):
        enforce_score_bounds(float('inf'), 10.0)  # non-finite
    with pytest.raises(ValueError):
        enforce_score_bounds(float('nan'), 10.0)


def test_empty_rubric_rejected():
    with pytest.raises(ValueError, match="Rubric criteria are empty"):
        evaluate_answer("some answer", "ref", [])


def test_negative_max_marks_rejected():
    bad = [RubricCriterion(id=1, criterion="X", max_marks=-5)]
    with pytest.raises(ValueError, match="invalid max_marks"):
        evaluate_answer("test", "ref", bad)


def test_score_bounds_for_correct_criteria():
    # Normal case passes bounds
    result = evaluate_answer("test answer", "ref", make_criteria())
    assert result.awarded_marks >= 0.0
    assert result.awarded_marks <= result.max_marks + 1e-6
    assert math.isfinite(result.awarded_marks)
    assert math.isfinite(result.max_marks)


def test_rationale_contains_mock_label():
    result = evaluate_answer("test", "ref", make_criteria())
    assert "MOCK" in result.rationale
    assert "not an AI grade" in result.rationale.lower() or "MOCK" in result.rationale
