# Model / System Card - AI Code Reviewer

## Overview
- **What it is:** an automated code-review pipeline (parse diff, prompt a model, parse structured
  comments) with a labeled bug-catching benchmark. The review logic has no third-party dependency.
- **Base model:** pluggable. Offline, a rule-based provider is used for tests and CI; in production,
  Anthropic's Claude via the Messages API.
- **Version and date:** 0.1.0, 2026.

## Intended use
- **Primary use case:** flagging likely defects in a diff, and measuring a reviewer's bug-catching
  precision and recall.
- **Primary users:** engineering teams adding automated review to their pull-request flow.

## Out-of-scope / prohibited use
- Not a substitute for human review or tests; it is an assistive signal.
- The offline provider catches recognizable patterns, not semantic bugs; do not treat a clean
  offline review as proof of correctness.

## Performance
- Precision 1.000 and recall 0.800 on the labeled benchmark with the offline provider.
- Full method and tables: [`EVALUATION_REPORT.md`](EVALUATION_REPORT.md).

## Limitations and failure modes
- Semantic bugs are missed by the offline provider; a language model is needed for those.
- The benchmark is small and curated; it is a regression guard, not a real-world recall estimate.

## Ethical considerations
- In production the diff is sent to a third-party model; do not submit secret-bearing diffs. The
  service reads credentials from the environment and never logs them.
