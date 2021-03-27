import subprocess
import getpass
import unittest
import hashlib
import json
import os
from engine import crypto
from engine import utils


def _run_generic_setup():
    print(subprocess.run('./configure.sh'))


def _generate_config_file():
    mpwd = hashlib.sha512(getpass.getpass(prompt='Pick a master password: ').encode('utf-8')).hexdigest()
    config = utils.build_config(mpwd, crypto.Crypto.generate_salt())
    configfile = './res/prd/.config'
    with open(configfile, 'w') as ofile:
        ofile.write(json.dumps(config))
    os.chmod(configfile, 0o400)


def main():
    _run_generic_setup()
    _generate_config_file()


if __name__ == '__main__':
    main()


