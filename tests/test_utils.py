import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from engine import utils
from engine import crypto

class TestConfigure(unittest.TestCase):
    def test_build_config(self):
        mpwd = 'secret pwd'
        asalt = crypto.Crypto.generate_salt(32)
        actual = utils.build_config(mpwd, asalt)
        self.assertTrue('mpwd' in actual)
        self.assertTrue('salt' in actual)
        self.assertEqual(32, len(bytes.fromhex(actual['salt'])))
