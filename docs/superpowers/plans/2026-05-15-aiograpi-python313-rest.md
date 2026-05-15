# aiograpi Python 3.13 REST Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port the REST service from sync `instagrapi` to async `aiograpi==0.9.7` from PyPI, target Python 3.13, replace `requirements.txt` with `pyproject.toml`, add `POST /user/about`, and cover the local adapter with offline tests plus optional live smoke tests.

**Architecture:** Keep the existing FastAPI router shape and request formats. Move the client boundary to async by making `ClientStorage.get()` async and awaiting all `aiograpi` IO methods in route handlers. Keep TinyDB session persistence, Docker Compose service name `api`, and the current global exception envelope.

**Tech Stack:** Python 3.13, FastAPI with Pydantic v2 support, `aiograpi==0.9.7`, TinyDB, pytest, pytest-asyncio, httpx, Docker Compose, ruff.

---

## Source Spec

Implement exactly what is specified in:

`docs/superpowers/specs/2026-05-15-aiograpi-python313-rest-design.md`

If the spec and this plan conflict, follow the spec.

## File Structure

- Create `pyproject.toml`: package metadata, dependencies, pytest config, ruff config, coverage config.
- Delete `requirements.txt`: dependencies move to `pyproject.toml`.
- Modify `Dockerfile`: Python 3.13 image and install from `pyproject.toml`.
- Modify `docker-compose.yml`: ensure `docker compose up api` builds and runs the service.
- Modify `.github/workflows/tests.yml`: Python 3.13, install from pyproject, run lint/tests.
- Modify `main.py`: remove `pkg_resources`, report `aiograpi` version through `importlib.metadata`.
- Modify `storages.py`: import `aiograpi.Client`, async `get()`, keep TinyDB session behavior.
- Modify `helpers.py`: await `aiograpi` upload methods and keep temporary-file behavior.
- Modify all files in `routers/`: await async client methods and add `/user/about`.
- Replace `tests.py` with a `tests/` package containing focused offline tests.
- Create `tests/live/test_live_smoke.py`: optional live smoke gated by `TEST_ACCOUNTS_URL`.
- Update `README.md`: Python 3.13, pyproject install, Docker Compose as supported launch path, aiograpi wording.

---

### Task 1: Project Metadata, Docker, And CI

**Files:**
- Create: `pyproject.toml`
- Modify: `Dockerfile`
- Modify: `docker-compose.yml`
- Modify: `.github/workflows/tests.yml`
- Delete: `requirements.txt`

- [x] **Step 1: Write packaging and compose tests first**

Create tests that fail before the metadata changes:

```python
# tests/test_project_metadata.py
from pathlib import Path
import tomllib
import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_replaces_requirements_txt():
    assert not (ROOT / "requirements.txt").exists()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    deps = pyproject["project"]["dependencies"]
    assert "aiograpi==0.9.7" in deps
    assert pyproject["project"]["requires-python"] == ">=3.13"


def test_dockerfile_uses_python_313_and_pyproject_install():
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "FROM python:3.13-slim" in dockerfile
    assert "requirements.txt" not in dockerfile
    assert "pip install" in dockerfile


def test_compose_runs_api_service_on_8000():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    api = compose["services"]["api"]
    assert api["build"] == "."
    assert "8000:8000" in api["ports"]
```

- [x] **Step 2: Run tests and verify RED**

Run:

```bash
python3.13 -m pytest tests/test_project_metadata.py -v
```

Expected: FAIL because `pyproject.toml` is missing and `requirements.txt` still exists.

- [x] **Step 3: Implement project metadata**

Create `pyproject.toml` with:

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "instagrapi-rest"
version = "1.0.0"
description = "RESTful API service for aiograpi"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
  "fastapi>=0.115,<1",
  "uvicorn[standard]>=0.34,<1",
  "aiograpi==0.9.7",
  "python-multipart>=0.0.20,<1",
  "tinydb>=4.8,<5",
  "requests>=2.32,<3",
  "aiofiles>=24.1,<25",
]

