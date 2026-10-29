# Evaluation Report - AI Code Reviewer

> Reproduce with `python -m ai_code_reviewer evaluate` and `benchmarks/benchmark.py`. The benchmark
> and the offline provider are deterministic.

## Setup

- **Benchmark:** 13 small unified diffs. Buggy diffs introduce a real defect on a known line; clean
  diffs must not be flagged.
- **Provider:** the offline rule-based provider, so results are reproducible with no credentials.
- **Metric:** line-level precision and recall. A true positive is a flagged line that is a labeled
  bug; a false positive is a flagged clean line; a false negative is a missed bug line.
- **Hardware / cost:** CPU only; the benchmark runs in a few milliseconds. No external services.

## Results

| Metric | Value |
|---|---:|
| precision | 1.000 |
| recall | 0.800 |
| F1 | 0.889 |
| true positives | 8 |
| false positives | 0 |
| false negatives | 2 |

The reviewer flags no clean line (precision 1.0) and catches 8 of 10 planted bugs. The two misses
are semantic: an off-by-one ``range(len(x) + 1)`` and a logic error ``if role == "admin" or "root":``
that is always truthy. Pattern rules cannot see these; a language model is the reason to expect
higher recall on them, and this benchmark is how that would be demonstrated.

## What the offline provider catches

Mutable default arguments, bare or overly broad excepts, ``== None`` comparisons, ``eval``/``exec``
on dynamic input, ``assert`` used for validation, hardcoded secrets, ``subprocess`` with
``shell=True``, SQL built by string concatenation, and files opened without a context manager.

## Service performance

The `/review` handler parses a diff and runs the provider; with the offline provider a concurrent
stress benchmark sustains about 9,000 requests per second with p50 near 0.06 ms. In production the
latency is dominated by the model call.

## Reproducibility

- Deterministic: the benchmark and offline provider produce identical results every run.
- No network access, no credentials, no external data in CI.
- Regenerate every number with the CLI and `benchmarks/benchmark.py`.
