import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import hashlib
import json
from engine.config import Config

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
    json_data = json.loads(''.join(data))
    return Config(json_data['mpwd'], json_data['msalt'])


def build_config(i_mpwd, i_salt):
    return Config(i_mpwd, i_salt)

