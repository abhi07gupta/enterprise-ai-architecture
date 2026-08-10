# ADR-001 — Keep semantic context outside the model prompt

- **Status:** Accepted (synthetic example)
- **Date:** 2026-08-07

## Context
A synthetic service-risk assistant needs product hierarchy, policy constraints and service relationships. Embedding all meaning into prompt templates would couple business semantics to one implementation.

## Decision
Represent critical concepts and relationships in a structured context layer and assemble task-specific context at runtime.

## Alternatives considered
1. Prompt-only instructions.
2. Retrieval over unstructured policy documents only.
3. Fine-tuning business facts into a model.

## Trade-offs
Structured context adds modelling effort, but improves reuse, provenance, changeability and testability.

## Revisit trigger
Revisit if the domain remains trivial enough that structure creates more maintenance cost than value.
