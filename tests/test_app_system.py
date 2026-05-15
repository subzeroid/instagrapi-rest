from importlib.metadata import PackageNotFoundError

import pytest
from httpx import ASGITransport, AsyncClient

import main
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


@pytest.mark.asyncio
async def test_version_returns_none_when_package_missing(monkeypatch):
    def fake_version(name):
        raise PackageNotFoundError(name)

    monkeypatch.setattr(main, "package_version", fake_version)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/version")
    assert response.status_code == 200
    assert response.json() == {"aiograpi": None}


@pytest.mark.asyncio
async def test_exception_handler_wraps_errors_in_envelope(monkeypatch):
    from dependencies import get_clients

    class BoomStorage:
        async def get(self, sessionid):
            raise RuntimeError("kapow")

        def close(self):
            pass

    app.dependency_overrides[get_clients] = lambda: BoomStorage()
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/auth/timeline_feed", params={"sessionid": "x"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    body = response.json()
    assert body["detail"] == "kapow"
    assert body["exc_type"] == "RuntimeError"


def test_custom_openapi_caches_schema():
    first = app.openapi()
    second = app.openapi()
    assert first is second
