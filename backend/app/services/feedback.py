"""Evidence-linked feedback generation."""

from typing import Any, Mapping

from .scoring import EvaluationResult, EvaluationStatus


def _value(result: EvaluationResult | Mapping[str, Any], name: str, default: Any = None) -> Any:
    if isinstance(result, Mapping):
        return result.get(name, default)
    return getattr(result, name, default)


def _item(text: str, *, certainty: str = "certain", source_evidence: Any = None) -> dict[str, Any]:
    return {
        "text": text,
        "certainty": certainty,
        "source_evidence": source_evidence,
    }


def generate_feedback(evaluation_result: EvaluationResult | Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Generate structured feedback without inventing unsupported claims."""
    strengths: list[dict[str, Any]] = []
    improvements: list[dict[str, Any]] = []
    suggestions: list[dict[str, Any]] = []

    evidence = _value(evaluation_result, "evidence", []) or []
    confidence = float(_value(evaluation_result, "confidence", 0.0) or 0.0)
    flags = _value(evaluation_result, "flags", {}) or {}
    status = _value(evaluation_result, "status")
    if isinstance(status, str):
        try:
            status = EvaluationStatus(status)
        except ValueError:
            pass

    if evidence:
        strengths.append(
            _item(
                "Evidence-backed assessment: rubric criteria were addressed.",
                source_evidence=evidence[0],
            )
        )

    if confidence < 0.6:
        uncertain = _item(
            "Review this evaluation before publishing feedback.",
            certainty="uncertain",
            source_evidence=evidence[0] if evidence else None,
        )
        improvements.append(uncertain)
        suggestions.append(dict(uncertain))

    if flags.get("unanswered") or status is EvaluationStatus.UNANSWERED:
        improvements.append(
            _item(
                "Answer is unanswered; provide a response for this criterion.",
                source_evidence=evidence[0] if evidence else None,
            )
        )
    elif flags.get("unrecognized") or status is EvaluationStatus.UNRECOGNIZED:
        improvements.append(
            _item(
                "Answer was not recognized reliably; clarify or rescan the response.",
                certainty="uncertain",
                source_evidence=evidence[0] if evidence else None,
            )
        )

    criterion_scores = _value(evaluation_result, "criterion_scores", {}) or {}
    for criterion in criterion_scores.values() if isinstance(criterion_scores, Mapping) else []:
        if isinstance(criterion, Mapping) and criterion.get("matched") is False:
            label = criterion.get("criterion", "criterion")
            improvements.append(
                _item(f"Improvement: {label} was not addressed.", source_evidence=criterion.get("evidence"))
            )

    return {
        "strengths": strengths,
        "improvements": improvements,
        "suggestions": suggestions,
    }
