from urllib import parse
from instagrapi import Client
from tinydb import TinyDB, Query
import json

class ClientStorage:
    db = TinyDB('./db.json')

    def client(self):
        """Get new client (helper)
        """
        cl = Client()
        cl.request_timeout = 0.1
        return cl

    def get(self, sessionid: str) -> Client:
        """Get client settings
        """
        key = parse.unquote(sessionid.strip(" \""))
        try:
            settings = json.loads(self.db.search(Query().sessionid == key)[0]['settings'])
            cl = Client()
            cl.set_settings(settings)
            cl.get_timeline_feed()
            return cl
        except IndexError:
            raise Exception('Session not found (e.g. after reload process), please relogin')

    def set(self, cl: Client) -> bool:
        """Set client settings
        """
        key = parse.unquote(cl.sessionid.strip(" \""))
        self.db.insert({'sessionid': key, 'settings': json.dumps(cl.get_settings())})
        return True

    def close(self):
        pass
