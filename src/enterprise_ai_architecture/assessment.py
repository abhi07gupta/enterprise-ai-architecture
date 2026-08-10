from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .validation import validate_canvas


DIMENSIONS = ("value", "context", "architecture", "trust", "operations", "adoption")
READINESS_FIELDS = {
    "value": ("outcome", "baseline", "success_measure"),
    "context": ("users", "workflow", "data_classification"),
    "architecture": ("system_boundary", "integration", "fallback"),
    "trust": ("human_oversight", "evaluation", "failure_modes"),
    "operations": ("service_owner", "monitoring", "incident_path"),
    "adoption": ("change_owner", "enablement", "feedback_loop"),
}


@dataclass(frozen=True)
class Assessment:
    score: int
    decision: str
    dimension_scores: dict[str, int]
    blockers: tuple[str, ...]
    next_actions: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "score": self.score,
            "decision": self.decision,
            "dimension_scores": self.dimension_scores,
            "blockers": list(self.blockers),
            "next_actions": list(self.next_actions),
        }


def _present(value: Any) -> bool:
    return value is not None and (not isinstance(value, str) or bool(value.strip()))


def assess(canvas: dict[str, Any]) -> Assessment:
    errors = validate_canvas(canvas)
    dimension_scores: dict[str, int] = {}
    next_actions: list[str] = []
    for dimension, fields in READINESS_FIELDS.items():
        section = canvas.get(dimension, {})
        count = sum(_present(section.get(field)) for field in fields)
        dimension_scores[dimension] = round(100 * count / len(fields))
        for field in fields:
            if not _present(section.get(field)):
                next_actions.append(f"Define {dimension}.{field}")

    score = round(sum(dimension_scores.values()) / len(DIMENSIONS))
    blockers = tuple(f"{item.path}: {item.message}" for item in errors)
    risk = canvas.get("trust", {}).get("risk_level", "critical")
    requested = canvas.get("initiative", {}).get("decision", "hold")
    if blockers or risk == "critical" or score < 60:
        decision = "hold"
    elif requested == "scale" and score < 95:
        decision = "pilot"
    else:
        decision = requested
    return Assessment(score, decision, dimension_scores, blockers, tuple(next_actions))
