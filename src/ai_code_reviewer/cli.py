"""Command line interface for the code reviewer."""

from __future__ import annotations

import argparse
import sys

from ai_code_reviewer.data import benchmark_cases
from ai_code_reviewer.evaluation import evaluate
from ai_code_reviewer.provider import FakeProvider
from ai_code_reviewer.reviewer import Reviewer


def _reviewer() -> Reviewer:
    return Reviewer(provider=FakeProvider())


def _cmd_evaluate(_: argparse.Namespace) -> None:
    report = evaluate(_reviewer())
    print("Bug-catching evaluation on the labeled benchmark:")
    print(f"  {report.format()}")
    if report.missed:
        print(f"  missed (semantic bugs pattern rules cannot catch): {', '.join(report.missed)}")


def _cmd_review(args: argparse.Namespace) -> None:
    diff_text = sys.stdin.read() if args.stdin else benchmark_cases()[args.case].diff
    review = _reviewer().review(diff_text)
    if not review.comments:
        print("No issues found.")
        return
    for comment in review.comments:
        print(f"  {comment.path}:{comment.line} [{comment.severity}] {comment.message}")


def _cmd_serve(args: argparse.Namespace) -> None:
    from ai_code_reviewer.service import serve

    serve(host=args.host, port=args.port)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="ai-code-reviewer", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("evaluate", help="bug-catching precision and recall on the benchmark")

    review = sub.add_parser("review", help="review a diff (a benchmark case, or stdin)")
    review.add_argument("--case", type=int, default=0, help="index into the built-in benchmark")
    review.add_argument("--stdin", action="store_true", help="read a unified diff from stdin")

    serve = sub.add_parser("serve", help="start the HTTP service")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    handlers = {"evaluate": _cmd_evaluate, "review": _cmd_review, "serve": _cmd_serve}
    args = parser.parse_args(argv)
    handlers[args.command](args)


if __name__ == "__main__":
    main()
