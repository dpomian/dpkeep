import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from engine import crypto
from engine import utils
from engine import pwd_utils

class TestCrypto(unittest.TestCase):
    def test_generate_salt(self):
      salt_len = 64
      salt = pwd_utils.generate_salt(salt_len)
      self.assertTrue(type(salt) == bytes)
      self.assertEqual(len(salt), salt_len)
    
    def test_encrypt_decrypt(self):
      config = utils.build_config('my pwd', pwd_utils.generate_salt())
      cry = crypto.Crypto(config)
      data = 'text to be encrypted'
      encrypted = cry.encrypt(data)
      decrypted = cry.decrypt(encrypted).decode('utf-8')
      self.assertEqual(data, decrypted)

    def test_invalid_config(self):
      with self.assertRaises(ValueError):
        config = utils.build_config('', 'salt')
        cry = crypto.Crypto(config)

