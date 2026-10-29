# Data Card - AI Code Reviewer

## Source
- **Authored in-repository.** The benchmark diffs are written for this project. There is no external
  dataset, download, or network access in tests or CI.

## Composition
- 13 small unified diffs. Buggy diffs introduce a single known defect (mutable default, bare except,
  ``== None``, ``eval``, hardcoded secret, ``shell=True``, SQL concatenation, ``assert`` validation,
  off-by-one, always-true logic); clean diffs are correct changes that must not be flagged.
- Each buggy diff is labeled with the exact (path, line) locations of the defect.

## Labels and supervision
- The labels are the bug locations, used to score precision and recall. There is no training.

## Provenance and licensing
- Authored for this repository under the MIT license. The code snippets are synthetic examples.

## Filtering and contamination
- Not applicable: the benchmark is a fixed, curated set.

## Known limitations
- The benchmark is small and synthetic by design so it is a clear, deterministic regression guard;
  it is not representative of the full distribution of real bugs.
