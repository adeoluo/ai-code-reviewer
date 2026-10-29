"""A labeled benchmark of diffs, each marked as introducing a bug or clean.

Each case is a small unified diff and the set of (path, line) locations where a
real defect was introduced, or an empty set for a clean change. The reviewer is
scored on whether it flags the buggy lines (recall) without flagging clean lines
(precision). The diffs are written to look like ordinary small pull requests.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BenchmarkCase:
    """One labeled diff: the patch text and the lines where a bug was introduced."""

    name: str
    diff: str
    bug_lines: frozenset[tuple[str, int]] = field(default_factory=frozenset)

    @property
    def is_buggy(self) -> bool:
        return len(self.bug_lines) > 0


def _diff(path: str, start: int, lines: list[str]) -> str:
    header = f"--- a/{path}\n+++ b/{path}\n@@ -{start},0 +{start},{len(lines)} @@\n"
    return header + "".join("+" + line + "\n" for line in lines)


def benchmark_cases() -> list[BenchmarkCase]:
    """Return the labeled benchmark of bug-introducing and clean diffs."""

    return [
        BenchmarkCase(
            name="mutable_default",
            diff=_diff("cache.py", 10, ["def add(item, bucket=[]):", "    bucket.append(item)"]),
            bug_lines=frozenset({("cache.py", 10)}),
        ),
        BenchmarkCase(
            name="bare_except",
            diff=_diff("io.py", 20, ["    try:", "        load()", "    except:", "        pass"]),
            bug_lines=frozenset({("io.py", 22)}),
        ),
        BenchmarkCase(
            name="eq_none",
            diff=_diff("check.py", 5, ["    if value == None:", "        return False"]),
            bug_lines=frozenset({("check.py", 5)}),
        ),
        BenchmarkCase(
            name="eval_injection",
            diff=_diff("calc.py", 30, ["    result = eval(user_input)", "    return result"]),
            bug_lines=frozenset({("calc.py", 30)}),
        ),
        BenchmarkCase(
            name="hardcoded_secret",
            diff=_diff("client.py", 3, ['    api_key = "sk-live-9f8a7b6c5d4e3f2a1b"']),
            bug_lines=frozenset({("client.py", 3)}),
        ),
        BenchmarkCase(
            name="shell_true",
            diff=_diff("run.py", 12, ["    subprocess.run(cmd, shell=True)"]),
            bug_lines=frozenset({("run.py", 12)}),
        ),
        BenchmarkCase(
            name="assert_validation",
            diff=_diff("api.py", 8, ["    assert user.is_authenticated", "    grant_access(user)"]),
            bug_lines=frozenset({("api.py", 8)}),
        ),
        BenchmarkCase(
            name="sql_concat",
            diff=_diff(
                "db.py", 25, ['    cursor.execute("SELECT * FROM users WHERE id=" + user_id)']
            ),
            bug_lines=frozenset({("db.py", 25)}),
        ),
        BenchmarkCase(
            name="off_by_one",
            diff=_diff(
                "iterate.py",
                18,
                ["    for i in range(len(items) + 1):", "        process(items[i])"],
            ),
            bug_lines=frozenset({("iterate.py", 18)}),
        ),
        BenchmarkCase(
            name="logic_always_true",
            diff=_diff(
                "auth.py",
                9,
                ['    if role == "admin" or "root":', "        grant_admin()"],
            ),
            bug_lines=frozenset({("auth.py", 9)}),
        ),
        BenchmarkCase(
            name="clean_refactor",
            diff=_diff(
                "math.py",
                40,
                ["def total(values):", "    return sum(values)"],
            ),
            bug_lines=frozenset(),
        ),
        BenchmarkCase(
            name="clean_guard",
            diff=_diff(
                "user.py",
                15,
                ["    if value is None:", "        raise ValueError('value required')"],
            ),
            bug_lines=frozenset(),
        ),
        BenchmarkCase(
            name="clean_context_manager",
            diff=_diff(
                "files.py",
                50,
                ["    with open(path) as handle:", "        data = handle.read()"],
            ),
            bug_lines=frozenset(),
        ),
    ]
