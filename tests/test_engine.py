import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from engine import model
from engine import utils
from engine import crypto as cry

class TestEngine(unittest.TestCase):
    def setUp(self):
        self.netrcfile = os.path.join(os.path.dirname(__file__),'./res/.netrc')

    def test_read_pwd(self):
        expected = b"test password"
        actual = utils.get_password(self.netrcfile)
        self.assertEqual(expected, actual)

    def test_encrypt(self):
        pwd = utils.get_password(self.netrcfile)
        crypto = cry.Crypto(pwd)
        encrypted = crypto.encrypt("abcdef")
        decrypted = crypto.decrypt(encrypted)
        self.assertEqual(b"abcdef", decrypted)

    def test_add_entry_invalid_name(self):
        existing = {'l1': {'link':'google.com', 'tags':'t1,t2'}}
        with self.assertRaises(ValueError):
            model.Model().add_entry(existing, name='123!', link='abc.com', pwd='secretpwd')

    def test_add_entry_already_existing(self):
        existing = {'l1': {'link':'google.com', 'tags':'t1,t2'}}
        with self.assertRaises(ValueError):
            model.Model().add_entry(existing, name='l1', link='abc.com', pwd='secretpwd')

    def test_add_entry_success(self):
        existing = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        expected = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'},'l2': {'link':'http://google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        self.assertDictEqual(expected, model.Model().add_entry(existing, name='l2', link='google.com', pwd='secretpwd', tags='t1,t2'))

    def test_remove_entry_inexisting_name(self):
        existing = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        expected = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        actual = model.Model().remove_entry(existing, 'l2')
        self.assertDictEqual(expected, actual)

    def test_remove_entry_success(self):
        existing = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        expected = {}
        actual = model.Model().remove_entry(existing, 'l1')
        self.assertDictEqual(expected, actual)

    def test_update_inexisting_name(self):
        existing = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        expected = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        actual = model.Model().update_entry(existing, name='l2', pwd='abc', tags='tt')
        self.assertDictEqual(expected, actual)

    def test_update_link(self):
        existing = {'l1': {'link':'gooogle.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        expected = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        actual = model.Model().update_entry(existing, name='l1', link='google.com', pwd='')
        self.assertDictEqual(expected, actual)

    def test_update_pwd(self):
        existing = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        expected = {'l1': {'link':'google.com', 'pwd':'secret2', 'tags':'t1,t2'}}
        actual = model.Model().update_entry(existing, name='l1', pwd='secret2')
        self.assertDictEqual(expected, actual)

    def test_update_tags(self):
        existing = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        expected = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t3'}}
        actual = model.Model().update_entry(existing, name='l1', tags='t3')
        self.assertDictEqual(expected, actual)

    def test_update_all_attributes(self):
        existing = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
        expected = {'l1': {'link':'amazon.com', 'pwd':'secret1', 'tags':'t3'}}
        actual = model.Model().update_entry(existing, link='amazon.com', pwd='secret1', name='l1', tags='t3')
        self.assertDictEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
