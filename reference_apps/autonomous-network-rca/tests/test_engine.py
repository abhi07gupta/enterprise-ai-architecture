import copy
import json
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from autonomous_network_rca import ScenarioError, analyze_scenario


class AutonomousNetworkRCATests(unittest.TestCase):
    def setUp(self):
        self.scenario = json.loads((PROJECT / "data/synthetic_metro_incident.json").read_text())

    def test_recent_change_is_ranked_first(self):
        report = analyze_scenario(self.scenario)
        self.assertEqual(report.hypotheses[0].candidate, "aggregation-a")
        self.assertEqual(report.hypotheses[0].cause_type, "recent_change")

    def test_shared_dependency_hypothesis_is_generated(self):
        report = analyze_scenario(self.scenario)
        matches = [h for h in report.hypotheses if h.candidate == "aggregation-a" and h.cause_type == "shared_dependency"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].affected_coverage, 1.0)

    def test_stale_change_loses_temporal_support(self):
        scenario = copy.deepcopy(self.scenario)
        scenario["signals"][0]["timestamp"] = "2026-08-11T08:00:00Z"
        report = analyze_scenario(scenario)
        change = next(h for h in report.hypotheses if h.cause_type == "recent_change")
        self.assertFalse(change.self_validation["temporal_order"])
        self.assertLess(change.confidence, 0.7)

    def test_contradictory_normal_signal_reduces_confidence(self):
        baseline = analyze_scenario(self.scenario).hypotheses[0].confidence
        scenario = copy.deepcopy(self.scenario)
        scenario["signals"].append({"id":"normal-9","timestamp":"2026-08-11T10:05:00Z","kind":"status","node":"aggregation-a","name":"health","state":"normal"})
        changed = analyze_scenario(scenario).hypotheses[0].confidence
        self.assertLess(changed, baseline)

    def test_low_evidence_causes_abstention(self):
        scenario = {"scenario_id":"thin","nodes":["isolated"],"topology":[],"signals":[{"id":"a1","timestamp":"2026-08-11T10:00:00Z","kind":"alarm","node":"isolated","name":"loss","state":"degraded"}]}
        report = analyze_scenario(scenario)
        self.assertEqual(report.decision, "abstain")
        self.assertIsNone(report.selected_candidate)

    def test_top_hypothesis_passes_self_validation(self):
        report = analyze_scenario(self.scenario)
        self.assertTrue(all(report.hypotheses[0].self_validation.values()))

    def test_analysis_is_deterministic(self):
        first = analyze_scenario(self.scenario).to_dict()
        second = analyze_scenario(self.scenario).to_dict()
        self.assertEqual(first, second)

    def test_remediation_is_never_authorized(self):
        report = analyze_scenario(self.scenario)
        self.assertTrue(report.human_review_required)
        self.assertFalse(report.remediation_allowed)

    def test_audit_trace_is_stable_sha256(self):
        trace = analyze_scenario(self.scenario).audit_trace
        self.assertEqual(len(trace), 64)
        self.assertTrue(all(char in "0123456789abcdef" for char in trace))

    def test_unknown_signal_node_is_rejected(self):
        scenario = copy.deepcopy(self.scenario)
        scenario["signals"][0]["node"] = "unknown"
        with self.assertRaises(ScenarioError):
            analyze_scenario(scenario)

    def test_duplicate_signal_id_is_rejected(self):
        scenario = copy.deepcopy(self.scenario)
        scenario["signals"].append(copy.deepcopy(scenario["signals"][0]))
        with self.assertRaises(ScenarioError):
            analyze_scenario(scenario)

    def test_recommendation_requires_human_review(self):
        report = analyze_scenario(self.scenario)
        self.assertEqual(report.decision, "recommend_investigation")
        self.assertIn("human operator", report.next_step)


if __name__ == "__main__":
    unittest.main()
