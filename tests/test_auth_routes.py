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
