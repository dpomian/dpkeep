import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Crypto:
    def __init__(self, pwd):
        if type(pwd) == str:
            pwd = pwd.encode()

        self._pwd = pwd

    def _get_salt(self):
        return b"F\x12D\x9a\xe9})\xa0\n\x07\x90'\xff|\xd6\x8c\xf4\xae\xa0C\xd8\x8bq!\x08\xa8\x0c\xf5\xbf\xf5F\xa5"

    def _get_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._get_salt(),
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self._pwd))
        return key


    def encrypt(self, data):
        if type(data) == str:
            data = data.encode()
        key = self._get_key()
        f = Fernet(key)

        return f.encrypt(data)

    def decrypt(self, encrypted):
        if encrypted:
            key = self._get_key()
            f = Fernet(key)
            return f.decrypt(encrypted)

        return None
