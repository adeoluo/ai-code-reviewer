"""Tests for the HTTP service routing and the CLI."""

from __future__ import annotations

from ai_code_reviewer.data import benchmark_cases
from ai_code_reviewer.service import ReviewService, handle

_SERVICE = ReviewService.with_provider()


def test_health_and_ready() -> None:
    status, payload = handle("GET", "/health", {}, _SERVICE)
    assert status == 200 and payload["provider"] == "FakeProvider"
    status, payload = handle("GET", "/ready", {}, _SERVICE)
    assert status == 200 and payload["status"] == "ready"


def test_review_route_flags_bug() -> None:
    case = next(c for c in benchmark_cases() if c.name == "hardcoded_secret")
    status, payload = handle("POST", "/review", {"diff": case.diff}, _SERVICE)
    assert status == 200
    assert payload["count"] >= 1
    assert any(c["severity"] == "high" for c in payload["comments"])


def test_review_route_clean_diff() -> None:
    case = next(c for c in benchmark_cases() if c.name == "clean_guard")
    status, payload = handle("POST", "/review", {"diff": case.diff}, _SERVICE)
    assert status == 200 and payload["count"] == 0


def test_review_validation() -> None:
    for body in ({"diff": ""}, {"diff": 5}, {}):
        status, _ = handle("POST", "/review", body, _SERVICE)
        assert status == 400


def test_evaluate_route() -> None:
    status, payload = handle("GET", "/evaluate", {}, _SERVICE)
    assert status == 200
    assert payload["precision"] == 1.0
    assert 0.7 <= payload["recall"] < 1.0


def test_unknown_route_and_metrics() -> None:
    status, _ = handle("GET", "/nope", {}, _SERVICE)
    assert status == 404
    handle("GET", "/evaluate", {}, _SERVICE)
    assert "service_requests_total" in _SERVICE.metrics.render_prometheus()


def test_cli_commands(capsys) -> None:  # type: ignore[no-untyped-def]
    from ai_code_reviewer.cli import main

    main(["evaluate"])
    main(["review", "--case", "3"])
    out = capsys.readouterr().out
    assert "precision=" in out
