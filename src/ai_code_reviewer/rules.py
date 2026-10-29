"""A rule-based bug detector over added diff lines.

This is the analysis the offline provider runs. Each rule looks for a recognizable
defect on a line that a change adds, and reports a finding with a severity. The set
is deliberately high-signal: mutable default arguments, bare excepts, ``== None``
comparisons, use of ``eval``/``exec``, ``assert`` used for validation, hardcoded
secrets, and a few more. In production the same findings would come from the
language model; here they come from these rules, which is what makes the
bug-catching benchmark reproducible offline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ai_code_reviewer.diff import AddedLine, parse_diff


@dataclass(frozen=True)
class Finding:
    """A single review comment: a file, a line, a severity, and a message."""

    path: str
    line: int
    severity: str
    message: str


_SECRET = re.compile(r"""(?i)(api_key|secret|password|token)\s*=\s*['"][^'"]{6,}['"]""")


def _rules(line: str) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    stripped = line.strip()
    if re.search(r"def \w+\([^)]*=\s*(\[\]|\{\}|\bset\(\))", line):
        findings.append(
            ("high", "mutable default argument; use None and build inside the function")
        )
    if re.search(r"except\s*:", line) or re.search(r"except\s+Exception\s*:\s*$", stripped):
        findings.append(("medium", "bare or overly broad except; catch a specific exception"))
    if "== None" in line or "!= None" in line:
        findings.append(("low", "compare to None with 'is' or 'is not', not equality"))
    if re.search(r"\beval\(", line) or re.search(r"\bexec\(", line):
        findings.append(("high", "use of eval/exec on dynamic input is an injection risk"))
    if re.search(r"^\s*assert ", line) and "test" not in line.lower():
        findings.append(("medium", "assert is skipped under optimization; validate explicitly"))
    if _SECRET.search(line):
        findings.append(("high", "hardcoded secret; load from the environment instead"))
    if re.search(r"\bshell\s*=\s*True", line):
        findings.append(("high", "subprocess with shell=True risks shell injection"))
    if re.search(r"""(?i)(select|insert|update|delete)\b.*["']\s*\+""", line) or re.search(
        r"(?i)execute\(.*%\s", line
    ):
        findings.append(
            ("high", "SQL built by string concatenation risks injection; use parameters")
        )
    if re.search(r"open\([^)]*\)(?!\s*as)", line) and "with " not in line:
        findings.append(("low", "file opened without a context manager may leak a handle"))
    return findings


def detect(diff_text: str) -> list[Finding]:
    """Return the findings for every added line of ``diff_text``."""

    findings: list[Finding] = []
    for added in parse_diff(diff_text):
        for severity, message in _rules(added.content):
            findings.append(
                Finding(path=added.path, line=added.new_line, severity=severity, message=message)
            )
    return findings


def detect_on_lines(lines: list[AddedLine]) -> list[Finding]:
    """Return findings for a pre-parsed list of added lines."""

    findings: list[Finding] = []
    for added in lines:
        for severity, message in _rules(added.content):
            findings.append(
                Finding(path=added.path, line=added.new_line, severity=severity, message=message)
            )
    return findings
