"""The reviewer: build a prompt from a diff, call the provider, parse comments."""

from __future__ import annotations

import json
from dataclasses import dataclass

from ai_code_reviewer.provider import Provider

_SYSTEM = (
    "You are a careful code reviewer. Review only the added lines of the diff and report "
    "concrete defects: likely bugs, security risks, and correctness issues. Respond with a "
    'JSON object {"comments": [{"path", "line", "severity", "message"}]}, severity one of '
    "high, medium, low. Do not comment on style."
)


@dataclass(frozen=True)
class Comment:
    """One review comment."""

    path: str
    line: int
    severity: str
    message: str


@dataclass(frozen=True)
class Review:
    """A full review of a diff."""

    comments: list[Comment]

    def by_severity(self, severity: str) -> list[Comment]:
        return [c for c in self.comments if c.severity == severity]

    @property
    def lines_flagged(self) -> set[tuple[str, int]]:
        return {(c.path, c.line) for c in self.comments}


def build_prompt(diff_text: str) -> str:
    """Return the user prompt that embeds the diff for review."""

    return (
        "Review the added lines in this unified diff and return JSON only.\n"
        f"<diff>{diff_text}</diff>"
    )


@dataclass(frozen=True)
class Reviewer:
    """Reviews diffs using an injected provider."""

    provider: Provider

    def review(self, diff_text: str) -> Review:
        raw = self.provider.complete(_SYSTEM, build_prompt(diff_text))
        return Review(comments=_parse_comments(raw))


def _parse_comments(raw: str) -> list[Comment]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    comments: list[Comment] = []
    for item in data.get("comments", []):
        try:
            comments.append(
                Comment(
                    path=str(item["path"]),
                    line=int(item["line"]),
                    severity=str(item["severity"]),
                    message=str(item["message"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return comments
