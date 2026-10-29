"""Tests for the diff parser, rules, reviewer, and bug-catching evaluation."""

from __future__ import annotations

from ai_code_reviewer.data import benchmark_cases
from ai_code_reviewer.diff import parse_diff
from ai_code_reviewer.evaluation import evaluate
from ai_code_reviewer.provider import FakeProvider
from ai_code_reviewer.reviewer import Reviewer, build_prompt
from ai_code_reviewer.rules import detect


def test_parse_diff_tracks_added_lines_and_numbers() -> None:
    diff = "--- a/x.py\n+++ b/x.py\n@@ -1,0 +5,2 @@\n+first\n+second\n"
    added = parse_diff(diff)
    assert [(a.path, a.new_line, a.content) for a in added] == [
        ("x.py", 5, "first"),
        ("x.py", 6, "second"),
    ]


def test_parse_diff_ignores_removed_lines() -> None:
    diff = "--- a/x.py\n+++ b/x.py\n@@ -1,1 +1,1 @@\n-old\n+new\n"
    added = parse_diff(diff)
    assert len(added) == 1 and added[0].content == "new"


def test_rules_detect_known_defects() -> None:
    diff = "--- a/x.py\n+++ b/x.py\n@@ -1,0 +1,1 @@\n+    if x == None:\n"
    findings = detect(diff)
    assert findings and findings[0].severity == "low"
    assert "is" in findings[0].message


def test_rules_detect_hardcoded_secret_and_eval() -> None:
    secret = '--- a/x.py\n+++ b/x.py\n@@ -1,0 +1,1 @@\n+api_key = "sk-live-abcdef123456"\n'
    assert any(f.severity == "high" for f in detect(secret))
    danger = "--- a/x.py\n+++ b/x.py\n@@ -1,0 +1,1 @@\n+    y = eval(data)\n"
    assert any("eval" in f.message for f in detect(danger))


def test_rules_do_not_flag_clean_code() -> None:
    clean = "--- a/x.py\n+++ b/x.py\n@@ -1,0 +1,2 @@\n+    if x is None:\n+        return 0\n"
    assert detect(clean) == []


def test_build_prompt_embeds_diff() -> None:
    assert "<diff>" in build_prompt("some diff") and "</diff>" in build_prompt("some diff")


def test_reviewer_parses_fake_provider_output() -> None:
    reviewer = Reviewer(provider=FakeProvider())
    case = next(c for c in benchmark_cases() if c.name == "eval_injection")
    review = reviewer.review(case.diff)
    assert review.comments
    assert review.by_severity("high")


def test_reviewer_handles_non_json_gracefully() -> None:
    class Garbage:
        def complete(self, system: str, prompt: str) -> str:
            return "not json at all"

    review = Reviewer(provider=Garbage()).review("--- a/x\n+++ b/x\n@@ -1,0 +1,1 @@\n+x\n")
    assert review.comments == []


def test_evaluation_precision_high_recall_realistic() -> None:
    report = evaluate(Reviewer(provider=FakeProvider()))
    assert report.precision == 1.0
    assert 0.7 <= report.recall < 1.0  # semantic bugs are intentionally missed
    assert "off_by_one" in report.missed


def test_clean_cases_produce_no_comments() -> None:
    reviewer = Reviewer(provider=FakeProvider())
    for case in benchmark_cases():
        if not case.is_buggy:
            assert reviewer.review(case.diff).comments == []


def test_benchmark_has_buggy_and_clean_cases() -> None:
    cases = benchmark_cases()
    assert any(c.is_buggy for c in cases)
    assert any(not c.is_buggy for c in cases)
