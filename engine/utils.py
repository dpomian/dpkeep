import os
import re

def get_password(filename):
    with open(filename, "rb") as ifile:
        data = ifile.read().splitlines()
        if len(data) == 0:
            raise ValueError("your password ain't good")
    return data[0]

