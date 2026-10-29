"""A minimal unified-diff parser.

Only what a reviewer needs is parsed: the file paths and the added lines with
their new line numbers. Hunk headers (``@@ -a,b +c,d @@``) set the line counters;
added lines (starting with ``+`` but not ``+++``) are collected with the line
number they occupy in the new file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


@dataclass(frozen=True)
class AddedLine:
    """A line introduced by a diff, with its path and new-file line number."""

    path: str
    new_line: int
    content: str


def parse_diff(diff_text: str) -> list[AddedLine]:
    """Return the added lines of a unified diff."""

    added: list[AddedLine] = []
    path = "<unknown>"
    new_line = 0
    for raw in diff_text.splitlines():
        if raw.startswith("+++ "):
            path = raw[4:].strip()
            if path.startswith("b/"):
                path = path[2:]
            continue
        if raw.startswith("--- "):
            continue
        hunk = _HUNK.match(raw)
        if hunk:
            new_line = int(hunk.group(1))
            continue
        if raw.startswith("+"):
            added.append(AddedLine(path=path, new_line=new_line, content=raw[1:]))
            new_line += 1
        elif raw.startswith("-"):
            continue
        else:
            new_line += 1
    return added
