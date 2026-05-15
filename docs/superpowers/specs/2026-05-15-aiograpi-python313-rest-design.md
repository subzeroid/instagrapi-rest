# aiograpi Python 3.13 REST Migration Design

## Goal

Move `instagrapi-rest` from synchronous `instagrapi` to asynchronous `aiograpi` from PyPI, update the project to Python 3.13, cover the local REST adapter with tests, add `GET /user/about`, align HTTP methods with REST semantics, publish API version `3.1.0`, and verify the final diff with Claude.

## Fixed Decisions

- Runtime target: Python 3.13.
- API version: `3.1.0` because the REST method and path cleanup was a breaking public API change in `3.0.0`, followed by client-friendly OpenAPI schema naming in `3.1.0`.
- Instagram client dependency: `aiograpi==0.9.7` from PyPI, not `../aiograpi`.
- `aiograpi==0.9.7` requires Python `>=3.10` and was the latest PyPI release checked during planning on 2026-05-15.
- `TEST_ACCOUNTS_URL` may be used only for optional live smoke tests. The default test suite must not require live Instagram accounts or network access.
- Implementation will be driven by `ralphex` using the implementation plan in `docs/superpowers/plans/`.
- Final review will run through the gstack Claude review flow requested as `/claude`.

## Current State

The app is a thin FastAPI wrapper over `instagrapi`. `main.py` registers routers, `storages.py` persists client settings in TinyDB keyed by `sessionid`, route handlers call `clients.get(sessionid)`, then delegate to an `instagrapi.Client` method.

The current dependency set is pinned to Python 3.8 era packages:

- `fastapi==0.65.1`
- `uvicorn==0.11.3`
- `instagrapi>=1.16.30`
- `Pillow==8.1.1`
- `pytest~=6.2.4`
- `httpx==0.17.1`

The current tests are minimal and fail in the local Python 3.14 environment before collection because `main.py` imports `pkg_resources`.

## Architecture

Keep the REST API shape stable and migrate the internal client boundary to async.

`ClientStorage` becomes an async-aware session factory:

- `client()` returns `aiograpi.Client`.
- `get(sessionid)` becomes `async def get(...)`.
- It loads settings from TinyDB, calls `cl.set_settings(settings)`, then validates the session with `await cl.get_timeline_feed()`.
- `set(cl)` continues to persist `cl.get_settings()` keyed by `cl.sessionid`.

Route handlers become async delegates:

- Pure helper methods that are synchronous in `aiograpi` stay sync, for example `media_pk_from_code`.
- Any Instagram IO method is awaited, for example `await cl.media_info(...)`.
- Download endpoints await the download call, then return `FileResponse` or the path as before.
- Upload helpers already use async wrappers and will await `aiograpi` upload methods.
- REST method convention: reads and downloads are `GET`, creates/uploads/login are `POST`, state changes are `PATCH`, and removals are `DELETE`.
- Settings are a single resource: `GET /auth/settings` reads settings and `PATCH /auth/settings` writes settings.
- Public URL paths use slash-separated words instead of underscores, for example `GET /user/info/by/username`.
- Story uploads use a single resource: `POST /story/upload` and `POST /story/upload/by/url`.

The app remains a single FastAPI service with the existing router split:

- `routers/auth.py`
- `routers/media.py`
- `routers/photo.py`
- `routers/video.py`
- `routers/album.py`
- `routers/clip.py`
- `routers/igtv.py`
- `routers/story.py`
- `routers/user.py`
- `routers/insights.py`

## Dependency And Packaging Design

Replace `requirements.txt` with `pyproject.toml`. `pyproject.toml` becomes the single source of truth for runtime dependencies, test dependencies, and tool configuration.

Target runtime dependencies:

- `fastapi`
- `uvicorn[standard]`
- `aiograpi==0.9.7`
- `python-multipart`
- `tinydb`
- `requests`
- `aiofiles`

Target test/development dependencies:

- `pytest`
- `pytest-asyncio`
- `httpx`
- `pytest-cov`
- `ruff`

Docker changes:

- Use `python:3.13-slim`.
- Keep `ffmpeg` and `gcc` because uploads and wheels may need them.
- Install the project from `pyproject.toml`, not `requirements.txt`.
- Run `uvicorn main:app --host 0.0.0.0 --port 8000`.

Compose changes:

