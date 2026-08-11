from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


ALLOWED_KINDS = {"alarm", "change", "metric", "status"}
SYMPTOM_STATES = {"anomalous", "degraded", "failed"}


class ScenarioError(ValueError):
    """Raised when scenario data violates the public input contract."""


@dataclass(frozen=True)
class Hypothesis:
    candidate: str
    cause_type: str
    confidence: float
    positive_evidence: tuple[str, ...]
    contradictory_evidence: tuple[str, ...]
    affected_coverage: float
    self_validation: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["positive_evidence"] = list(self.positive_evidence)
        value["contradictory_evidence"] = list(self.contradictory_evidence)
        return value


@dataclass(frozen=True)
class AnalysisReport:
    decision: str
    selected_candidate: str | None
    confidence: float
    margin: float
    hypotheses: tuple[Hypothesis, ...]
    human_review_required: bool
    remediation_allowed: bool
    next_step: str
    audit_trace: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "selected_candidate": self.selected_candidate,
            "confidence": self.confidence,
            "margin": self.margin,
            "hypotheses": [item.to_dict() for item in self.hypotheses],
            "human_review_required": self.human_review_required,
            "remediation_allowed": self.remediation_allowed,
            "next_step": self.next_step,
            "audit_trace": self.audit_trace,
        }


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ScenarioError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _validate(scenario: dict[str, Any]) -> None:
    if not isinstance(scenario, dict):
        raise ScenarioError("scenario must be a JSON object")
    nodes = scenario.get("nodes")
    topology = scenario.get("topology")
    signals = scenario.get("signals")
    if not isinstance(nodes, list) or not nodes or not all(isinstance(x, str) and x for x in nodes):
        raise ScenarioError("nodes must be a non-empty list of identifiers")
    if len(nodes) != len(set(nodes)):
        raise ScenarioError("node identifiers must be unique")
    if not isinstance(topology, list) or not isinstance(signals, list):
        raise ScenarioError("topology and signals must be lists")
    known = set(nodes)
    for edge in topology:
        if not isinstance(edge, dict) or edge.get("source") not in known or edge.get("target") not in known:
            raise ScenarioError("every topology edge must reference known nodes")
    signal_ids: set[str] = set()
    for signal in signals:
        if not isinstance(signal, dict) or signal.get("node") not in known:
            raise ScenarioError("every signal must reference a known node")
        if signal.get("kind") not in ALLOWED_KINDS:
            raise ScenarioError(f"unsupported signal kind: {signal.get('kind')!r}")
        signal_id = signal.get("id")
        if not isinstance(signal_id, str) or not signal_id or signal_id in signal_ids:
            raise ScenarioError("signal identifiers must be present and unique")
        signal_ids.add(signal_id)
        _timestamp(signal.get("timestamp"))


def _descendants(nodes: list[str], edges: list[dict[str, str]]) -> dict[str, set[str]]:
    children = {node: set() for node in nodes}
    for edge in edges:
        children[edge["source"]].add(edge["target"])
    reach: dict[str, set[str]] = {}
    for node in nodes:
        seen: set[str] = set()
        pending = list(children[node])
        while pending:
            child = pending.pop()
            if child in seen:
                continue
            seen.add(child)
            pending.extend(children[child] - seen)
        reach[node] = seen
    return reach


def _is_symptom(signal: dict[str, Any]) -> bool:
    return signal.get("kind") in {"alarm", "metric", "status"} and signal.get("state") in SYMPTOM_STATES


def _bounded(value: float) -> float:
    return round(max(0.0, min(0.99, value)), 3)