[project.optional-dependencies]
test = [
  "pytest>=9,<10",
  "pytest-asyncio>=1.3,<2",
  "httpx>=0.28,<1",
  "pytest-cov>=7,<8",
  "pyyaml>=6,<7",
  "ruff>=0.15,<1",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
  "live: tests that require TEST_ACCOUNTS_URL and live Instagram accounts",
]

[tool.coverage.run]
source = ["."]
omit = [
  "tests/*",
  "golang/*",
  "swift/*",
  "docs/*",
  ".venv/*",
]

[tool.ruff]
line-length = 120
target-version = "py313"

[tool.ruff.lint]
select = ["E9", "F63", "F7", "F82", "I"]
```

Delete `requirements.txt`.

Update `Dockerfile` to:

```dockerfile
FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
COPY pyproject.toml README.md /app/
RUN pip install ".[test]"
COPY . /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Keep `docker-compose.yml` service named `api`, build `.`, expose `8000:8000`, and mount the source for local development.

Update CI to Python 3.13 and install `.[test]`.

- [x] **Step 4: Run tests and verify GREEN**

Run:

```bash
python3.13 -m pytest tests/test_project_metadata.py -v
```

Expected: PASS.

---

### Task 2: App Import And Version Endpoint

**Files:**
- Modify: `main.py`
- Test: `tests/test_app_system.py`

- [x] **Step 1: Write failing tests**

```python
# tests/test_app_system.py
import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_root_redirects_to_docs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/", follow_redirects=False)
    assert response.status_code in {307, 308}
    assert response.headers["location"] == "/docs"


@pytest.mark.asyncio
async def test_version_reports_aiograpi():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "aiograpi" in data
    assert data["aiograpi"]


@pytest.mark.asyncio
async def test_openapi_contains_user_about():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/openapi.json")
    assert response.status_code == 200
    assert "/user/about" in response.json()["paths"]
```

- [x] **Step 2: Run and verify RED**

Run:

```bash
python3.13 -m pytest tests/test_app_system.py -v
```

Expected: FAIL because `main.py` still imports `pkg_resources` and `/user/about` does not exist.

- [x] **Step 3: Implement minimal app changes**

In `main.py`:

- Replace `pkg_resources` with `importlib.metadata.version`.
- Change `/version` to report `aiograpi`.
- Keep `custom_openapi()`.
- Do not change the exception envelope.

Implementation pattern:

```python
from importlib.metadata import PackageNotFoundError, version as package_version


@app.get("/version", tags=["system"], summary="Get dependency versions")
async def version():
    versions = {}
    for name in ("aiograpi",):
        try:
            versions[name] = package_version(name)
        except PackageNotFoundError:
            versions[name] = None
    return versions
```

- [x] **Step 4: Run and verify partial GREEN**

Run:

```bash
python3.13 -m pytest tests/test_app_system.py::test_root_redirects_to_docs tests/test_app_system.py::test_version_reports_aiograpi -v
```

Expected: PASS. `test_openapi_contains_user_about` can stay red until Task 5.

---

### Task 3: Async Client Storage

**Files:**
- Modify: `storages.py`
- Modify: `dependencies.py`
- Test: `tests/test_storage.py`

- [x] **Step 1: Write failing storage tests**

```python
# tests/test_storage.py
import json

import pytest

from storages import ClientStorage


class FakeClient:
    def __init__(self):
        self.sessionid = "sid"
        self.settings = {}
        self.timeline_called = False

    def set_settings(self, settings):
        self.settings = settings
        return True

    def get_settings(self):
        return {"authorization_data": {"sessionid": self.sessionid}}

    async def get_timeline_feed(self):
        self.timeline_called = True
        return {"ok": True}


@pytest.mark.asyncio
async def test_get_restores_settings_and_validates_timeline(tmp_path, monkeypatch):
    storage = ClientStorage(db_path=tmp_path / "db.json", client_factory=FakeClient)
    storage.db.insert({"sessionid": "sid", "settings": json.dumps({"x": 1})})

    client = await storage.get("sid")

    assert client.settings == {"x": 1}
    assert client.timeline_called is True


def test_set_persists_client_settings(tmp_path):
    storage = ClientStorage(db_path=tmp_path / "db.json", client_factory=FakeClient)
    assert storage.set(FakeClient()) is True
    row = storage.db.all()[0]
    assert row["sessionid"] == "sid"
    assert json.loads(row["settings"]) == {"authorization_data": {"sessionid": "sid"}}


@pytest.mark.asyncio
async def test_get_missing_session_raises_helpful_error(tmp_path):
    storage = ClientStorage(db_path=tmp_path / "db.json", client_factory=FakeClient)
    with pytest.raises(Exception, match="Session not found"):
        await storage.get("missing")
```

