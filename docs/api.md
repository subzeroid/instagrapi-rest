# API Guide

## Authentication

Protected routes accept the saved session ID through the `X-Session-ID` header.
Swagger UI exposes this through the green **Authorize** button.

Public session-creation routes:

- `POST /auth/login`
- `POST /auth/login/by/sessionid`
- `PATCH /auth/settings`

Session-aware routes still accept legacy `sessionid` values from query
parameters, form data, or a `sessionid` cookie for backwards compatibility.

## Route Conventions

- `GET` routes read or download data.
- `POST` routes create sessions, create actions, or upload media.
- `PATCH` routes update state.
- `DELETE` routes remove or undo state.
- Paths use slash-separated resources such as `/story/upload/by/url`.

## OpenAPI

- Swagger UI: `/docs`
- Raw schema: `/openapi.json`

The schema uses client-friendly operation IDs and request schema names so it can
be passed directly into OpenAPI client generators.

## System Endpoints

- `GET /health` returns `{"status":"ok"}` for liveness.
- `GET /ready` checks storage and required runtime dependencies.
- `GET /metrics` exports Prometheus text metrics.
- `GET /build` returns service build metadata.
- `GET /deps` returns runtime dependency versions.
