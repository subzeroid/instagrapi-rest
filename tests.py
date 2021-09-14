import pytest
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_media_pk_from_code() -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            app.url_path_for("media_pk_from_code"),
            params={"code": "B1LbfVPlwIA"}
        )
    assert response.status_code == 200
    assert response.text == "\"2110901750722920960\""


@pytest.mark.asyncio
async def test_media_info() -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            app.url_path_for("media_info"),
            params={"pk": 2110901750722920960}
        )
    media = response.json()
    assert response.status_code == 200
    assert media["pk"] == 2110901750722920960
    assert media["id"] == "2110901750722920960_8572539084"
    assert media["code"] == "B1LbfVPlwIA"
    assert media["media_type"] == 1
