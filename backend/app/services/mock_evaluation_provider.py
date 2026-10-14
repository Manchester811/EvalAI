"""Local deterministic evaluation provider."""

from typing import Any, Mapping, Sequence

from .scoring import EvaluationResult, RubricCriterion, evaluate_answer


class MockEvaluationProvider:
    """Adapter kept for callers that select the ``mock`` provider."""

    def evaluate(
        self,
        answer_text: str | None,
        reference_answer: str | Sequence[RubricCriterion | Mapping[str, Any]] | None = None,
        rubric_criteria: Sequence[RubricCriterion | Mapping[str, Any]] | None = None,
    ) -> EvaluationResult:
        # Preserve compatibility with the original two-argument provider API:
        # evaluate(answer_text, criteria).
        if rubric_criteria is None and isinstance(reference_answer, Sequence) and not isinstance(reference_answer, str):
            rubric_criteria = reference_answer
            reference_answer = None
        return evaluate_answer(answer_text, reference_answer if isinstance(reference_answer, str) else "", rubric_criteria or [])
