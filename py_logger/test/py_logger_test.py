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
    expected_host_name = os.getenv('HOSTNAME')
    self.expected_format = "%%(asctime)s %s app %%(message)s" % expected_host_name

  def tearDown(self):
    print logging.handlers
    logger = PyLogger.getLogger('stdout', 'app')
    print logger.handlers
    # Remove any handlers after each test
    map(logger.removeHandler, logger.handlers)

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
    #   logging.formatter
    formatter_mock = Mock()
    patches_dict['formatter_patch'] = patch('logging.Formatter', formatter_mock)
    #   setFormatter
    set_formatter_mock = Mock()
    set_formatter_class_mock = Mock(set_formatter_mock)
    patches_dict['set_formatter_patch'] = patch('py_logger.py_syslog_handler.PySysLogHandler.setFormatter', set_formatter_class_mock)
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
    formatter_mock.assert_called_once_with(self.expected_format, None)
    set_formatter_class_mock.assert_called_once
    add_handler_mock.assert_called
    connect_mock.assert_called_once

    # stop patches
    self.stop_patches(patches_dict)

  def test_get_tcp_logger_handler(self):
    # py_syslog_handler
    # mock
    py_syslog_handler_mock = Mock()
    py_syslog_handler_class_mock = Mock(return_value=py_syslog_handler_mock)
    py_syslog_handler_patch = patch('py_logger.py_syslog_handler.PySysLogHandler', py_syslog_handler_class_mock)

    # connect
    connect_mock = Mock()
    socket_class_mock = Mock(return_value=connect_mock)
    connect_patch = patch('socket.socket', socket_class_mock)

    # patch
    py_syslog_handler_patch.start()
    connect_patch.start()

    # do stuff
    PyLogger.getLogger('tcp', 'app')

    # assert stuff
    py_syslog_handler_mock.assert_called_once

    # stop patch
    py_syslog_handler_patch.stop()
    connect_patch.stop()


if __name__ == '__main__':
    unittest.main()
