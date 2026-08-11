"""Topology-aware root-cause analysis with explicit abstention."""

from .engine import AnalysisReport, Hypothesis, ScenarioError, analyze_scenario

__all__ = ["AnalysisReport", "Hypothesis", "ScenarioError", "analyze_scenario"]
__version__ = "1.0.0"
