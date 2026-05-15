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
