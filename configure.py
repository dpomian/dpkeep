import subprocess
import getpass
import unittest
import hashlib
import json
import os
from engine import crypto
from engine import utils
from engine import pwd_utils


def _run_generic_setup():
    print(subprocess.run('source ./configure.sh'))


def _generate_config_file():
    mpwd = getpass.getpass(prompt='Pick a master password: ')
    print("\n/!\\ DON'T LOSE YOUR MASTER PASSWORD!! /!\\")
    config = utils.build_config(mpwd, pwd_utils.generate_salt())
    configfile = './res/prd/.config'
    with open(configfile, 'w') as ofile:
        ofile.write(json.dumps(config))
    os.chmod(configfile, 0o400)


def main():
    _run_generic_setup()
    _generate_config_file()
    print('you can now run ./runweb.sh to start the webserver')


if __name__ == '__main__':
    main()


