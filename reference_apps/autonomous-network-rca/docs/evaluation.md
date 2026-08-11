# Evaluation plan

A production evaluation set should contain versioned, access-controlled incident
episodes with time windows, topology snapshots, candidate causes, accepted root
causes, and adjudication notes. Split episodes by time or operational region to
reduce leakage.

Track top-1 and top-3 accuracy, mean reciprocal rank, calibration error,
abstention precision and recall, false high-confidence rate, time-to-useful
hypothesis, evidence completeness, and operator override rate. Review results by
incident class and topology depth. Stress tests should remove signals, introduce
late or contradictory telemetry, alter topology, and create two plausible causes.

The included unit tests verify ranking behavior, temporal sensitivity,
contradiction penalties, abstention, self-validation, determinism, input safety,
the audit trace, and the non-remediation boundary. They demonstrate mechanics,
not production performance.
