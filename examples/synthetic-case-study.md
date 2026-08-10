# Synthetic case study — service-risk assistant

A fictional industrial company wants to reduce delays in service-ticket resolution. Tickets are distributed across product families and countries; the same symptom can mean different things depending on product configuration and policy.

## Business objective
Improve triage quality and reduce time to a defensible next action.

## Architecture conclusion
The problem is not a generic chatbot. The useful capability combines:
- structured product and policy context;
- retrieval of relevant historical resolutions;
- bounded generation of a recommendation and rationale;
- deterministic policy checks;
- human confirmation for high-impact actions;
- feedback captured for evaluation and knowledge improvement.

## Why this matters
The AI component remains replaceable because context, policy checks, evaluation and workflow integration are explicit system capabilities rather than hidden inside a prompt.