- `docker compose up api` must build and run the service successfully.
- The compose service remains named `api`.
- The service must expose port `8000:8000`.
- The app source may stay mounted into `/app` for local development.
- Test commands should run through compose as well, for example `docker compose run --rm api pytest`.

CI changes:

- Use Python 3.13.
- Install project dependencies.
- Run lint and test commands.
- Keep live smoke separate and gated by `TEST_ACCOUNTS_URL`.

## `/user/about`

Add:

```http
GET /user/about?sessionid=<SESSIONID>&user_id=<USER_ID>
```

Behavior:

- Resolve the authenticated client with `await clients.get(sessionid)`.
- Call `await cl.user_about_v1(user_id)`.
- Return `aiograpi.types.About`.

Expected response fields:

- `username`
- `is_verified`
- `country`
- `date`
- `former_usernames`

## Test Strategy

The default suite must be deterministic and network-free.

Offline tests:

- Import app successfully under Python 3.13.
- Verify `/version` reports `aiograpi`.
- Verify OpenAPI generation includes all routers, `GET /user/about`, API version `3.1.0`, slash-separated paths, client-friendly schemas, and the REST HTTP method map.
- Cover `ClientStorage.client`, `ClientStorage.get`, `ClientStorage.set`, session not found, and stored settings reload.
- Cover every route handler at least once using fake async clients and dependency overrides.
- Cover pure media/story PK helper routes with real `aiograpi.Client` pure helpers.
- Cover upload helper functions by injecting fake clients and temporary uploads.
- Cover download endpoints with fake paths and `returnFile=false`.
- Cover the existing `/story/unlike` bug by asserting the handler passes `story_id`.

Live smoke tests:

- Mark as optional.
- Skip when `TEST_ACCOUNTS_URL` is unset.
- Fetch account records from `TEST_ACCOUNTS_URL` using the same account shape as `../aiograpi/tests/live/smoke.py`.
- Login with username/password, proxy, saved settings, and optional TOTP seed when available.
- Exercise a minimal happy path: login, `user_info_by_username`, `user_about_v1`, timeline feed.

Coverage expectation:

- Route and storage behavior should be fully exercised offline.
- Coverage gate should target local adapter code, not generated examples or live-only branches.
- Exclude `golang/`, `swift/`, and generated or static example artifacts from coverage.

## Error Handling

Keep the existing global exception response shape:

```json
{
  "detail": "...",
  "exc_type": "..."
}
```

Do not introduce a new API error envelope in this migration. The goal is a dependency/runtime migration with stable caller behavior.

## Compatibility Notes

`aiograpi` is async for IO methods. The migration must not leave un-awaited coroutines in route responses.

`aiograpi` uses Pydantic v2 models. FastAPI must be updated to a version compatible with Pydantic v2.

`pkg_resources` should be removed from app startup. Use `importlib.metadata.version("aiograpi")` for `/version`.

`login`, `login_by_sessionid`, `relogin`, `GET/PATCH /auth/settings`, and `timeline_feed` must await the corresponding `aiograpi` IO methods.

## Out Of Scope

- Changing public endpoint names or form field names beyond the intentional v2 REST method cleanup and `/auth/settings` consolidation.
- Replacing TinyDB with a production database.
- Adding auth to the REST service itself.
- Solving Instagram account bans, proxy rotation, challenge workers, or managed session orchestration.
- Migrating Go or Swift clients beyond documentation touchups required by the new dependency name.
- Maintaining `requirements.txt`.

## Verification

Required local verification:

```bash
python3.13 -m pytest
python3.13 -m pytest --cov=. --cov-report=term-missing
python3.13 -m compileall .
docker compose build api
docker compose run --rm api pytest
```

Optional live verification:

```bash
TEST_ACCOUNTS_URL="$TEST_ACCOUNTS_URL" python3.13 -m pytest tests/live -m live
```

Final review:

```bash
ralphex docs/superpowers/plans/2026-05-15-aiograpi-python313-rest.md
```

Then run the `/claude` review flow on the resulting diff and address findings.

## Self-Review

- No placeholders remain.
- The dependency source is explicitly PyPI, not the sibling checkout.
- Python 3.13 is explicit in runtime, Docker, CI, and verification.
- `requirements.txt` is replaced by `pyproject.toml`.
- Docker Compose is the supported service launch path.
- `/user/about` request and response behavior are specified.
- Offline tests are separated from live account tests.
- The existing `story_unlike` runtime bug is included in the covered behavior.