def analyze_scenario(
    scenario: dict[str, Any], *, min_confidence: float = 0.62, min_margin: float = 0.08, change_window_minutes: int = 20
) -> AnalysisReport:
    """Rank explanations and abstain when evidence cannot distinguish a cause.

    The function recommends investigation only. It never executes remediation.
    """
    _validate(scenario)
    nodes: list[str] = scenario["nodes"]
    reach = _descendants(nodes, scenario["topology"])
    signals: list[dict[str, Any]] = sorted(scenario["signals"], key=lambda x: (x["timestamp"], x["id"]))
    symptoms = [signal for signal in signals if _is_symptom(signal)]
    affected = {signal["node"] for signal in symptoms}
    normal = [signal for signal in signals if signal.get("state") == "normal"]
    first_symptom = min((_timestamp(s["timestamp"]) for s in symptoms), default=None)
    hypotheses: list[Hypothesis] = []

    def coverage(candidate: str) -> tuple[float, list[dict[str, Any]]]:
        scope = reach[candidate] | {candidate}
        covered = [signal for signal in symptoms if signal["node"] in scope]
        ratio = len({signal["node"] for signal in covered}) / max(1, len(affected))
        return ratio, covered

    for change in (signal for signal in signals if signal["kind"] == "change"):
        candidate = change["node"]
        ratio, covered = coverage(candidate)
        change_time = _timestamp(change["timestamp"])
        gap = (first_symptom - change_time).total_seconds() / 60 if first_symptom else -1
        temporal_ok = 0 <= gap <= change_window_minutes
        contradictions = [s for s in normal if s["node"] == candidate and _timestamp(s["timestamp"]) >= change_time]
        positive = [f"{change['id']}: change on {candidate}"]
        positive.extend(f"{s['id']}: affected node {s['node']} is downstream" for s in covered)
        if temporal_ok:
            positive.append(f"change preceded the first symptom by {gap:.1f} minutes")
        contradictory = [f"{s['id']}: normal signal on candidate" for s in contradictions]
        score = 0.28 + 0.32 * ratio + (0.20 if temporal_ok else -0.15) + min(0.12, 0.04 * len(covered)) - 0.15 * len(contradictions)
        checks = {
            "temporal_order": temporal_ok,
            "blast_radius_coverage": ratio >= 0.5,
            "contradiction_check": len(contradictions) <= len(positive),
            "counterfactual_scope": ratio > 0,
        }
        hypotheses.append(Hypothesis(candidate, "recent_change", _bounded(score), tuple(positive), tuple(contradictory), round(ratio, 3), checks))

    for candidate in nodes:
        ratio, covered = coverage(candidate)
        covered_nodes = {signal["node"] for signal in covered}
        if len(covered_nodes) < 2:
            continue
        direct = [signal for signal in symptoms if signal["node"] == candidate]
        contradictions = [signal for signal in normal if signal["node"] == candidate]
        positive = [f"shared upstream scope covers {len(covered_nodes)} affected nodes"]
        positive.extend(f"{s['id']}: anomaly on candidate" for s in direct)
        contradictory = [f"{s['id']}: normal signal on candidate" for s in contradictions]
        score = 0.22 + 0.42 * ratio + min(0.12, 0.06 * len(direct)) - 0.15 * len(contradictions)
        checks = {
            "temporal_order": True,
            "blast_radius_coverage": ratio >= 0.5,
            "contradiction_check": len(contradictions) <= len(positive),
            "counterfactual_scope": ratio > 0,
        }
        hypotheses.append(Hypothesis(candidate, "shared_dependency", _bounded(score), tuple(positive), tuple(contradictory), round(ratio, 3), checks))

    for signal in symptoms:
        if signal["kind"] != "metric" or signal.get("name") not in {"cpu_utilization", "memory_utilization", "health_score"}:
            continue
        candidate = signal["node"]
        ratio, covered = coverage(candidate)
        contradictions = [s for s in normal if s["node"] == candidate and s.get("name") == signal.get("name")]
        score = 0.42 + 0.24 * ratio + min(0.12, 0.04 * len(covered)) - 0.18 * len(contradictions)
        positive = (f"{signal['id']}: anomalous {signal.get('name')} on candidate",)
        contradictory = tuple(f"{s['id']}: normal {s.get('name')} on candidate" for s in contradictions)
        checks = {
            "temporal_order": True,
            "blast_radius_coverage": ratio >= 0.5,
            "contradiction_check": not contradictions,
            "counterfactual_scope": ratio > 0,
        }
        hypotheses.append(Hypothesis(candidate, "resource_or_health", _bounded(score), positive, contradictory, round(ratio, 3), checks))

    hypotheses.sort(key=lambda item: (-item.confidence, item.candidate, item.cause_type))
    top = hypotheses[0] if hypotheses else None
    runner_up = hypotheses[1].confidence if len(hypotheses) > 1 else 0.0
    margin = round((top.confidence - runner_up) if top else 0.0, 3)
    validated = bool(top and all(top.self_validation.values()))
    selected = bool(top and top.confidence >= min_confidence and margin >= min_margin and validated)
    decision = "recommend_investigation" if selected else "abstain"
    candidate = top.candidate if selected else None
    next_step = (
        f"A human operator should review evidence for {candidate} before selecting any remediation."
        if selected
        else "Collect or reconcile more telemetry; no root cause is sufficiently distinguished."
    )
    trace_payload = {
        "scenario_id": scenario.get("scenario_id", "unnamed"),
        "signals": [signal["id"] for signal in signals],
        "ranking": [(item.candidate, item.cause_type, item.confidence) for item in hypotheses],
        "decision": decision,
        "selected_candidate": candidate,
    }
    audit_trace = hashlib.sha256(json.dumps(trace_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return AnalysisReport(decision, candidate, top.confidence if top else 0.0, margin, tuple(hypotheses), True, False, next_step, audit_trace)
