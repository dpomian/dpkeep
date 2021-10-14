import os
import sys
import unittest
import getpass
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cli
import engine

class TestCli(unittest.TestCase):
    @patch("getpass.getpass", side_effect=['abc','def'])
    @patch("cli.mykeep.chng_pwd", return_value=None)
    @patch('engine.utils.read_config', return_value={'mpwd':'abc','salt':'asalt'})
    def test_change_password_interactive(self, mock_getpass, chng_pwd, config_mock):
        parser = cli.mykeep.get_argparser()
        iargs = ['chng']
        pargs = parser.parse_args(iargs)

        try:
            if hasattr(pargs, 'func'):
                pargs.func(pargs)
        except ValueError as v:
            self.fail(f'Unexpected exception raised!: {v}')


    @patch('engine.utils.read_config', return_value={'mpwd': 'ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f','salt': 'e1a22653db140ba9df9f63d48989228a6dd37c65bac850ab07dddf7773c13538'})
    @patch('engine.storage.Storage.read', return_value=b'gAAAAABhaFvMaTNDlL4ZMIrknhkjpAzrO8u_CdxnycvARZeyEdO0JFmQF7J-PqX2zXBI_HIgfXzG6Fz7AeAjots7cXG4v7klaaxjMFNrVkod3sejBCQCA9yHSe3OJe1A1VjRtDgeH4qLNLlNjzuBV0vNlLLCB16GgQ==')
    @patch('engine.pwd_utils.generate_salt', return_value=b'\x055\xde\x022\x83\x92\xc3\x80?l\xd0\x14\x15`\x0b\xc678\xa1\x9d:\xba\x02\xd9&\xc2\xf6\xc6V\xbb\x00')
    @patch('engine.storage.Storage.write', return_value=None)
    @patch('cli.mykeep._update_config', return_value=None)
    def test_change_pwd(self, config_mock, storage_read_mock, gen_salt_mock, storage_write_mock, upd_config_mock):
        cli.mykeep.chng_pwd('abc', 'def')

        engine.utils.read_config.assert_called_once()
        engine.storage.Storage.write.assert_called_once()
        cli.mykeep._update_config.assert_called_once()


    @patch('engine.utils.read_config', return_value={'mpwd': 'ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f','salt': 'e1a22653db140ba9df9f63d48989228a6dd37c65bac850ab07dddf7773c13538'})
    @patch('engine.storage.Storage.read', return_value=b'gAAAAABhaFvMaTNDlL4ZMIrknhkjpAzrO8u_CdxnycvARZeyEdO0JFmQF7J-PqX2zXBI_HIgfXzG6Fz7AeAjots7cXG4v7klaaxjMFNrVkod3sejBCQCA9yHSe3OJe1A1VjRtDgeH4qLNLlNjzuBV0vNlLLCB16GgQ==')
    @patch('engine.pwd_utils.generate_salt', return_value=b'\x055\xde\x022\x83\x92\xc3\x80?l\xd0\x14\x15`\x0b\xc678\xa1\x9d:\xba\x02\xd9&\xc2\xf6\xc6V\xbb\x00')
    @patch('engine.storage.Storage.write', side_effect=OSError)
    @patch('cli.mykeep._update_config', return_value=None)
    def test_change_pwd_storage_fail(self, config_mock, storage_read_mock, gen_salt_mock, storage_write_mock, upd_config_mock):
        cli.mykeep.chng_pwd('abc', 'def')

        engine.utils.read_config.assert_called_once()
        engine.storage.Storage.write.assert_called_once()
        cli.mykeep._update_config.assert_not_called()


    @patch('engine.utils.read_config', return_value={'mpwd':'def','salt':'asalt'})
    def test_validate_password_invalid_password(self, config_mock):
        old_pwd = 'abc'
        with self.assertRaises(ValueError):
            cli.mykeep.validate_password(old_pwd)
        

    @patch('engine.utils.read_config', return_value={'mpwd':'def','salt':'asalt'})
    def test_validate_password_valid_password(self, config_mock):
        old_pwd = 'def'
        try:
            cli.mykeep.validate_password(old_pwd)
        except ValueError:
            self.fail("validate_password() raised an unexpected exception!")
