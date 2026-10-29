# Threat Model - AI Code Reviewer

## Assets
- The HTTP service's availability and the integrity of its responses, and any credentials used by a
  production provider.

## Trust boundaries
- The only external input is the JSON body and path of a request. The review logic and benchmark are
  in-process. In production, the diff is sent to a third-party model over HTTPS.

## Entry points and mitigations

### `POST /review`
- **Malformed JSON** is rejected with 400 before routing.
- **Validation:** the diff must be a non-empty string within a size bound; oversized or wrong-type
  input returns 400 with a message.
- **Bounded work:** the diff size is capped, so a single request cannot force unbounded parsing.

### `GET` routes
- `/health`, `/ready`, `/evaluate`, and `/metrics` take no user input and return fixed-shape
  payloads. `/metrics` exposes only aggregate counters.

## Provider and credentials
- The offline provider needs no secrets. The Anthropic provider reads its key from the environment,
  never from the request, and never logs it. CI uses only the offline provider.

## Data handling
- In production, submitted diffs are sent to the model. Callers should not submit secret-bearing
  diffs; the reviewer itself flags hardcoded secrets it sees.

## Supply chain
- Zero third-party runtime dependencies; the production provider uses the standard-library HTTP
  client. Development tooling is pinned via `uv.lock`. CodeQL and dependency scanning run in CI.

## Residual risk
- A flood of requests could exhaust CPU or, in production, model quota. A deployment would add a rate
  limiter behind a reverse proxy.
