import os
import re
import hashlib
import json

def get_password(filename):
    with open(filename, "rb") as ifile:
        data = ifile.read().splitlines()
        if len(data) == 0:
            raise ValueError("your password ain't good")
    return data[0]


def read_config(filename):
    data = ''
    with open(filename, 'r') as ifile:
        data = ifile.readlines()
    return json.loads(''.join(data))


def build_config(i_mpwd, i_salt):
    return {'mpwd':hashlib.sha512(i_mpwd.encode('utf-8')).hexdigest(), 'salt':i_salt.hex()}

