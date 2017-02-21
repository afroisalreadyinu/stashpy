import unittest
from unittest import mock
import stashpy.main

class InitTests(unittest.TestCase):

    @mock.patch('stashpy.main.read_config')
    def test_error_on_no_spec_config(self, mock_read_config):
        config = {'tcp_config': {'host': 'localhost', 'port': 1234}}
        mock_read_config.return_value = config
        with self.assertRaises(AssertionError):
            stashpy.main.run()

    @mock.patch('stashpy.main.read_config')
    def test_error_on_no_app_config(self, mock_read_config):
        config = {'processor_spec': {}}
        mock_read_config.return_value = config
        with self.assertRaises(AssertionError):
            stashpy.main.run()


    @mock.patch('stashpy.main.read_config')
    def test_error_on_two_app_configs(self, mock_read_config):
        config = {'processor_spec': {},
                  'tcp_config': {'host': 'localhost', 'port': 1234},
                  'queue_config': {'host': 'localhost', 'port':1234}}
        mock_read_config.return_value = config
        with self.assertRaises(AssertionError):
            stashpy.main.run()
