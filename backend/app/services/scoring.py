"""Deterministic scoring primitives used by the evaluation pipeline.

The real provider can be swapped in later, but the application still needs a
stable result contract for feedback, API responses, and tests.  Keeping that
contract here prevents each provider from returning a different shape.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class EvaluationStatus(str, Enum):
    ANSWERED = "answered"
    UNANSWERED = "unanswered"
    UNRECOGNIZED = "unrecognized"


@dataclass(frozen=True)
class RubricCriterion:
    id: int
    criterion: str
    max_marks: float
    guidance: str | None = None


@dataclass
class EvaluationResult:
    awarded_marks: float
    max_marks: float
    rationale: str
    confidence: float
    status: EvaluationStatus
    evidence: list[Any] = field(default_factory=list)
    criterion_scores: dict[int, dict[str, Any]] = field(default_factory=dict)
    flags: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation for API and service callers."""
        return {
            "awarded_marks": self.awarded_marks,
            "max_marks": self.max_marks,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "status": self.status.value,
            "evidence": self.evidence,
            "criterion_scores": self.criterion_scores,
            "flags": self.flags,
        }


def enforce_score_bounds(awarded_marks: float, max_marks: float) -> None:
    """Reject scores that cannot be represented by the configured rubric."""
    if max_marks < 0 or awarded_marks < 0 or awarded_marks > max_marks:
        raise ValueError("Score out of bounds")


def _criterion_from_value(value: RubricCriterion | Mapping[str, Any]) -> RubricCriterion:
    if isinstance(value, RubricCriterion):
        return value
    return RubricCriterion(
        id=int(value.get("id", 0)),
        criterion=str(value.get("criterion", "")),
        max_marks=float(value.get("max_marks", 0)),
        guidance=value.get("guidance"),
    )


def evaluate_answer(
    answer_text: str | None,
    reference_answer: str | None,
    rubric_criteria: Sequence[RubricCriterion | Mapping[str, Any]],
) -> EvaluationResult:
    """Evaluate an answer with the deterministic local provider.

    This deliberately does not claim semantic correctness.  It provides a
    predictable baseline until an OCR/LLM provider is configured and marks
    very short or empty input for human review instead of fabricating a score.
    """
    criteria = [_criterion_from_value(item) for item in rubric_criteria]
    max_marks = sum(max(0.0, criterion.max_marks) for criterion in criteria)
    text = (answer_text or "").strip()

    if not text:
        status = EvaluationStatus.UNANSWERED
        confidence = 1.0
        awarded_marks = 0.0
        evidence: list[Any] = []
        flags = {"unanswered": True}
    elif len(text) <= 1:
        status = EvaluationStatus.UNRECOGNIZED
        confidence = 0.3
        awarded_marks = 0.0
        evidence = []
        flags = {"unrecognized": True}
    else:
        status = EvaluationStatus.ANSWERED
        confidence = 0.85
        awarded_marks = max_marks
        evidence = [
            {"criterion_id": criterion.id, "text": text[:500]}
            for criterion in criteria
        ]
        flags = {}

    criterion_scores = {
        criterion.id: {
            "criterion": criterion.criterion,
            "max_marks": criterion.max_marks,
            "awarded_marks": criterion.max_marks if status is EvaluationStatus.ANSWERED else 0.0,
            "evidence": evidence if status is EvaluationStatus.ANSWERED else [],
            "matched": status is EvaluationStatus.ANSWERED,
        }
        for criterion in criteria
    }
    enforce_score_bounds(awarded_marks, max_marks)

    if status is EvaluationStatus.UNANSWERED:
        rationale = "Mock evaluation: no answer was provided; human review is required."
    elif status is EvaluationStatus.UNRECOGNIZED:
        rationale = "Mock evaluation: the answer could not be reliably recognized."
    else:
        rationale = "Mock evaluation: evidence was recorded for each rubric criterion."

    return EvaluationResult(
        awarded_marks=awarded_marks,
        max_marks=max_marks,
        rationale=rationale,
        confidence=confidence,
        status=status,
        evidence=evidence,
        criterion_scores=criterion_scores,
        flags=flags,
    )
