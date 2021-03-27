import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from engine import crypto
from engine import utils

class TestCrypto(unittest.TestCase):
    def test_generate_salt(self):
        salt_len = 64
        salt = crypto.Crypto.generate_salt(salt_len)
        self.assertTrue(type(salt) == bytes)
        self.assertEqual(len(salt), salt_len)
    
    def test_encrypt_decrypt(self):
        config = utils.build_config('my pwd', crypto.Crypto.generate_salt())
        cry = crypto.Crypto(config)
        data = 'text to be encrypted'
        encrypted = cry.encrypt(data)
        decrypted = cry.decrypt(encrypted).decode('utf-8')
        self.assertEqual(data, decrypted)

    def test_invalid_config(self):
        config = {}
        with self.assertRaises(ValueError):
            cry = crypto.Crypto(config)
