class Config:
    def __init__(self, pwd, salt):
        if pwd is None or not pwd:
            raise ValueError('Invalid config')

        self.pwd = self._encode_bin(pwd)
        self.salt = self._encode_bin(salt)

    def _encode_bin(self, item):
        if type(item) == str:
            item = item.encode()
        return item
