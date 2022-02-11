import os


class Storage:
    def __init__(self, filename):
        self._fname = filename

    def read(self):
        if not os.path.isfile(self._fname):
            return None

        with open(self._fname, "rb") as myfile:
            data = myfile.read()
            return data

        return None

    def write(self, data):
        with open(self._fname, 'wb') as ofile:
            ofile.write(data)
