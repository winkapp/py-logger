from py_logger.py_logger import PyLogger
from py_logger.py_syslog_handler import PySysLogHandler
import unittest
import os
from mock import Mock
from mock import patch
import logging
import socket

class PyLogger_test(unittest.TestCase):
  def setUp(self):
    os.environ['SYSLOG_HOST'] = 'logger'
    os.environ['SYSLOG_PORT'] = '514'
    self.test_py_logger = PyLogger.getPyLogger()
    self.test_py_logger.setLevel(logging.DEBUG)
    expected_host_name = os.getenv('HOSTNAME')
    self.expected_format = "%%(asctime)s %s app %%(message)s" % expected_host_name

  def tearDown(self):
    # Remove any handlers after each test
    map(self.test_py_logger.removeHandler, self.test_py_logger.handlers)

  def start_patches(self, patches_dict):
    # Start patches
    for p in patches_dict:
        patches_dict[p].start()

  def stop_patches(self, patches_dict):
    # Start patches
    for p in patches_dict:
        patches_dict[p].stop()

  def test_get_stdout_logger(self):
    expected_message = 'Logging configured'

    patches_dict = {}
    basic_config_mock = Mock()
    patches_dict['basic_config_patch'] = patch('logging.basicConfig', basic_config_mock)
    #   getLogger
    get_logger_mock = Mock()
    patches_dict['get_logger_patch'] = patch('logging.getLogger', get_logger_mock)
    #   info
    info_mock = Mock()
    patches_dict['info_patch'] = patch('logging.info', info_mock)

    # start patches
    self.start_patches(patches_dict)

    # call method
    PyLogger.getLogger('stdout', 'app')

    # make sure things happened
    basic_config_mock.assert_called_once_with(format=self.expected_format, level=logging.INFO)
    info_mock.assert_called_once_with(expected_message)
    get_logger_mock.assert_called_once

    # stop patches
    self.stop_patches(patches_dict)

  def test_get_tcp_logger(self):
    expected_message = ''

    patches_dict = {}
    #   info
    info_mock = Mock()
    patches_dict['info_patch'] = patch('logging.info', info_mock)
    #   addHandler
    add_handler_mock = Mock()
    patches_dict['add_handler_patch'] = patch('logging.Logger.addHandler', add_handler_mock)

    #   setLevel
    set_level_mock = Mock()
    patches_dict['set_level_patch'] = patch('py_logger.py_syslog_handler.PySysLogHandler.setLevel', set_level_mock)
    #   setFormatter
    set_formater_mock = Mock()
    patches_dict['set_formater_patch'] = patch('py_logger.py_syslog_handler.PySysLogHandler.setFormatter', set_formater_mock)
    #   emit
    emit_mock = Mock()
    patches_dict['emit_patch'] = patch('py_logger.py_syslog_handler.PySysLogHandler.emit', emit_mock)
    #   connect
    connect_mock = Mock()
    socket_class_mock = Mock(return_value=connect_mock)
    patches_dict['connect_patch'] = patch('socket.socket', socket_class_mock)

    # start patches
    self.start_patches(patches_dict)

    # call method
    PyLogger.getLogger('tcp', 'app')

    # make sure things happened
    set_level_mock.assert_called_once_with(logging.INFO)
    set_formater_mock.assert_called_once_with(logging.Formater(self.expected_format))
    pysyslog_handler_mock.assert_called_once_with(('test_host', '545'),
                                                   sockettype=socket.SOCK_STREAM,
                                                   terminator= '\n')
    add_handler_mock.assert_called_once_with('')
    connect_mock.assert_called_once_with('')

    # stop patches
    self.start_patches(patches_dict)

    os.environ['SYSLOG_HOST'] = None
    os.environ['SYSLOG_PORT'] = None

if __name__ == '__main__':
    unittest.main()
