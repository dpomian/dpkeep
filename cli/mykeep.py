#!/usr/local/bin/python3

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json
import argparse
import clipboard
import functools
from engine import utils
from engine import storage as st
from engine import crypto as cry
from engine import model
from engine import pwd_utils

netrcfile = ''
storagefile = ''

def stop_on_exception(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            func(args[0])
        except ValueError as e:
            print(e)
            exit(1)
    return wrapped


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


@stop_on_exception
def add_entry(args):
    crypto = None
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)
    pwd = pwd_utils.generate_pwd() if args.pwd=='random' else args.pwd
    try:
        model.Model().add_entry(data_dict, name=args.name, link=args.link, pwd=pwd, tags=args.tags)
    except ValueError as e:
        print(e)
        exit(1)

    recrypted = crypto.encrypt(json.dumps(data_dict))
    storage.write(recrypted)


@stop_on_exception
def list_all(args):
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)
    for key in sorted(data_dict.keys()):
        print(_format_entry(data_dict, key))


@stop_on_exception
def cp_pwd(args):
    if not args.name:
        return
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)

    clipboard.copy(data_dict[args.name]['pwd']) if args.name in data_dict else clipboard.copy('')


@stop_on_exception
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
    _replace_in_file('../res/prd/.mig_netrc', tmp)


@stop_on_exception
def update_entry(args):
    crypto = cry.Crypto(utils.get_password(netrcfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)
    data_dict = model.Model().update_entry(data_dict, name=args.name, link=args.link, pwd=args.pwd, tags=args.tags)
    storage.write(crypto.encrypt(json.dumps(data_dict)))


def generate_random_password(args):
    print('pwd: {}'.format(pwd_utils.generate_pwd()))


def parse_args(myargs):
    global netrcfile, storagefile
    netrcfile = os.environ['DPKEEP_NETRC'] if 'DPKEEP_NETRC' in os.environ else ''
    storagefile = os.environ['DPKEEP_STORAGE'] if 'DPKEEP_STORAGE' in os.environ else ''
    
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

    args = parser.parse_args(myargs)
    if hasattr(args, 'func'):
        args.func(args)


def main():
    os.environ['DPKEEP_NETRC'] = os.path.join(os.path.dirname(__file__),'../res/prd/.netrc')
    os.environ['DPKEEP_STORAGE'] = os.path.join(os.path.dirname(__file__),'../res/prd/.mykeep_storage')

    parse_args(sys.argv[1:])

    return None


if __name__ == "__main__":
    main()

