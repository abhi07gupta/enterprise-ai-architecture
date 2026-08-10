import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from enterprise_ai_architecture import assess, validate_canvas


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.canvas = json.loads((Path(__file__).parents[1] / "examples/service_knowledge_copilot.json").read_text())

    def test_complete_canvas_is_valid(self):
        self.assertEqual(validate_canvas(self.canvas), [])
        result = assess(self.canvas)
        self.assertEqual(result.score, 100)
        self.assertEqual(result.decision, "pilot")

    def test_high_risk_requires_oversight(self):
        self.canvas["trust"]["human_oversight"] = "none"
        errors = validate_canvas(self.canvas)
        self.assertTrue(any(e.path == "trust.human_oversight" for e in errors))
        self.assertEqual(assess(self.canvas).decision, "hold")

    def test_scale_requires_readiness(self):
        self.canvas["initiative"]["decision"] = "scale"
        self.canvas["trust"]["failure_modes"] = ""
        self.assertEqual(assess(self.canvas).decision, "pilot")


if __name__ == "__main__":
    unittest.main()
