import pytest
from app.services.feedback import generate_feedback
from app.services.scoring import EvaluationResult, EvaluationStatus, RubricCriterion

def test_groups_exist():
    result = EvaluationResult(
        awarded_marks=5, max_marks=10, rationale="test", confidence=0.8,
        status=EvaluationStatus.ANSWERED, evidence=["found A"], criterion_scores={}
    )
    groups = generate_feedback(result)
    assert 'strengths' in groups
    assert 'improvements' in groups
    assert 'suggestions' in groups

def test_no_fabricated_claims():
    # No evidence -> no fabricated strengths
    result = EvaluationResult(
        awarded_marks=5, max_marks=10, rationale="test", confidence=0.8,
        status=EvaluationStatus.ANSWERED, evidence=[], criterion_scores={}
    )
    groups = generate_feedback(result)
    # Should not claim strengths without evidence
    for s in groups['strengths']:
        assert 'source_evidence' in s
        assert s.get('source_evidence') is not None

def test_uncertain_flagged():
    result = EvaluationResult(
        awarded_marks=5, max_marks=10, rationale="test", confidence=0.3,
        status=EvaluationStatus.ANSWERED, evidence=["something"], criterion_scores={}
    )
    groups = generate_feedback(result)
    # Low confidence should flag uncertain
    uncertain_items = [i for g in groups.values() for i in g if i.get('certainty') == 'uncertain']
    assert len(uncertain_items) > 0

def test_unanswered_flagged():
    result = EvaluationResult(
        awarded_marks=0, max_marks=10, rationale="unanswered", confidence=1.0,
        status=EvaluationStatus.UNANSWERED, evidence=[], criterion_scores={}
    )
    groups = generate_feedback(result)
    improvements = groups['improvements']
    assert any('unanswered' in i['text'].lower() for i in improvements)

def test_improvement_linked_to_rubric():
    from app.services.scoring import RubricCriterion
    result = EvaluationResult(
        awarded_marks=3, max_marks=10, rationale="partial", confidence=0.8,
        status=EvaluationStatus.ANSWERED, evidence=["found criterion"],
        criterion_scores={1: {"criterion": "Accuracy", "max_marks": 10, "evidence": [], "matched": False}}
    )
    groups = generate_feedback(result)
    improvements = groups['improvements']
    assert any('not addressed' in i['text'].lower() or 'improvement' in i['text'].lower() for i in improvements)
