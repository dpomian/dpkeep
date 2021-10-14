import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from engine import utils
from engine import crypto
from engine import pwd_utils

class TestUtils(unittest.TestCase):
    def test_build_config(self):
        mpwd = 'secret pwd'
        asalt = pwd_utils.generate_salt(32)
        actual = utils.build_config(mpwd, asalt)
        self.assertTrue('mpwd' in actual)
        self.assertTrue('salt' in actual)
        self.assertEqual(32, len(bytes.fromhex(actual['salt'])))

    def test_change_pwd(self):
        old_pwd = "abcd"
        old_salt = pwd_utils.generate_salt(32)
        old_config = utils.build_config(old_pwd, old_salt)
        old_data = "current data"

        old_encryptor = crypto.Crypto(old_config)
        old_encrypted_data = old_encryptor.encrypt(old_data)
        
        new_pwd = "1234"
        new_salt = pwd_utils.generate_salt(32)
        new_config = utils.build_config(new_pwd, new_salt)
