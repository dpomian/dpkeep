import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os


class Crypto:
    def __init__(self, config):
        if 'mpwd' not in config or 'salt' not in config:
            raise ValueError('Invalid config')
        self._config = config

    def _get_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=bytes.fromhex(self._config['salt']),
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(bytes.fromhex(self._config['mpwd'])))
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
