import os
import sys
import unittest

from engine import model

class TestModel(unittest.TestCase):
    def test_add_entry(self):
        m = model.Model()
        data_dict = {}
        expected = {
                'abc': {'link': 'https://domain.com', 'pwd': 'mypwd'},
                'bcd': {'link': 'https://b.com', 'pwd':'bpwd', 'uname':'b@domain.com'}
                }

        data_dict = m.add_entry(data_dict, name="abc", link="https://domain.com", pwd="mypwd")
        data_dict = m.add_entry(data_dict, name="bcd", link="https://b.com", pwd="bpwd", uname='b@domain.com')

        self.assertEqual(expected, data_dict)


    def test_update_entry(self):
        m = model.Model()
        data_dict = {
                'abc': {'link': 'https://domain.com', 'pwd': 'mypwd'}
                }
        expected = {
                'abc': {'link': 'https://a.com', 'pwd': 'apwd', 'uname':'a@a.com'}
                }
        data_dict = m.update_entry(data_dict, name='abc', link='https://a.com', pwd='apwd', uname='a@a.com')

        self.assertEqual(expected, data_dict)

