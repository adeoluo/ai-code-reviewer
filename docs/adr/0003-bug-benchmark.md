# ADR-0003: Evaluate on labeled bug-introducing diffs

- **Status:** Accepted
- **Date:** 2026-01-01

## Context
Most automated review tools are never measured, so there is no way to tell whether their comments
catch real defects or just add noise. Without a benchmark, a change to the reviewer cannot be judged.

## Decision
Ship a labeled benchmark: small unified diffs, each annotated with the exact lines where a real
defect was introduced, plus clean diffs that must not be flagged. Score the reviewer at the line
level with precision and recall, and surface which bugs it missed.

## Consequences
- The reviewer's value is a measured number, and every change is a regression test against it.
- The benchmark deliberately includes semantic bugs that pattern rules cannot catch, so recall is
  below one and the gap is attributable to the kind of reasoning a language model provides.
- Precision of one on clean diffs demonstrates the reviewer does not flag correct code, which is the
  failure mode that makes review tools get ignored.
