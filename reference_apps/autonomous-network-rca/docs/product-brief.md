# Product brief

## User problem

Operators investigating a multi-node incident often receive many alarms without
a compact, inspectable explanation of which dependency or recent change deserves
attention first. The product question is how to shorten investigation while
making uncertainty and contradictory evidence visible.

## Reference experience

1. Load a topology and time-ordered signal bundle.
2. Review ranked hypotheses with evidence and blast-radius coverage.
3. See an explicit abstention when confidence or ranking separation is weak.
4. Confirm the evidence outside the tool before choosing a remediation.

## Product requirements

- deterministic and explainable ranking;
- latency suitable for interactive investigation;
- schema validation and stable audit traces;
- visible positive and contradictory evidence;
- measured abstention quality, not only top-1 accuracy;
- human authority over every remediation decision;
- feedback capture and scenario-based regression testing in a real implementation.

This is a public product-engineering reference, not a claim of a deployed network
product or commercial product-management ownership.
