# Autonomous Network RCA: Self-Validating Product AI Reference

[![quality](https://github.com/abhi07gupta/enterprise-ai-architecture/actions/workflows/quality.yml/badge.svg)](https://github.com/abhi07gupta/enterprise-ai-architecture/actions/workflows/quality.yml)
[![MIT license](https://img.shields.io/badge/license-MIT-0f766e.svg)](LICENSE)

A runnable, dependency-free reference app for topology-aware root-cause analysis
in autonomous networks. It ranks recent-change, shared-dependency, and resource
or health hypotheses using synthetic telemetry, then self-validates the leading
explanation before recommending an investigation.

The app makes Product AI concerns concrete: the operator's task, the evidence
contract, quality thresholds, abstention, feedback-ready outputs, safe operating
boundaries, and a deterministic audit trace. It does not connect to a network or
perform remediation.

## What it demonstrates

- topology-aware blast-radius reasoning;
- temporal correlation between changes and symptoms;
- positive and contradictory evidence;
- multiple explicit hypothesis generators;
- confidence and ranking-margin thresholds;
- self-validation and counterfactual scope checks;
- abstention when evidence is weak or ambiguous;
- human review before any remediation decision;
- deterministic output, tests, and a stable audit trace.

## Quick start

```bash
cd reference_apps/autonomous-network-rca
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
network-rca data/synthetic_metro_incident.json
python -m unittest discover -s tests -v
```

No model API, network endpoint, database, credential, or third-party Python
package is required.

## Decision contract

The output is either `recommend_investigation` or `abstain`. A recommendation
contains the selected candidate, confidence, separation from the runner-up,
ranked alternatives, evidence, validation checks, and a trace hash. It always
sets `human_review_required` to true and `remediation_allowed` to false.

## Repository map

```text
src/autonomous_network_rca/  analysis engine and CLI
data/                        fully synthetic incident bundle
docs/                        architecture, product brief, evaluation plan
tests/                       twelve deterministic behavior tests
PUBLIC_SAFETY.md             public-data and human-authority boundary
```

## Product and architecture choices

1. **The unit of value is an investigation decision.** A score without usable
   evidence does not improve the operator's task.
2. **Causality is a hypothesis.** Time and topology increase plausibility but do
   not prove root cause.
3. **Contradictions remain visible.** Normal signals can reduce confidence.
4. **Abstention is a product behavior.** A close or weak ranking asks for more
   evidence instead of manufacturing certainty.
5. **Remediation stays outside the AI boundary.** A human validates evidence and
   chooses any operational action through approved systems.

## Standards inspiration

The design is informed by public work on autonomous networks, closed-loop
automation, anomaly and causal analysis, and interoperable telemetry:

- [TM Forum Autonomous Networks](https://www.tmforum.org/missions/autonomous-networks)
- [TM Forum anomaly management and causal analysis](https://www.tmforum.org/resources/guidebook/ig1411-anomaly-management-api-enhancements-to-support-causal-analysis-v1-0-0/)
- [ETSI ZSM closed-loop automation](https://www.etsi.org/deliver/etsi_gs/ZSM/001_099/00901/01.01.01_60/gs_ZSM00901v010101p.pdf)
- [3GPP AI/ML features and analytics](https://www.3gpp.org/technologies/ct3-aiml)
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)

These references inspired the public design. This repository does not claim
standards conformance or certification.

## Public-use note

All data, topology, names, events, and outcomes are synthetic and vendor-neutral.
The project contains no employer-specific concepts or implementation details.
Read [PUBLIC_SAFETY.md](PUBLIC_SAFETY.md) before contributing examples.

## Author

**Abhi Gupta**: AI systems technical leader and architect across enterprise and
product contexts, based in Stockholm.

[Portfolio](https://abhi07gupta.github.io/) ·
[LinkedIn](https://www.linkedin.com/in/abhi07gupta/) ·
[GitHub](https://github.com/abhi07gupta)