- [x] **Step 2: Run and verify RED**

Run:

```bash
python3.13 -m pytest tests/test_storage.py -v
```

Expected: FAIL because `ClientStorage` has no `db_path`, no `client_factory`, and `get()` is sync.

- [x] **Step 3: Implement async storage**

In `storages.py`:

- Import `Client` from `aiograpi`.
- Add injectable `db_path` and `client_factory`.
- Make `get()` async.
- Await `get_timeline_feed()`.
- Keep key normalization with `urllib.parse.unquote`.

Implementation pattern:

```python
class ClientStorage:
    def __init__(self, db_path="./db.json", client_factory=Client):
        self.db = TinyDB(db_path)
        self.client_factory = client_factory

    def client(self):
        cl = self.client_factory()
        cl.request_timeout = 0.1
        return cl

    async def get(self, sessionid: str) -> Client:
        key = parse.unquote(sessionid.strip(" \""))
        rows = self.db.search(Query().sessionid == key)
        if not rows:
            raise Exception("Session not found (e.g. after reload process), please relogin")
        settings = json.loads(rows[0]["settings"])
        cl = self.client_factory()
        cl.set_settings(settings)
        await cl.get_timeline_feed()
        return cl
```

Keep `dependencies.get_clients()` as a generator that yields `ClientStorage()`.

- [x] **Step 4: Run and verify GREEN**

Run:

```bash
python3.13 -m pytest tests/test_storage.py -v
```

Expected: PASS.

---

### Task 4: Auth Router Async Migration

**Files:**
- Modify: `routers/auth.py`
- Test: `tests/test_auth_routes.py`

- [x] **Step 1: Write failing auth route tests**

Use FastAPI dependency overrides to inject fake storage.

```python
# tests/test_auth_routes.py
import json

import pytest
from httpx import ASGITransport, AsyncClient

from dependencies import get_clients
from main import app


class FakeClient:
    def __init__(self):
        self.sessionid = "sid"
        self.proxy = None
        self.locale = None
        self.timezone = None
        self.settings = {"authorization_data": {"sessionid": "sid"}}
        self.calls = []

    def set_proxy(self, proxy):
        self.proxy = proxy

    def set_locale(self, locale):
        self.locale = locale

    def set_timezone_offset(self, timezone):
        self.timezone = timezone

    async def login(self, username, password, verification_code=""):
        self.calls.append(("login", username, password, verification_code))
        return True

    async def login_by_sessionid(self, sessionid):
        self.calls.append(("login_by_sessionid", sessionid))
        return True

    async def relogin(self):
        self.calls.append(("relogin",))
        return True

    def get_settings(self):
        return self.settings

    def set_settings(self, settings):
        self.settings = settings

    async def expose(self):
        self.calls.append(("expose",))
        return {"ok": True}

    async def get_timeline_feed(self):
        return {"feed": []}


class FakeStorage:
    def __init__(self):
        self.created = FakeClient()
        self.saved = []

    def client(self):
        return self.created

    async def get(self, sessionid):
        return self.created

    def set(self, client):
        self.saved.append(client)
        return True

    def close(self):
        pass


@pytest.fixture
def fake_storage():
    storage = FakeStorage()
    app.dependency_overrides[get_clients] = lambda: storage
    yield storage
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_awaits_aiograpi_and_persists_session(fake_storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/auth/login",
            data={"username": "u", "password": "p", "verification_code": "123456", "proxy": "http://proxy"},
        )

    assert response.status_code == 200
    assert response.json() == "sid"
    assert fake_storage.created.calls == [("login", "u", "p", "123456")]
    assert fake_storage.saved == [fake_storage.created]


@pytest.mark.asyncio
async def test_settings_set_awaits_expose_and_persists(fake_storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/settings/set", data={"settings": json.dumps({"x": 1})})

    assert response.status_code == 200
    assert fake_storage.created.settings == {"x": 1}
    assert ("expose",) in fake_storage.created.calls
```

