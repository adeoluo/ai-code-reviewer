# ADR-0002: A provider interface with an offline fake

- **Status:** Accepted
- **Date:** 2026-01-01

## Context
The reviewer should use a real language model in production, but tests, the benchmark, and
continuous integration must be deterministic and must not require credentials or network access.

## Decision
Depend only on a small ``Provider`` protocol with a single ``complete(system, prompt)`` method. Ship
two implementations: a ``FakeProvider`` that is offline and rule-based (used by tests, the benchmark,
and CI) and an ``AnthropicProvider`` that calls the Claude Messages API over HTTPS using only the
standard library (used in production). The review logic, prompt construction, and output parsing are
identical for both.

## Consequences
- CI and the benchmark are fully reproducible with no secrets and no network.
- Production gains a real model by swapping the provider; nothing else changes.
- The real provider adds no third-party dependency, because it uses the standard-library HTTP client.
- The offline provider's quality is a pattern detector, not a model, which the evaluation reports
  honestly.
