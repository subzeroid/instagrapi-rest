import json
import os
import ssl
import urllib.request

import pytest

from aiograpi import Client


pytestmark = pytest.mark.live


def fetch_accounts(url, count=10):
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(
        url + sep + f"count={count}",
        headers={"User-Agent": "Mozilla/5.0 instagrapi-rest-aiograpi-smoke"},
    )
    with urllib.request.urlopen(req, context=ssl._create_unverified_context()) as response:
        return json.loads(response.read())


@pytest.mark.asyncio
async def test_live_login_user_about_and_timeline():
    url = os.environ.get("TEST_ACCOUNTS_URL")
    if not url:
        pytest.skip("TEST_ACCOUNTS_URL not configured")

    accounts = fetch_accounts(url)
    errors = []
    for account in accounts:
        client = Client()
        settings = dict(account.get("client_settings") or account.get("settings") or {})
        totp_seed = settings.pop("totp_seed", None) or account.get("totp_seed")
        client.set_settings(settings)
        if account.get("proxy"):
            client.set_proxy(account["proxy"])
        kwargs = {
            "username": account["username"],
            "password": account["password"],
            "relogin": True,
        }
        if totp_seed:
            kwargs["verification_code"] = client.totp_generate_code(totp_seed)
        try:
            assert await client.login(**kwargs)
            user = await client.user_info_by_username("instagram")
            about = await client.user_about_v1(user.pk)
            feed = await client.get_timeline_feed()
            assert user.username == "instagram"
            assert about.username
            assert isinstance(feed, dict)
            return
        except Exception as exc:
            errors.append(f"{account.get('username', '?')}: {type(exc).__name__}: {exc}")

    pytest.fail("No live test account succeeded: " + " | ".join(errors[:5]))
