import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes

class Crypto:
    def __init__(self, config):
        self._config = config

    def _get_key(self):
        key = SHA512.new(self._config.pwd).digest().upper()[:16]
        return key

    def encrypt(self, data):
        if type(data) == str:
            data = data.encode()

        cipher = AES.new(self._get_key(), AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        # print(f'nonce: {cipher.nonce}, tag: {tag}, ciphertext: {ciphertext}')
        return cipher.nonce + tag + ciphertext

    def decrypt(self, encrypted):
        if encrypted is None:
            return None
        key = self._get_key()
        nonce, tag, ciphertext = encrypted[:16], encrypted[16:32], encrypted[32:]
        # print(f'nonce: {nonce}, tag: {tag}, ciphertext: {ciphertext}')
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)

