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
async def test_login_without_verification_code_uses_two_arg_login(fake_storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/auth/login",
            data={
                "username": "u",
                "password": "p",
                "locale": "en_US",
                "timezone": "10800",
            },
        )

    assert response.status_code == 200
    assert response.json() == "sid"
    assert fake_storage.created.locale == "en_US"
    assert fake_storage.created.timezone == "10800"
    assert fake_storage.created.calls == [("login", "u", "p", "")]


@pytest.mark.asyncio
async def test_login_returns_false_without_persisting_on_failure(fake_storage):
    async def failing_login(username, password, verification_code=""):
        fake_storage.created.calls.append(("login", username, password, verification_code))
        return False

    fake_storage.created.login = failing_login

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/auth/login",
            data={"username": "u", "password": "p"},
        )

    assert response.status_code == 200
    assert response.json() is False
    assert fake_storage.saved == []


@pytest.mark.asyncio
async def test_login_2fa_fallback_invokes_input_patch(fake_storage):
    captured = {}

    original_login = fake_storage.created.login

    async def picky_login(username, password, verification_code=None):
        if verification_code is not None:
            raise TypeError("verification_code not supported")
        captured["called"] = (username, password)
        return await original_login(username, password)

    fake_storage.created.login = picky_login

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/auth/login",
            data={"username": "u", "password": "p", "verification_code": "999111"},
        )

    assert response.status_code == 200
    assert captured["called"] == ("u", "p")


@pytest.mark.asyncio
async def test_login_by_sessionid_persists_session(fake_storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/login_by_sessionid", data={"sessionid": "sid"})

    assert response.status_code == 200
    assert response.json() == "sid"
    assert ("login_by_sessionid", "sid") in fake_storage.created.calls
    assert fake_storage.saved == [fake_storage.created]


@pytest.mark.asyncio
async def test_login_by_sessionid_returns_false_without_persisting(fake_storage):
    async def failing_login_by_sessionid(sessionid):
        fake_storage.created.calls.append(("login_by_sessionid", sessionid))
        return False

    fake_storage.created.login_by_sessionid = failing_login_by_sessionid

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/login_by_sessionid", data={"sessionid": "sid"})

    assert response.status_code == 200
    assert response.json() is False
    assert fake_storage.saved == []


@pytest.mark.asyncio
async def test_relogin_awaits_aiograpi(fake_storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/relogin", data={"sessionid": "sid"})

    assert response.status_code == 200
    assert response.json() is True
    assert ("relogin",) in fake_storage.created.calls


@pytest.mark.asyncio
async def test_settings_get_returns_client_settings(fake_storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/auth/settings/get", params={"sessionid": "sid"})

    assert response.status_code == 200
    assert response.json() == {"authorization_data": {"sessionid": "sid"}}


@pytest.mark.asyncio
async def test_settings_set_awaits_expose_and_persists(fake_storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/settings/set", data={"settings": json.dumps({"x": 1})})

    assert response.status_code == 200
    assert fake_storage.created.settings == {"x": 1}
    assert ("expose",) in fake_storage.created.calls


@pytest.mark.asyncio
async def test_settings_set_with_existing_sessionid_reuses_client(fake_storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/auth/settings/set",
            data={"settings": json.dumps({"x": 2}), "sessionid": "sid"},
        )

    assert response.status_code == 200
    assert fake_storage.created.settings == {"x": 2}


@pytest.mark.asyncio
async def test_timeline_feed_awaits_aiograpi(fake_storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/auth/timeline_feed", params={"sessionid": "sid"})

    assert response.status_code == 200
    assert response.json() == {"feed": []}
