"""Mock evaluation provider — clearly labelled, never claims accuracy."""
from typing import Any, Mapping, Sequence
from .scoring import EvaluationResult, RubricCriterion, evaluate_answer


class MockEvaluationProvider:
    """Adapter for the mock provider (deterministic tests only).

    Warning: this is NOT a real grading engine. It never assigns full
    marks to arbitrary answers. All outputs must be reviewed by faculty.
    """

    def evaluate(
        self,
        answer_text: str | None,
        reference_answer: str | None = None,
        rubric_criteria: Sequence[RubricCriterion | Mapping[str, Any]] | None = None,
    ) -> EvaluationResult:
        # Preserve compatibility: if second arg is criteria (not reference), swap
        if rubric_criteria is None and isinstance(reference_answer, Sequence) and not isinstance(reference_answer, str):
            rubric_criteria = reference_answer
            reference_answer = None
        result = evaluate_answer(
            answer_text,
            reference_answer if isinstance(reference_answer, str) else None,
            rubric_criteria or [],
        )
        # Explicit label — mock, not trustworthy grading
        result.flags["mock_provider"] = True
        result.flags["requires_review"] = True
        result.is_mock = True
        result.requires_review = True
        result.confidence = min(result.confidence, 0.4)  # never high for mock
        result.rationale = f"MOCK PROVIDER RESULT (not an AI grade): {result.rationale}"
        return result
