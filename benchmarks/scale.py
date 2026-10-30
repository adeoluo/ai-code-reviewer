"""A large-workload scale benchmark for the code reviewer.

Where ``benchmark.py`` scores the reviewer on the small labeled benchmark and
``stress.py`` drives the HTTP service under concurrent load, this script measures
the core operation - :meth:`Reviewer.review`, which turns a diff into review
comments via the offline rule provider - on progressively larger synthetic sets
of diffs. It reports wall-clock time, throughput, peak memory (via the
standard-library :mod:`tracemalloc`), and line-level detection precision and
recall against planted bugs.

Each diff plants one rule-detectable bug among clean added lines and is generated
deterministically (nothing is downloaded), so the run is reproducible, fully
offline, and the model call is the deterministic offline fake provider. Run with:

    uv run python benchmarks/scale.py
"""

from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass

from ai_code_reviewer.provider import FakeProvider
from ai_code_reviewer.reviewer import Reviewer

WORKLOAD_SIZES: tuple[int, ...] = (8_000, 20_000, 40_000, 80_000)

_BUGS: tuple[str, ...] = (
    "def add(item, bucket=[]):",
    "    result = eval(user_input)",
    '    api_key = "sk-live-9f8a7b6c5d4e3f2a1b"',
    "    subprocess.run(cmd, shell=True)",
    "    if value == None:",
    "    assert user.is_authenticated",
)
_CLEAN: tuple[str, ...] = (
    "    return result",
    "    total = a + b",
    '    logger.info("done")',
)
_START_LINE = 10


def _diff(path: str, start: int, lines: list[str]) -> str:
    header = f"--- a/{path}\n+++ b/{path}\n@@ -{start},0 +{start},{len(lines)} @@\n"
    return header + "".join("+" + line + "\n" for line in lines)


def _make_case(index: int) -> tuple[str, tuple[str, int]]:
    """Build one synthetic diff with a single planted bug on its first added line."""
    path = f"module_{index % 50}.py"
    lines = [_BUGS[index % len(_BUGS)], *_CLEAN]
    return _diff(path, _START_LINE, lines), (path, _START_LINE)


@dataclass(frozen=True, slots=True)
class ScaleRow:
    """One measured row of the scale sweep."""

    size: int
    seconds: float
    throughput: float
    peak_mib: float
    precision: float
    recall: float


def run_workload(size: int) -> ScaleRow:
    """Review ``size`` synthetic diffs and score line-level precision/recall.

    Peak memory is measured over building the workload of diffs (the data
    footprint, which grows with the number of diffs); timing and throughput
    cover the review loop itself.
    """
    reviewer = Reviewer(provider=FakeProvider())
    tracemalloc.start()
    cases = [_make_case(index) for index in range(size)]
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    true_positive = false_positive = false_negative = 0
    start = time.perf_counter()
    for diff_text, bug_line in cases:
        flagged = reviewer.review(diff_text).lines_flagged
        bug = {bug_line}
        true_positive += len(flagged & bug)
        false_negative += len(bug - flagged)
        false_positive += len(flagged - bug)
    elapsed = time.perf_counter() - start

    precision = (
        true_positive / (true_positive + false_positive) if true_positive + false_positive else 1.0
    )
    recall = (
        true_positive / (true_positive + false_negative) if true_positive + false_negative else 1.0
    )
    throughput = size / elapsed if elapsed > 0 else float("inf")
    return ScaleRow(size, elapsed, throughput, peak / (1024 * 1024), precision, recall)


def main() -> None:
    print("AI Code Reviewer scale benchmark")
    print(
        "Data is SYNTHETIC: diffs with planted rule-detectable bugs, generated deterministically."
    )
    print("The model call uses the deterministic offline fake provider.\n")
    header = (
        f"{'diffs':>8}  {'seconds':>8}  {'diffs/sec':>10}  "
        f"{'peak MiB':>9}  {'precision':>10}  {'recall':>8}"
    )
    print(header)
    print("-" * len(header))
    for size in WORKLOAD_SIZES:
        row = run_workload(size)
        print(
            f"{row.size:>8,}  {row.seconds:>8.3f}  {row.throughput:>10,.0f}  "
            f"{row.peak_mib:>9.2f}  {row.precision:>10.3f}  {row.recall:>8.3f}"
        )


if __name__ == "__main__":
    main()
