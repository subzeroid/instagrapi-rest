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
    data = response.json()
    assert data["info"]["title"] == "aiograpi-rest"
    assert data["info"]["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_openapi_uses_rest_http_methods():
    expected_methods = {
        "/": {"get"},
        "/version": {"get"},
        "/album/download": {"get"},
        "/album/download/by/urls": {"get"},
        "/album/upload": {"post"},
        "/auth/login": {"post"},
        "/auth/login/by/sessionid": {"post"},
        "/auth/relogin": {"patch"},
        "/auth/settings": {"get", "patch"},
        "/auth/timeline/feed": {"get"},
        "/clip/download": {"get"},
        "/clip/download/by/url": {"get"},
        "/clip/upload": {"post"},
        "/clip/upload/by/url": {"post"},
        "/igtv/download": {"get"},
        "/igtv/download/by/url": {"get"},
        "/igtv/upload": {"post"},
        "/igtv/upload/by/url": {"post"},
        "/insights/account": {"get"},
        "/insights/media": {"get"},
        "/insights/media/feed/all": {"get"},
        "/media/archive": {"patch"},
        "/media/delete": {"delete"},
        "/media/edit": {"patch"},
        "/media/id": {"get"},
        "/media/info": {"get"},
        "/media/like": {"post"},
        "/media/likers": {"get"},
        "/media/oembed": {"get"},
        "/media/pk": {"get"},
        "/media/pk/from/code": {"get"},
        "/media/pk/from/url": {"get"},
        "/media/seen": {"patch"},
        "/media/unarchive": {"patch"},
        "/media/unlike": {"delete"},
        "/media/user": {"get"},
        "/media/user/medias": {"get"},
        "/media/usertag/medias": {"get"},
        "/photo/download": {"get"},
        "/photo/download/by/url": {"get"},
        "/photo/upload": {"post"},
        "/photo/upload/by/url": {"post"},
        "/story/delete": {"delete"},
        "/story/download": {"get"},
        "/story/download/by/url": {"get"},
        "/story/info": {"get"},
        "/story/like": {"post"},
        "/story/pk/from/url": {"get"},
        "/story/seen": {"patch"},
        "/story/unlike": {"delete"},
        "/story/upload": {"post"},
        "/story/upload/by/url": {"post"},
        "/story/user/stories": {"get"},
        "/user/about": {"get"},
        "/user/follow": {"post"},
        "/user/followers": {"get"},
        "/user/following": {"get"},
        "/user/id/from/username": {"get"},
        "/user/info": {"get"},
        "/user/info/by/username": {"get"},
        "/user/mute/posts/from/follow": {"patch"},
        "/user/mute/stories/from/follow": {"patch"},
        "/user/remove/follower": {"delete"},
        "/user/unfollow": {"delete"},
        "/user/unmute/posts/from/follow": {"patch"},
        "/user/unmute/stories/from/follow": {"patch"},
        "/user/username/from/id": {"get"},
        "/video/download": {"get"},
        "/video/download/by/url": {"get"},
        "/video/upload": {"post"},
        "/video/upload/by/url": {"post"},
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert set(paths) == set(expected_methods)
    for path, methods in expected_methods.items():
        assert set(paths[path]) == methods


@pytest.mark.asyncio
async def test_openapi_uses_client_friendly_schema_names():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    schema_names = set(schema["components"]["schemas"])
    assert not [name for name in schema_names if name.startswith("Body_")]
    assert not [name for name in schema_names if "_" in name]
    assert {
        "AuthLoginRequest",
        "AuthLoginBySessionIdRequest",
        "AuthSettingsRequest",
        "StoryUploadRequest",
        "StoryUploadByUrlRequest",
        "ClipUploadByUrlRequest",
    } <= schema_names

    operation_ids = [
        operation["operationId"]
        for methods in schema["paths"].values()
        for operation in methods.values()
    ]
    assert not [operation_id for operation_id in operation_ids if "_" in operation_id]
    assert "postStoryUploadByUrl" in operation_ids


@pytest.mark.asyncio
async def test_openapi_uses_human_friendly_tag_names():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    operation_tags = {
        tag
        for methods in schema["paths"].values()
        for operation in methods.values()
        for tag in operation["tags"]
    }
    assert operation_tags == {
        "Album (Carousel)",
        "Auth",
        "Clip (Reels)",
        "IGTV (Legacy)",
        "Insights",
        "Media",
        "Photo",
        "Story",
        "System",
        "User",
        "Video",
    }
    assert [tag["name"] for tag in schema["tags"]] == [
        "System",
        "Auth",
        "User",
        "Media",
        "Photo",
        "Video",
        "Clip (Reels)",
        "Album (Carousel)",
        "Story",
        "IGTV (Legacy)",
        "Insights",
    ]


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
            response = await ac.get("/auth/timeline/feed", params={"sessionid": "x"})
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
