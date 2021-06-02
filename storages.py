from urllib import parse
from instagrapi import Client


class ClientStorage:
    storage = {}

    def client(self):
        """Get new client (helper)
        """
        cl = Client()
        cl.request_timeout = 0.1
        return cl

    def get(self, sessionid: str) -> Client:
        """Get client settings
        """
        key = parse.unquote(sessionid.strip())
        try:
            return self.storage[key]
        except KeyError:
            raise Exception('Session not found (e.g. after reload process), please relogin')

    def set(self, cl: Client) -> bool:
        """Set client settings
        """
        key = parse.unquote(cl.sessionid)
        self.storage[key] = cl
        return True

    def close(self):
        self.storage = {}