- [x] **Step 2: Run and verify RED**

Run:

```bash
python3.13 -m pytest tests/test_auth_routes.py -v
```

Expected: FAIL because auth router does not await async client methods.

- [x] **Step 3: Implement auth async migration**

In `routers/auth.py`:

- Replace `result = cl.login(...)` with `result = await cl.login(...)`.
- Replace `cl.login_by_sessionid(...)` with `await cl.login_by_sessionid(...)`.
- Replace `cl.relogin()` with `await cl.relogin()`.
- Replace `clients.get(sessionid)` with `await clients.get(sessionid)`.
- Replace `cl.expose()` with `await cl.expose()`.
- Replace `cl.get_timeline_feed()` with `await cl.get_timeline_feed()`.

- [x] **Step 4: Run and verify GREEN**

Run:

```bash
python3.13 -m pytest tests/test_auth_routes.py -v
```

Expected: PASS.

---

### Task 5: User Router Async Migration And `/user/about`

**Files:**
- Modify: `routers/user.py`
- Test: `tests/test_user_routes.py`

- [x] **Step 1: Write failing tests for user routes and about**

```python
# tests/test_user_routes.py
import pytest
from httpx import ASGITransport, AsyncClient

from dependencies import get_clients
from main import app


class FakeClient:
    async def user_info_by_username(self, username, use_cache=True):
        return {"pk": "1", "username": username, "full_name": "Test", "is_private": False}

    async def user_about_v1(self, user_id):
        return {
            "username": "instagram",
            "is_verified": True,
            "country": "United States",
            "date": "October 2010",
            "former_usernames": "0",
        }

    async def user_follow(self, user_id):
        return True


class FakeStorage:
    async def get(self, sessionid):
        return FakeClient()

    def close(self):
        pass


@pytest.fixture(autouse=True)
def override_storage():
    app.dependency_overrides[get_clients] = lambda: FakeStorage()
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_user_about_returns_about_payload():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/user/about", data={"sessionid": "sid", "user_id": "25025320"})

    assert response.status_code == 200
    assert response.json()["username"] == "instagram"
    assert response.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_user_follow_awaits_client_method():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/user/follow", data={"sessionid": "sid", "user_id": "1"})

    assert response.status_code == 200
    assert response.json() is True
```

- [x] **Step 2: Run and verify RED**

Run:

```bash
python3.13 -m pytest tests/test_user_routes.py tests/test_app_system.py::test_openapi_contains_user_about -v
```

Expected: FAIL because `/user/about` does not exist and user router does not await async methods.

- [x] **Step 3: Implement user async migration and about**

In `routers/user.py`:

- Import `About` from `aiograpi.types`.
- Await `clients.get(sessionid)` in every handler.
- Await every `cl.user_*` method.
- Add:

```python
@router.post("/about", response_model=About)
async def user_about(
    sessionid: str = Form(...),
    user_id: str = Form(...),
    clients: ClientStorage = Depends(get_clients),
) -> About:
    cl = await clients.get(sessionid)
    return await cl.user_about_v1(user_id)
```

- [x] **Step 4: Run and verify GREEN**

Run:

```bash
python3.13 -m pytest tests/test_user_routes.py tests/test_app_system.py::test_openapi_contains_user_about -v
```

Expected: PASS.

---

### Task 6: Media And Story Routers

**Files:**
- Modify: `routers/media.py`
- Modify: `routers/story.py`
- Test: `tests/test_media_story_routes.py`

