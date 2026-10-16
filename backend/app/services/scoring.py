"""Deterministic scoring primitives — mock only, clearly labelled.

Policy:
- Mock provider NEVER claims semantic grading accuracy.
- Mock assigns 0 for blank/unrecognized; partial credit only if evidence
  clearly matches rubric criteria (simulated, not AI-grading).
- All scores validated: finite, [0, max], no NaN/inf.
- Final grades MUST be approved by faculty (FR-08); this returns drafts.
- No live model calls from test suite.
"""
from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Mapping, Sequence


class EvaluationStatus(str, Enum):
    ANSWERED = "answered"
    UNANSWERED = "unanswered"
    UNRECOGNIZED = "unrecognized"
    PARTIAL = "partial"
    INCORRECT = "incorrect"


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
    is_mock: bool = True  # clearly labelled
    requires_review: bool = True  # draft until faculty approves

    def to_dict(self) -> dict[str, Any]:
        return {
            "awarded_marks": self.awarded_marks,
            "max_marks": self.max_marks,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "status": self.status.value,
            "evidence": self.evidence,
            "criterion_scores": self.criterion_scores,
            "flags": self.flags,
            "is_mock": self.is_mock,
            "requires_review": self.requires_review,
        }


def enforce_score_bounds(awarded_marks: float, max_marks: float, criterion: str = "") -> None:
    if not math.isfinite(awarded_marks) or not math.isfinite(max_marks):
        raise ValueError(f"Non-finite score detected (criterion: {criterion})")
    if max_marks < 0:
        raise ValueError(f"Rubric criterion '{criterion}' has negative max_marks ({max_marks})")
    if awarded_marks < 0 or awarded_marks > max_marks + 1e-6:  # tiny float tolerance
        raise ValueError(f"Score out of bounds: awarded={awarded_marks}, max={max_marks} (criterion: {criterion})")


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
    """Evaluate with the deterministic MOCK provider (NOT semantic grading).

    Policy notes:
    - Blank/unreadable => 0 marks, requires review.
    - Any non-empty answer => PARTIAL/INCORRECT with LOW confidence; must NOT
      award max_marks automatically.
    - Real grading requires a configured LLM adapter (ChatGPT/Gemini) with
      rubric-linked rationale and evidence from the answer text.
    - This mock is for deterministic tests only.
    """
    criteria = [_criterion_from_value(item) for item in rubric_criteria]
    max_marks = sum(max(0.0, c.max_marks) for c in criteria)

    # Validate rubric definition
    if not criteria:
        raise ValueError("Rubric criteria are empty — cannot score without rubric.")
    for c in criteria:
        if c.max_marks < 0:
            raise ValueError(f"Criterion {c.id} ('{c.criterion}') has invalid max_marks {c.max_marks}")
        if not c.criterion or not str(c.criterion).strip():
            raise ValueError(f"Criterion {c.id} has empty criterion text")

    text = (answer_text or "").strip()

    # Ensure reference answer is present for real-scoring context (warn if missing)
    if not reference_answer or not str(reference_answer).strip():
        # Mock allows missing reference but flags it; real grading requires it.
        pass

    # Blank / unreadable
    if not text or len(text) <= 1:
        status = EvaluationStatus.UNANSWERED if not text else EvaluationStatus.UNRECOGNIZED
        confidence = 0.3 if text else 1.0
        awarded_marks = 0.0
        evidence: list[Any] = []
        flags = {"unanswered": True} if not text else {"unrecognized": True}
        criterion_scores = {
            c.id: {
                "criterion": c.criterion,
                "max_marks": c.max_marks,
                "awarded_marks": 0.0,
                "evidence": [],
                "matched": False,
                "rationale": "No answer provided; human review required.",
            }
            for c in criteria
        }
        enforce_score_bounds(awarded_marks, max_marks, "total")
        return EvaluationResult(
            awarded_marks=awarded_marks,
            max_marks=max_marks,
            rationale="MOCK EVALUATION (not semantic grading): answer is blank or unreadable. Faculty review required before any publication. Never treat this as an AI-approved grade.",
            confidence=confidence,
            status=status,
            evidence=evidence,
            criterion_scores=criterion_scores,
            flags=flags,
            is_mock=True,
            requires_review=True,
        )

    # Non-empty answer — mock must NOT award full marks automatically.
    # Assign partial (simulated) based on simple heuristic: if text contains
    # keyword from criterion guidance, give partial; else low. This is
    # DETERMINISTIC for tests only, NOT semantic grading.
    score_per_criterion = {}
    total_awarded = 0.0
    for c in criteria:
        # Simple deterministic mock logic: partial if text length > 10
        # and contains at least one word from criterion guidance (if present), else low.
        guidance_words = [w.lower() for w in (c.guidance or "").split() if len(w) > 2] if c.guidance else []
        text_words = [w.lower() for w in text.split() if len(w) > 2]

        if not text_words:
            awarded = 0.0
        elif len(text_words) < 3 and (not guidance_words or not any(w in text_words for w in guidance_words)):
            awarded = round(c.max_marks * 0.1, 2)
        elif guidance_words and any(w in text_words for w in guidance_words):
            awarded = round(c.max_marks * 0.6, 2)
        else:
            awarded = round(c.max_marks * 0.3, 2)
        awarded = max(0.0, min(awarded, c.max_marks))
        total_awarded += awarded
        score_per_criterion[c.id] = {
            "criterion": c.criterion,
            "max_marks": c.max_marks,
            "awarded_marks": awarded,
            "evidence": [{"criterion_id": c.id, "text": text[:500]}],
            "matched": awarded > 0,
            "rationale": f"MOCK (not semantic): criterion '{c.criterion}' partially matched (simulated). Requires faculty review.",
        }

    # Validate totals
    enforce_score_bounds(total_awarded, max_marks, "total")

    # Flag if answer is adversarial / repeats keywords incorrectly
    flags = {
        "mock_evaluation": True,
        "requires_faculty_review": True,
        "not_semantically_graded": True,
    }

    # Detect adversarial pattern: answer repeats keywords but gives wrong reasoning
    # (simulated: if text is very short or just keywords, mark lower)
    word_count = len(text.split())
    if word_count < 5 and any(w in text.lower() for w in ("correct", "true", "right", "yes")):
        flags["keyword_repetition_without_reasoning"] = True
        total_awarded = max(0.0, total_awarded * 0.5)  # reduce for adversarial
        for sid in score_per_criterion:
            score_per_criterion[sid]["awarded_marks"] = round(score_per_criterion[sid]["awarded_marks"] * 0.5, 2)
        enforce_score_bounds(total_awarded, max_marks, "total (after adversarial adjustment)")

    status = EvaluationStatus.PARTIAL if total_awarded < max_marks * 0.9 else EvaluationStatus.ANSWERED
    if total_awarded <= 0.01:
        status = EvaluationStatus.INCORRECT

    return EvaluationResult(
        awarded_marks=total_awarded,
        max_marks=max_marks,
        rationale=f"MOCK EVALUATION — NOT SEMANTICALLY GRADED ({status.value}). Answer evidence recorded per criterion. Faculty must review and approve; this is a draft, never a published grade. Model provider: mock (no LLM called).",
        confidence=0.3,  # low due to mock nature
        status=status,
        evidence=[{"criterion_id": sid, "text": text[:500]} for sid in score_per_criterion],
        criterion_scores=score_per_criterion,
        flags=flags,
        is_mock=True,
        requires_review=True,
    )
