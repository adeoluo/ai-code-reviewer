"""A deterministic micro-benchmark for the code reviewer.

Scores the offline reviewer on the labeled bug-catching benchmark and prints
line-level precision, recall, and F1, plus the bugs it misses. Deterministic and
offline; run with:

    uv run python benchmarks/benchmark.py
"""

from __future__ import annotations

import time

from ai_code_reviewer.evaluation import evaluate
from ai_code_reviewer.provider import FakeProvider
from ai_code_reviewer.reviewer import Reviewer


def main() -> None:
    reviewer = Reviewer(provider=FakeProvider())
    start = time.perf_counter()
    report = evaluate(reviewer)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"Bug-catching benchmark ({report.cases} labeled diffs, {elapsed:.0f} ms):")
    print(f"  {report.format()}")
    if report.missed:
        print(f"  missed (semantic bugs pattern rules cannot catch): {', '.join(report.missed)}")


if __name__ == "__main__":
    main()
