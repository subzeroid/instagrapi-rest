import pytest
from httpx import ASGITransport, AsyncClient

from dependencies import get_clients
from main import app


def _user_payload(pk="1", username="instagram"):
    return {
        "pk": pk,
        "username": username,
        "full_name": "Test",
        "is_private": False,
        "profile_pic_url": "https://example.com/p.jpg",
        "is_verified": True,
        "media_count": 0,
        "follower_count": 0,
        "following_count": 0,
        "is_business": False,
    }


def _user_short(pk):
    return {"pk": str(pk), "username": f"u{pk}", "full_name": "Full"}


class FakeClient:
    def __init__(self):
        self.calls = []

    async def user_followers(self, user_id, use_cache=True, amount=0):
        self.calls.append(("user_followers", user_id, use_cache, amount))
        return {1: _user_short(1), 2: _user_short(2)}

    async def user_following(self, user_id, use_cache=True, amount=0):
        self.calls.append(("user_following", user_id, use_cache, amount))
        return {3: _user_short(3)}

    async def user_info(self, user_id, use_cache=True):
        self.calls.append(("user_info", user_id, use_cache))
        return _user_payload(pk=str(user_id))

    async def user_info_by_username(self, username, use_cache=True):
        self.calls.append(("user_info_by_username", username, use_cache))
        return _user_payload(username=username)

    async def user_about_v1(self, user_id):
        self.calls.append(("user_about_v1", user_id))
        return {
            "username": "instagram",
            "is_verified": True,
            "country": "United States",
            "date": "October 2010",
            "former_usernames": "0",
        }

    async def user_follow(self, user_id):
        self.calls.append(("user_follow", user_id))
        return True

    async def user_unfollow(self, user_id):
        self.calls.append(("user_unfollow", user_id))
        return True

    async def user_id_from_username(self, username):
        self.calls.append(("user_id_from_username", username))
        return 42

    async def username_from_user_id(self, user_id):
        self.calls.append(("username_from_user_id", user_id))
        return "instagram"

    async def user_remove_follower(self, user_id):
        self.calls.append(("user_remove_follower", user_id))
        return True

    async def mute_posts_from_follow(self, user_id, revert=False):
        self.calls.append(("mute_posts_from_follow", user_id, revert))
        return True

    async def unmute_posts_from_follow(self, user_id):
        self.calls.append(("unmute_posts_from_follow", user_id))
        return True

    async def mute_stories_from_follow(self, user_id, revert=False):
        self.calls.append(("mute_stories_from_follow", user_id, revert))
        return True

    async def unmute_stories_from_follow(self, user_id):
        self.calls.append(("unmute_stories_from_follow", user_id))
        return True


class FakeStorage:
    def __init__(self):
        self.client_instance = FakeClient()

    async def get(self, sessionid):
        return self.client_instance

    def close(self):
        pass


@pytest.fixture
def storage():
    fake = FakeStorage()
    app.dependency_overrides[get_clients] = lambda: fake
    yield fake
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_user_followers_returns_dict(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/user/followers",
            data={"sessionid": "sid", "user_id": "1", "amount": "5"},
        )
    assert response.status_code == 200
    assert "1" in response.json()
    assert ("user_followers", "1", True, 5) in storage.client_instance.calls


@pytest.mark.asyncio
async def test_user_following_returns_dict(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/user/following",
            data={"sessionid": "sid", "user_id": "1", "use_cache": "false"},
        )
    assert response.status_code == 200
    assert "3" in response.json()
    assert ("user_following", "1", False, 0) in storage.client_instance.calls


@pytest.mark.asyncio
async def test_user_info_awaits_client(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/user/info",
            data={"sessionid": "sid", "user_id": "55"},
        )
    assert response.status_code == 200
    assert response.json()["pk"] == "55"


@pytest.mark.asyncio
async def test_user_info_by_username_awaits_client(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/user/info_by_username",
            data={"sessionid": "sid", "username": "instagram"},
        )
    assert response.status_code == 200
    assert response.json()["username"] == "instagram"


@pytest.mark.asyncio
async def test_user_about_returns_about_payload(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/user/about", data={"sessionid": "sid", "user_id": "25025320"}
        )

    assert response.status_code == 200
    assert response.json()["username"] == "instagram"
    assert response.json()["is_verified"] is True


@pytest.mark.asyncio
async def test_user_follow_awaits_client_method(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/user/follow", data={"sessionid": "sid", "user_id": "1"})

    assert response.status_code == 200
    assert response.json() is True
    assert ("user_follow", 1) in storage.client_instance.calls


@pytest.mark.asyncio
async def test_user_unfollow_awaits_client_method(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/user/unfollow", data={"sessionid": "sid", "user_id": "1"})
    assert response.status_code == 200
    assert ("user_unfollow", 1) in storage.client_instance.calls


@pytest.mark.asyncio
async def test_user_id_from_username_returns_int(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/user/id_from_username",
            data={"sessionid": "sid", "username": "instagram"},
        )
    assert response.status_code == 200
    assert response.json() == 42


@pytest.mark.asyncio
async def test_username_from_user_id_returns_string(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/user/username_from_id",
            data={"sessionid": "sid", "user_id": "1"},
        )
    assert response.status_code == 200
    assert response.json() == "instagram"


@pytest.mark.asyncio
async def test_user_remove_follower_returns_true(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/user/remove_follower",
            data={"sessionid": "sid", "user_id": "1"},
        )
    assert response.status_code == 200
    assert ("user_remove_follower", 1) in storage.client_instance.calls


@pytest.mark.asyncio
async def test_mute_and_unmute_posts_from_follow(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        mute = await ac.post(
            "/user/mute_posts_from_follow",
            data={"sessionid": "sid", "user_id": "1", "revert": "true"},
        )
        unmute = await ac.post(
            "/user/unmute_posts_from_follow",
            data={"sessionid": "sid", "user_id": "1"},
        )
    assert mute.status_code == 200 and mute.json() is True
    assert unmute.status_code == 200 and unmute.json() is True
    assert ("mute_posts_from_follow", 1, True) in storage.client_instance.calls
    assert ("unmute_posts_from_follow", 1) in storage.client_instance.calls


@pytest.mark.asyncio
async def test_mute_and_unmute_stories_from_follow(storage):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        mute = await ac.post(
            "/user/mute_stories_from_follow",
            data={"sessionid": "sid", "user_id": "1"},
        )
        unmute = await ac.post(
            "/user/unmute_stories_from_follow",
            data={"sessionid": "sid", "user_id": "1"},
        )
    assert mute.status_code == 200 and mute.json() is True
    assert unmute.status_code == 200 and unmute.json() is True
    assert ("mute_stories_from_follow", 1, False) in storage.client_instance.calls
    assert ("unmute_stories_from_follow", 1) in storage.client_instance.calls
