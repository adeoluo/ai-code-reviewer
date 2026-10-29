"""Evaluation: line-level precision and recall of catching planted bugs."""

from __future__ import annotations

from dataclasses import dataclass

from ai_code_reviewer.data import BenchmarkCase, benchmark_cases
from ai_code_reviewer.reviewer import Reviewer


@dataclass(frozen=True)
class BugReport:
    """Line-level detection quality over the labeled benchmark."""

    true_positives: int
    false_positives: int
    false_negatives: int
    cases: int
    missed: tuple[str, ...]

    @property
    def precision(self) -> float:
        denom = self.true_positives + self.false_positives
        return self.true_positives / denom if denom else 1.0

    @property
    def recall(self) -> float:
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom else 1.0

    @property
    def f1(self) -> float:
        if self.precision + self.recall == 0:
            return 0.0
        return 2 * self.precision * self.recall / (self.precision + self.recall)

    def format(self) -> str:
        return (
            f"precision={self.precision:.3f}, recall={self.recall:.3f}, f1={self.f1:.3f} "
            f"over {self.cases} cases (TP={self.true_positives}, "
            f"FP={self.false_positives}, FN={self.false_negatives})"
        )


def evaluate(reviewer: Reviewer, cases: list[BenchmarkCase] | None = None) -> BugReport:
    """Score ``reviewer`` on the labeled benchmark at the line level."""

    cases = cases or benchmark_cases()
    tp = fp = fn = 0
    missed: list[str] = []
    for case in cases:
        flagged = reviewer.review(case.diff).lines_flagged
        bug = set(case.bug_lines)
        tp += len(flagged & bug)
        fn += len(bug - flagged)
        fp += len(flagged - bug)
        if bug - flagged:
            missed.append(case.name)
    return BugReport(
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        cases=len(cases),
        missed=tuple(missed),
    )