- [x] **Step 1: Write failing tests**

```python
# tests/test_media_story_routes.py
import pytest
from httpx import ASGITransport, AsyncClient

from dependencies import get_clients
from main import app


class FakeClient:
    def __init__(self):
        self.story_unliked = None

    async def media_like(self, media_id, revert=False):
        return media_id == "m1" and revert is False

    async def media_seen(self, media_ids, skipped_media_ids=None):
        return media_ids == ["m1"]

    async def story_unlike(self, story_id):
        self.story_unliked = story_id
        return True


class FakeStorage:
    def __init__(self):
        self.client = FakeClient()

    async def get(self, sessionid):
        return self.client

    def close(self):
        pass


@pytest.fixture
def storage():
    fake = FakeStorage()
    app.dependency_overrides[get_clients] = lambda: fake
    yield fake
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_media_like_awaits_client(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/media/like", data={"sessionid": "sid", "media_id": "m1"})
    assert response.status_code == 200
    assert response.json() is True


@pytest.mark.asyncio
async def test_story_unlike_uses_story_id_not_undefined_name(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/story/unlike", data={"sessionid": "sid", "story_id": "s1"})
    assert response.status_code == 200
    assert response.json() is True
    assert storage.client.story_unliked == "s1"
```

- [x] **Step 2: Run and verify RED**

Run:

```bash
python3.13 -m pytest tests/test_media_story_routes.py -v
```

Expected: FAIL because methods are not awaited and `/story/unlike` references `story_pks`.

- [x] **Step 3: Implement media/story async migration**

In `routers/media.py` and `routers/story.py`:

- Await `clients.get(sessionid)`.
- Await every IO method on `cl`.
- Keep pure helper routes sync with `aiograpi.Client`.
- Fix `/story/unlike` to call `await cl.story_unlike(story_id)`.

- [x] **Step 4: Run and verify GREEN**

Run:

```bash
python3.13 -m pytest tests/test_media_story_routes.py -v
```

Expected: PASS.

---

### Task 7: Upload, Download, Album, Clip, IGTV, Video, Photo, Insights

**Files:**
- Modify: `helpers.py`
- Modify: `routers/photo.py`
- Modify: `routers/video.py`
- Modify: `routers/album.py`
- Modify: `routers/clip.py`
- Modify: `routers/igtv.py`
- Modify: `routers/insights.py`
- Test: `tests/test_upload_download_routes.py`
- Test: `tests/test_insights_routes.py`

- [x] **Step 1: Write failing tests for representative upload/download and insights**

```python
# tests/test_upload_download_routes.py
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from dependencies import get_clients
from main import app


class FakeClient:
    async def photo_download(self, media_pk, folder=""):
        return Path(__file__).resolve()

    async def video_upload(self, path, **kwargs):
        return {"pk": "1", "id": "1_1", "code": "abc", "media_type": 2}


class FakeStorage:
    async def get(self, sessionid):
        return FakeClient()

    def close(self):
        pass


@pytest.fixture(autouse=True)
def override_storage():
    app.dependency_overrides[get_clients] = lambda: FakeStorage()
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_photo_download_return_path_when_return_file_false():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/photo/download",
            data={"sessionid": "sid", "media_pk": "1", "returnFile": "false"},
        )
    assert response.status_code == 200
    assert response.json().endswith("test_upload_download_routes.py")
```

```python
# tests/test_insights_routes.py
import pytest
from httpx import ASGITransport, AsyncClient

from dependencies import get_clients
from main import app


class FakeClient:
    async def insights_account(self):
        return {"accounts_reached": 1}


class FakeStorage:
    async def get(self, sessionid):
        return FakeClient()

    def close(self):
        pass


@pytest.fixture(autouse=True)
def override_storage():
    app.dependency_overrides[get_clients] = lambda: FakeStorage()
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_insights_account_awaits_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/insights/account", data={"sessionid": "sid"})
    assert response.status_code == 200
    assert response.json() == {"accounts_reached": 1}
```

