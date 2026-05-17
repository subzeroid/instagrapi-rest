import json

import pytest

from storages import ClientStorage


class FakeClient:
    def __init__(self):
        self.sessionid = "sid"
        self.settings = {}
        self.timeline_called = False

    def set_settings(self, settings):
        self.settings = settings
        return True

    def get_settings(self):
        return {"authorization_data": {"sessionid": self.sessionid}}

    async def get_timeline_feed(self):
        self.timeline_called = True
        return {"ok": True}


@pytest.mark.asyncio
async def test_get_restores_settings_and_validates_timeline(tmp_path, monkeypatch):
    storage = ClientStorage(db_path=tmp_path / "db.json", client_factory=FakeClient)
    storage.db.insert({"sessionid": "sid", "settings": json.dumps({"x": 1})})

    client = await storage.get("sid")

    assert client.settings == {"x": 1}
    assert client.timeline_called is True


def test_set_persists_client_settings(tmp_path):
    storage = ClientStorage(db_path=tmp_path / "db.json", client_factory=FakeClient)
    assert storage.set(FakeClient()) is True
    row = storage.db.all()[0]
    assert row["sessionid"] == "sid"
    assert json.loads(row["settings"]) == {"authorization_data": {"sessionid": "sid"}}


def test_storage_path_can_come_from_environment(tmp_path, monkeypatch):
    db_path = tmp_path / "env-db.json"
    monkeypatch.setenv("AIOGRAPI_REST_DB_PATH", str(db_path))

    storage = ClientStorage(client_factory=FakeClient)
    storage.db.insert({"sessionid": "sid", "settings": "{}"})

    assert db_path.exists()


@pytest.mark.asyncio
async def test_get_missing_session_raises_helpful_error(tmp_path):
    storage = ClientStorage(db_path=tmp_path / "db.json", client_factory=FakeClient)
    with pytest.raises(Exception, match="Session not found"):
        await storage.get("missing")


def test_client_factory_produces_configured_client(tmp_path):
    storage = ClientStorage(db_path=tmp_path / "db.json", client_factory=FakeClient)
    cl = storage.client()
    assert isinstance(cl, FakeClient)
    assert cl.request_timeout == 0.1


def test_close_is_a_no_op(tmp_path):
    storage = ClientStorage(db_path=tmp_path / "db.json", client_factory=FakeClient)
    assert storage.close() is None


def test_get_clients_dependency_yields_storage(monkeypatch, tmp_path):
    import storages
    from dependencies import get_clients

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(storages, "Client", FakeClient)

    gen = get_clients()
    storage = next(gen)
    try:
        assert isinstance(storage, storages.ClientStorage)
    finally:
        with pytest.raises(StopIteration):
            next(gen)
