"""A dependency-free HTTP service exposing the code reviewer.

The service reviews a submitted diff and reports its bug-catching evaluation on the
built-in benchmark. By default it uses the offline rule-based provider, so it runs
with no credentials; a real language-model provider can be injected in production.
The routing logic is a pure function tested without a socket.

Endpoints
---------
``GET  /health``   liveness and the active provider name.
``GET  /ready``    readiness.
``GET  /metrics``  per-route request, error, and latency metrics (Prometheus text).
``POST /review``   body ``{"diff": str}``; review comments for the diff.
``GET  /evaluate`` bug-catching precision and recall on the built-in benchmark.
"""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from ai_code_reviewer.evaluation import evaluate
from ai_code_reviewer.observability import ServiceMetrics
from ai_code_reviewer.provider import FakeProvider, Provider
from ai_code_reviewer.reviewer import Reviewer

JsonObject = dict[str, Any]
_MAX_DIFF = 100_000


@dataclass(frozen=True)
class ReviewService:
    """Holds a reviewer and answers review and evaluation requests."""

    reviewer: Reviewer
    provider_name: str
    metrics: ServiceMetrics = field(default_factory=ServiceMetrics)

    @classmethod
    def with_provider(cls, provider: Provider | None = None) -> ReviewService:
        provider = provider or FakeProvider()
        return cls(reviewer=Reviewer(provider=provider), provider_name=type(provider).__name__)

    def review(self, diff_text: str) -> JsonObject:
        review = self.reviewer.review(diff_text)
        return {
            "comments": [
                {"path": c.path, "line": c.line, "severity": c.severity, "message": c.message}
                for c in review.comments
            ],
            "count": len(review.comments),
        }

    def evaluate(self) -> JsonObject:
        report = evaluate(self.reviewer)
        return {
            "precision": round(report.precision, 6),
            "recall": round(report.recall, 6),
            "f1": round(report.f1, 6),
            "cases": report.cases,
            "missed": list(report.missed),
        }


def _route(
    method: str, path: str, body: Mapping[str, Any], service: ReviewService
) -> tuple[int, JsonObject]:
    if method == "GET" and path == "/health":
        return 200, {"status": "ok", "provider": service.provider_name}
    if method == "GET" and path == "/evaluate":
        return 200, service.evaluate()
    if method == "POST" and path == "/review":
        diff_text = body.get("diff")
        if not isinstance(diff_text, str) or not diff_text or len(diff_text) > _MAX_DIFF:
            return 400, {
                "error": f"'diff' must be a non-empty string of at most {_MAX_DIFF} characters"
            }
        return 200, service.review(diff_text)
    return 404, {"error": f"no route for {method} {path}"}


def handle(
    method: str, path: str, body: Mapping[str, Any], service: ReviewService
) -> tuple[int, JsonObject]:
    """Route a request, recording per-route metrics, and return status and payload."""

    if method == "GET" and path == "/ready":
        return 200, {"status": "ready"}
    start = time.perf_counter()
    status, payload = _route(method, path, body, service)
    service.metrics.observe(
        f"{method} {path}", (time.perf_counter() - start) * 1000.0, error=status >= 400
    )
    return status, payload


class _Handler(BaseHTTPRequestHandler):  # pragma: no cover - exercised over sockets
    service: ReviewService

    def _respond(self, status: int, payload: JsonObject) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path == "/metrics":
            body = self.service.metrics.render_prometheus().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        status, payload = handle("GET", self.path, {}, self.service)
        self._respond(status, payload)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self._respond(400, {"error": "request body is not valid JSON"})
            return
        status, payload = handle("POST", self.path, body, self.service)
        self._respond(status, payload)

    def log_message(self, *_: Any) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:  # pragma: no cover
    """Start the HTTP service (blocking)."""

    handler = type("_BoundHandler", (_Handler,), {"service": ReviewService.with_provider()})
    server = ThreadingHTTPServer((host, port), handler)
    print(f"ai-code-reviewer service listening on http://{host}:{port}")
    server.serve_forever()