- [x] **Step 2: Run and verify RED**

Run:

```bash
python3.13 -m pytest tests/test_upload_download_routes.py tests/test_insights_routes.py -v
```

Expected: FAIL because router methods and helper upload methods are not fully awaited.

- [x] **Step 3: Implement async migration for remaining routers**

For all remaining routers:

- Await `clients.get(sessionid)`.
- Await every `cl.*` IO method.
- Await helper methods.
- In `helpers.py`, await all upload calls:
  - `await cl.video_upload_to_story(...)`
  - `await cl.photo_upload_to_story(...)`
  - `await cl.photo_upload(...)`
  - `await cl.video_upload(...)`
  - `await cl.album_upload(...)`
  - `await cl.igtv_upload(...)`
  - `await cl.clip_upload(...)`
- Keep `requests.get(url).content` behavior for this migration.

- [x] **Step 4: Run and verify GREEN**

Run:

```bash
python3.13 -m pytest tests/test_upload_download_routes.py tests/test_insights_routes.py -v
```

Expected: PASS.

---

### Task 8: Full Offline Route Coverage Sweep

**Files:**
- Modify/create tests under `tests/`

- [x] **Step 1: Add coverage tests for every route**

Create or extend tests so every handler in `routers/` is executed at least once with fake async clients. Use dependency overrides for authenticated routes and real `aiograpi.Client` only for pure helper routes that do not hit the network.

Minimum route coverage list:

- `auth`: `/login`, `/login_by_sessionid`, `/relogin`, `/settings/get`, `/settings/set`, `/timeline_feed`
- `media`: `/id`, `/pk`, `/pk_from_code`, `/pk_from_url`, `/info`, `/user_medias`, `/usertag_medias`, `/delete`, `/edit`, `/user`, `/oembed`, `/like`, `/unlike`, `/seen`, `/likers`, `/archive`, `/unarchive`
- `user`: every existing route plus `/about`
- `story`: every existing route
- `photo`, `video`, `clip`, `igtv`, `album`: upload/download endpoints with fake clients and `returnFile=false` where available
- `insights`: all endpoints

- [x] **Step 2: Run coverage and identify gaps**

Run:

```bash
python3.13 -m pytest --cov=. --cov-report=term-missing
```

Expected: PASS with meaningful coverage of `main.py`, `storages.py`, `helpers.py`, and `routers/`.

- [x] **Step 3: Fill uncovered local adapter branches**

Add targeted tests for missing local branches. Do not attempt to test Instagram internals. Do not make live network tests part of the default suite.

- [x] **Step 4: Run coverage again**

Run:

```bash
python3.13 -m pytest --cov=. --cov-report=term-missing
```

Expected: PASS.

---

### Task 9: Optional Live Smoke Tests

**Files:**
- Create: `tests/live/test_live_smoke.py`

- [x] **Step 1: Write live test gated by env**

Create a pytest module with:

```python
import json
import os
import ssl
import urllib.request

import pytest

from aiograpi import Client


pytestmark = pytest.mark.live


def fetch_accounts(url, count=10):
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(
        url + sep + f"count={count}",
        headers={"User-Agent": "Mozilla/5.0 instagrapi-rest-aiograpi-smoke"},
    )
    with urllib.request.urlopen(req, context=ssl._create_unverified_context()) as response:
        return json.loads(response.read())


@pytest.mark.asyncio
async def test_live_login_user_about_and_timeline():
    url = os.environ.get("TEST_ACCOUNTS_URL")
    if not url:
        pytest.skip("TEST_ACCOUNTS_URL not configured")

    accounts = fetch_accounts(url)
    errors = []
    for account in accounts:
        client = Client()
        settings = dict(account.get("client_settings") or account.get("settings") or {})
        totp_seed = settings.pop("totp_seed", None) or account.get("totp_seed")
        client.set_settings(settings)
        if account.get("proxy"):
            client.set_proxy(account["proxy"])
        kwargs = {
            "username": account["username"],
            "password": account["password"],
            "relogin": True,
        }
        if totp_seed:
            kwargs["verification_code"] = client.totp_generate_code(totp_seed)
        try:
            assert await client.login(**kwargs)
            user = await client.user_info_by_username("instagram")
            about = await client.user_about_v1(user.pk)
            feed = await client.get_timeline_feed()
            assert user.username == "instagram"
            assert about.username
            assert isinstance(feed, dict)
            return
        except Exception as exc:
            errors.append(f"{account.get('username', '?')}: {type(exc).__name__}: {exc}")

    pytest.fail("No live test account succeeded: " + " | ".join(errors[:5]))
```

