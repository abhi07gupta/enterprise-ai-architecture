from __future__ import annotations

from dataclasses import dataclass
from typing import Any


REQUIRED_SECTIONS = {
    "initiative": ("name", "owner", "decision_date", "decision"),
    "value": ("outcome", "baseline", "success_measure"),
    "context": ("users", "workflow", "data_classification"),
    "architecture": ("system_boundary", "integration", "fallback"),
    "trust": ("risk_level", "human_oversight", "evaluation"),
    "operations": ("service_owner", "monitoring", "incident_path"),
    "adoption": ("change_owner", "enablement", "feedback_loop"),
}

ALLOWED_RISK = {"low", "medium", "high", "critical"}
ALLOWED_DECISIONS = {"explore", "pilot", "scale", "hold", "retire"}


@dataclass(frozen=True)
class ValidationError:
    path: str
    message: str


def _blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def validate_canvas(canvas: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for section, fields in REQUIRED_SECTIONS.items():
        value = canvas.get(section)
        if not isinstance(value, dict):
            errors.append(ValidationError(section, "required object is missing"))
            continue
        for field in fields:
            if _blank(value.get(field)):
                errors.append(ValidationError(f"{section}.{field}", "required value is missing"))

    risk = canvas.get("trust", {}).get("risk_level")
    if risk not in ALLOWED_RISK:
        errors.append(ValidationError("trust.risk_level", f"must be one of {sorted(ALLOWED_RISK)}"))
    decision = canvas.get("initiative", {}).get("decision")
    if decision not in ALLOWED_DECISIONS:
        errors.append(ValidationError("initiative.decision", f"must be one of {sorted(ALLOWED_DECISIONS)}"))

    trust = canvas.get("trust", {})
    if risk in {"high", "critical"} and trust.get("human_oversight") in {"none", "not required", None, ""}:
        errors.append(ValidationError("trust.human_oversight", "high-risk use requires explicit human oversight"))
    if risk == "critical" and decision == "scale":
        errors.append(ValidationError("initiative.decision", "critical-risk use cannot move directly to scale"))
    return errors
