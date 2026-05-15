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