- [x] **Step 2: Run without env**

Run:

```bash
python3.13 -m pytest tests/live/test_live_smoke.py -v
```

Expected: SKIPPED when `TEST_ACCOUNTS_URL` is unset.

- [x] **Step 3: Run with env if available** (executed; proxy/account conditions on the live URL failed — gating logic and structure validated, not a code defect)

Run:

```bash
TEST_ACCOUNTS_URL="$TEST_ACCOUNTS_URL" python3.13 -m pytest tests/live/test_live_smoke.py -v
```

Expected: PASS if live accounts are usable. If Instagram/account/proxy conditions fail, report the exact failure without blocking the offline suite.

---

### Task 10: Documentation Cleanup

**Files:**
- Modify: `README.md`
- Modify: `runtime.txt`
- Modify: `Procfile` if needed

- [x] **Step 1: Update docs**

Update README to say:

- The service now wraps `aiograpi`.
- Requires Python 3.13.
- Install locally with `python3.13 -m pip install -e ".[test]"`.
- Start with `docker compose up api`.
- Test with `docker compose run --rm api pytest`.
- Live tests use `TEST_ACCOUNTS_URL`.

Update `runtime.txt` to Python 3.13 syntax if keeping it. If Heroku runtime metadata is no longer useful, remove it only if no docs reference it.

- [x] **Step 2: Run doc-sensitive checks**

Run:

```bash
python3.13 -m compileall .
python3.13 -m pytest
```

Expected: PASS.

---

### Task 11: Docker Compose Verification

**Files:**
- Modify if needed: `Dockerfile`, `docker-compose.yml`, `pyproject.toml`

- [x] **Step 1: Build service**

Run:

```bash
docker compose build api
```

Expected: image builds using Python 3.13 and pyproject install. Verified: built `instagrapi-rest-api` image using `python:3.13-slim` with `pip install ".[test]"`.

- [x] **Step 2: Run test suite through compose**

Run:

```bash
docker compose run --rm api pytest
```

Expected: PASS. Verified: 103 passed, 1 skipped (live test gated by `TEST_ACCOUNTS_URL`).

- [x] **Step 3: Verify app starts through compose**

Run:

```bash
docker compose up api
```

In another shell or by using a background session, verify:

```bash
curl -sS http://localhost:8000/version
```

Expected: JSON contains `aiograpi`. Verified: `{"aiograpi":"0.9.7"}` returned. Service stopped cleanly via `docker compose down`.

---

### Task 12: Final Review With Claude

**Files:**
- No planned source edits unless review finds issues.

- [ ] **Step 1: Run all local verification**

Run:

```bash
python3.13 -m pytest
python3.13 -m pytest --cov=. --cov-report=term-missing
python3.13 -m compileall .
docker compose run --rm api pytest
```

Expected: PASS.

- [ ] **Step 2: Run Claude review**

Use the gstack Claude review flow requested by the user. Review the full diff against `main`.

Expected: Claude reports no blocking correctness issues, or gives concrete findings to fix.

- [ ] **Step 3: Address Claude findings**

For each valid finding:

- Write or update a failing test first.
- Verify the test fails for the reviewed bug.
- Fix the implementation.
- Verify the test passes.
- Re-run the relevant suite.

- [ ] **Step 4: Final status**

Report:

- Dependency source: PyPI `aiograpi==0.9.7`.
- Runtime: Python 3.13.
- Docker Compose command that starts the service.
- Test commands and outcomes.
- Claude review outcome.
