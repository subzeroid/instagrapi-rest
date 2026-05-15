import json
from urllib import parse

from aiograpi import Client
from tinydb import Query, TinyDB


class ClientStorage:
    def __init__(self, db_path="./db.json", client_factory=Client):
        self.db = TinyDB(db_path)
        self.client_factory = client_factory

    def client(self):
        """Get new client (helper)
        """
        cl = self.client_factory()
        cl.request_timeout = 0.1
        return cl

    async def get(self, sessionid: str) -> Client:
        """Get client settings
        """
        key = parse.unquote(sessionid.strip(" \""))
        rows = self.db.search(Query().sessionid == key)
        if not rows:
            raise Exception('Session not found (e.g. after reload process), please relogin')
        settings = json.loads(rows[0]['settings'])
        cl = self.client_factory()
        cl.set_settings(settings)
        await cl.get_timeline_feed()
        return cl

    def set(self, cl: Client) -> bool:
        """Set client settings
        """
        key = parse.unquote(cl.sessionid.strip(" \""))
        self.db.insert({'sessionid': key, 'settings': json.dumps(cl.get_settings())})
        return True

    def close(self):
        pass
