"""AI Code Reviewer - automated code review with a bug-catching benchmark."""

from __future__ import annotations

from ai_code_reviewer.data import BenchmarkCase, benchmark_cases
from ai_code_reviewer.diff import AddedLine, parse_diff
from ai_code_reviewer.evaluation import BugReport, evaluate
from ai_code_reviewer.provider import AnthropicProvider, FakeProvider, Provider
from ai_code_reviewer.reviewer import Comment, Review, Reviewer, build_prompt
from ai_code_reviewer.rules import Finding, detect

__version__ = "0.1.0"

__all__ = [
    "AddedLine",
    "AnthropicProvider",
    "BenchmarkCase",
    "BugReport",
    "Comment",
    "FakeProvider",
    "Finding",
    "Provider",
    "Review",
    "Reviewer",
    "__version__",
    "benchmark_cases",
    "build_prompt",
    "detect",
    "evaluate",
    "parse_diff",
]
