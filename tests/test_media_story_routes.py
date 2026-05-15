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
