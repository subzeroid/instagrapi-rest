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
