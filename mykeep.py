#!/usr/local/bin/python3

import os
import sys
import unittest
import json
import argparse
import clipboard
from engine import utils
from engine import storage as st
from engine import crypto as cry
from engine import model
from engine import pwd_utils

# STORAGE = "{}/.dpkeep".format(os.path.expanduser("~"))
netrcfile = ''
storagefile = ''

def mp(text, var):
    print('{}: {}'.format(text, var))

def _format_entry(data_dict, key):
    tags = ''
    if "tags" in data_dict[key]:
        tags = data_dict[key]["tags"]
    return '{} |{}| -> {}'.format(key.ljust(15), tags.ljust(20), data_dict[key]["link"])


def _get_decrypted_dict(crypto, storage):
    result = {}
    encrypted = storage.read()

    if encrypted:
        try:
            decrypted = crypto.decrypt(encrypted)
        except cryptography.fernet.InvalidToken:
            print("your password ain't good")
            return result
        result = json.loads(decrypted)

    return result


def add_entry(args):
    crypto = None
    try:
        crypto = cry.Crypto(utils.get_password(netrcfile))
    except ValueError as e:
        print(e)
        exit(1)
    storage = st.Storage(storagefile)

    data_dict = _get_decrypted_dict(crypto, storage)

    try:
        model.Model().add_entry(data_dict, name=args.name, link=args.link, pwd=args.pwd, tags=args.tags)
    except ValueError as e:
        print(e)
        exit(1)

    recrypted = crypto.encrypt(json.dumps(data_dict))
    storage.write(recrypted)


def list_all(args):
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)
    for key in sorted(data_dict.keys()):
        print(_format_entry(data_dict, key))


def cp_pwd(args):
    if not args.name:
        return
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)

    clipboard.copy(data_dict[args.name]['pwd']) if args.name in data_dict else clipboard.copy('')


def remove_entry(args):
    if not args.name:
        return
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)
    model.Model().remove_entry(data_dict, args.name)

    storage.write(crypto.encrypt(json.dumps(data_dict)))


def _replace_in_file(filename, lines):
    os.remove(filename)
    with open(filename, 'wb') as ofile:
        for line in lines:
            ofile.write(line)
    os.chmod(filename, 0o400)


def chng_pwd(args):
    if not args.netrc or not os.path.exists(args.netrc):
        return

    with open(args.netrc, 'r') as ifile:
        data = []
        for line in ifile:
            if '\n' in line:
                line = line.replace('\n','')
            data.append(line)

    if len(data) != 2:
        return
    if data[0].find('current:') != 0:
        return
    if data[1].find('new:') != 0:
        return
    c_pwd = data[0][len('current:'):]
    n_pwd = data[1][len('new:'):]

    decryptor = cry.Crypto(c_pwd)
    storage = st.Storage(storagefile)
    try:
        decrypted = decryptor.decrypt(storage.read())
    except cryptography.fernet.InvalidToken as e:
        print("your password ain't good")
        exit(1)

    encryptor = cry.Crypto(n_pwd)
    storage.write(encryptor.encrypt(decrypted))

    tmp = [n_pwd.encode()]
    _replace_in_file(netrcfile, tmp)

    tmp = ['current:{}\n'.format(n_pwd).encode(), 'new:{}'.format(n_pwd).encode()]
    _replace_in_file('./res/prd/.mig_netrc', tmp)


def update_entry(args):
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)
    data_dict = model.Model().update_entry(data_dict, name=args.name, link=args.link, pwd=args.pwd, tags=args.tags)
    storage.write(crypto.encrypt(json.dumps(data_dict)))


def generate_random_password(args):
    print('pwd: {}'.format(pwd_utils.generate_pwd()))


def main():
    global netrcfile, storagefile
    netrcfile = os.path.join(os.path.dirname(__file__),'res/prd/.netrc')
    storagefile = os.path.join(os.path.dirname(__file__),'res/prd/.mykeep_storage')

    parser = argparse.ArgumentParser(description="Password keepr", prog="mykeep", allow_abbrev=True)

    subparsers = parser.add_subparsers(help='commands')

    add_parser = subparsers.add_parser('add', help='add a new ink')
    add_parser.add_argument("-name", help="fast link name", required=True)
    add_parser.add_argument("-link", help="actual link. Must be surrounded by quotes", required=True)
    add_parser.add_argument("-pwd", help="password. Must be surrounded by quotes", required=True)
    add_parser.add_argument("-tags", help="add comma separated tags")
    add_parser.set_defaults(func=add_entry)

    list_parser = subparsers.add_parser('ll', help='list all')
    list_parser.set_defaults(func=list_all)

    cp_parser = subparsers.add_parser('cp', help='copy pwd to clipboard')
    cp_parser.add_argument("name", help="name")
    cp_parser.set_defaults(func=cp_pwd)

    rm_parser = subparsers.add_parser('rm', help="remove entry")
    rm_parser.add_argument("name", help="name to be removed")
    rm_parser.set_defaults(func=remove_entry)

    up_parser = subparsers.add_parser('up', help='update link, pwd or tags')
    up_parser.add_argument('name', help='name for which the update is wanted')
    up_parser.add_argument('-link', help='update link')
    up_parser.add_argument('-pwd', help='update pwd')
    up_parser.add_argument('-tags', help='update tags')
    up_parser.set_defaults(func=update_entry)

    chng_parser = subparsers.add_parser('chng', help="change password")
    chng_parser.add_argument("netrc", help="netrc file for change password")
    chng_parser.set_defaults(func=chng_pwd)

    gen_parser = subparsers.add_parser('genpwd', help="generates a random password")
    gen_parser.set_defaults(func=generate_random_password)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)

    return None


if __name__ == "__main__":
    main()


class MyKeepTest(unittest.TestCase):
    def test_read_pwd(self):
        expected = b"test password"
        actual = utils.get_password("./res/test/.netrc")
        self.assertEqual(expected, actual)

    def test_encrypt(self):
        pwd = utils.get_password("./res/test/.netrc")
        crypto = cry.Crypto(pwd)
        expected = "aaa"
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
        expected = {'l1': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'},'l2': {'link':'google.com', 'pwd':'secretpwd', 'tags':'t1,t2'}}
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
        actual = model.Model().update_entry(existing, name='l1', link='google.com')
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

