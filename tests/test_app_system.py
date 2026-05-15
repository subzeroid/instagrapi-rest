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
    methods = response.json()["paths"]["/user/about"]
    assert "get" in methods
    assert "post" not in methods


@pytest.mark.asyncio
async def test_openapi_reports_app_version_200():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["version"] == "2.0.0"


@pytest.mark.asyncio
async def test_openapi_uses_rest_http_methods():
    expected_methods = {
        "/": {"get"},
        "/version": {"get"},
        "/album/download": {"get"},
        "/album/download/by_urls": {"get"},
        "/album/upload": {"post"},
        "/auth/login": {"post"},
        "/auth/login_by_sessionid": {"post"},
        "/auth/relogin": {"patch"},
        "/auth/settings": {"get", "patch"},
        "/auth/timeline_feed": {"get"},
        "/clip/download": {"get"},
        "/clip/download/by_url": {"get"},
        "/clip/upload": {"post"},
        "/clip/upload/by_url": {"post"},
        "/igtv/download": {"get"},
        "/igtv/download/by_url": {"get"},
        "/igtv/upload": {"post"},
        "/igtv/upload/by_url": {"post"},
        "/insights/account": {"get"},
        "/insights/media": {"get"},
        "/insights/media_feed_all": {"get"},
        "/media/archive": {"patch"},
        "/media/delete": {"delete"},
        "/media/edit": {"patch"},
        "/media/id": {"get"},
        "/media/info": {"get"},
        "/media/like": {"post"},
        "/media/likers": {"get"},
        "/media/oembed": {"get"},
        "/media/pk": {"get"},
        "/media/pk_from_code": {"get"},
        "/media/pk_from_url": {"get"},
        "/media/seen": {"patch"},
        "/media/unarchive": {"patch"},
        "/media/unlike": {"delete"},
        "/media/user": {"get"},
        "/media/user_medias": {"get"},
        "/media/usertag_medias": {"get"},
        "/photo/download": {"get"},
        "/photo/download/by_url": {"get"},
        "/photo/upload": {"post"},
        "/photo/upload/by_url": {"post"},
        "/photo/upload_to_story": {"post"},
        "/photo/upload_to_story/by_url": {"post"},
        "/story/delete": {"delete"},
        "/story/download": {"get"},
        "/story/download/by_url": {"get"},
        "/story/info": {"get"},
        "/story/like": {"post"},
        "/story/pk_from_url": {"get"},
        "/story/seen": {"patch"},
        "/story/unlike": {"delete"},
        "/story/user_stories": {"get"},
        "/user/about": {"get"},
        "/user/follow": {"post"},
        "/user/followers": {"get"},
        "/user/following": {"get"},
        "/user/id_from_username": {"get"},
        "/user/info": {"get"},
        "/user/info_by_username": {"get"},
        "/user/mute_posts_from_follow": {"patch"},
        "/user/mute_stories_from_follow": {"patch"},
        "/user/remove_follower": {"delete"},
        "/user/unfollow": {"delete"},
        "/user/unmute_posts_from_follow": {"patch"},
        "/user/unmute_stories_from_follow": {"patch"},
        "/user/username_from_id": {"get"},
        "/video/download": {"get"},
        "/video/download/by_url": {"get"},
        "/video/upload": {"post"},
        "/video/upload/by_url": {"post"},
        "/video/upload_to_story": {"post"},
        "/video/upload_to_story/by_url": {"post"},
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert set(paths) == set(expected_methods)
    for path, methods in expected_methods.items():
        assert set(paths[path]) == methods


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
