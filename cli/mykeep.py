#!/usr/local/bin/python3

import os
import sys
import getpass

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
configfile = ''

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


def _update_config(config):
    pass


def add_entry(args, data_dict):
    pwd = pwd_utils.generate_pwd() if args.pwd=='random' else args.pwd
    try:
        data_dict = model.Model().add_entry(data_dict, name=args.name, link=args.link, pwd=pwd, tags=args.tags, uname=args.uname)
    except ValueError as e:
        print(e)
        exit(1)
    return data_dict


@stop_on_exception
def add_entry_cli(args):
    crypto = cry.Crypto(utils.read_config(configfile))
    storage = st.Storage(storagefile)
    data_dict = add_entry(args, _get_decrypted_dict(crypto, storage))
    recrypted = crypto.encrypt(json.dumps(data_dict))
    storage.write(recrypted)


@stop_on_exception
def list_all(args):
    crypto = cry.Crypto(utils.read_config(configfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)
    print(data_dict)
    for key in sorted(data_dict.keys()):
        print(_format_entry(data_dict, key))


@stop_on_exception
def cp_pwd(args):
    if not args.name:
        return
    crypto = cry.Crypto(utils.read_config(configfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)

    clipboard.copy(data_dict[args.name]['pwd']) if args.name in data_dict else clipboard.copy('')


@stop_on_exception
def remove_entry(args):
    if not args.name:
        return
    crypto = cry.Crypto(utils.read_config(configfile))
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


def validate_password(pwd):
    config = utils.read_config(configfile)
    if config['mpwd'] != pwd:
        raise ValueError('Invalid password')


def change_password_interactive(args):
    old_pwd = getpass.getpass('Old password: ')
    new_pwd = getpass.getpass('New password: ')
    validate_password(old_pwd)
    chng_pwd(old_pwd, new_pwd)


def chng_pwd(old_pwd, new_pwd):
    old_config = utils.read_config(configfile)
    crypto = cry.Crypto(old_config)
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)

    new_salt = pwd_utils.generate_salt()
    new_config = utils.build_config(new_pwd, new_salt)
    new_crypto = cry.Crypto(new_config)

    try:
        storage.write(new_crypto.encrypt(json.dumps(data_dict)))
    except OSError:
        return

    _update_config(new_config)


@stop_on_exception
def update_entry(args):
    crypto = cry.Crypto(utils.read_config(configfile))
    storage = st.Storage(storagefile)
    data_dict = _get_decrypted_dict(crypto, storage)
    data_dict = model.Model().update_entry(data_dict, name=args.name, link=args.link, pwd=args.pwd, tags=args.tags)
    storage.write(crypto.encrypt(json.dumps(data_dict)))


def generate_random_password(args):
    print('pwd: {}'.format(pwd_utils.generate_pwd()))


def get_argparser():
    parser = argparse.ArgumentParser(description="Password keepr", prog="mykeep", allow_abbrev=True)

    subparsers = parser.add_subparsers(help='commands')

    add_parser = subparsers.add_parser('add', help='add a new ink')
    add_parser.add_argument("-name", help="fast link name", required=True)
    add_parser.add_argument("-link", help="actual link. Must be surrounded by quotes", required=True)
    add_parser.add_argument("-pwd", help="password. Must be surrounded by quotes", required=True)
    add_parser.add_argument("-tags", help="add comma separated tags")
    add_parser.add_argument("-uname", help="username")
    add_parser.set_defaults(func=add_entry_cli)

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
    chng_parser.set_defaults(func=change_password_interactive)

    gen_parser = subparsers.add_parser('genpwd', help="generates a random password")
    gen_parser.set_defaults(func=generate_random_password)

    return parser


def parse_args(myargs):
    global storagefile, configfile
    storagefile = os.environ['DPKEEP_STORAGE'] if 'DPKEEP_STORAGE' in os.environ else ''
    configfile = os.environ['DPKEEP_CONFIG'] if 'DPKEEP_CONFIG' in os.environ else ''

    parser = get_argparser()

    args = parser.parse_args(myargs)
    if hasattr(args, 'func'):
        args.func(args)


def main():
    os.environ['DPKEEP_STORAGE'] = os.path.join(os.path.dirname(__file__),'../res/prd/.mykeep_storage')
    os.environ['DPKEEP_CONFIG'] = os.path.join(os.path.dirname(__file__),'../res/prd/.config')

    parse_args(sys.argv[1:])

    return None


if __name__ == "__main__":
    main()

