from py_logger.py_logger import PyLogger
from py_logger.py_syslog_handler import PySysLogHandler
import unittest
import os
from mock import Mock
from mock import patch
from freezegun import freeze_time
import logging
import socket



class PyLogger_test(unittest.TestCase):
  def setUp(self):
    self.freezer = freeze_time("2017-05-20 03:21:34")
    self.freezer.start()
    self.expected_host_name = os.getenv('HOSTNAME')
    self.expected_format = " %%(asctime)s %s app %%(message)s" % self.expected_host_name

  def tearDown(self):
    PyLogger.pyLoggers = {}
    self.freezer.stop()

  def start_patches(self, patches_dict):
    # Start patches
    for p in patches_dict:
        patches_dict[p].start()

  def stop_patches(self, patches_dict):
    # Start patches
    for p in patches_dict:
        patches_dict[p].stop()

  def test_get_stdout_logger(self):
    expected_message = 'testing stdout logger'

    patches_dict = {}
    basic_config_mock = Mock()
    patches_dict['basic_config_patch'] = patch('logging.basicConfig', basic_config_mock)
    #   getLogger
    logger_mock = Mock()
    get_logger_mock = Mock(return_value=logger_mock)
    patches_dict['get_logger_patch'] = patch('logging.getLogger', get_logger_mock)

    # start patches
    self.start_patches(patches_dict)

    # call method
    logger = PyLogger.getLogger('stdout', 'app')
    logger.info('testing stdout logger')

    # make sure things happened
    basic_config_mock.assert_called_once_with(format=self.expected_format, level=logging.INFO)
    logger_mock.info.assert_called_once_with(expected_message)
    get_logger_mock.assert_called_once

    # stop patches
    self.stop_patches(patches_dict)

  def test_get_tcp_logger(self):
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
    add_handler_mock.assert_called
    connect_mock.assert_called_once

    # stop patches
    self.stop_patches(patches_dict)

  def test_get_tcp_logger_handler(self):
    # mock
    # py_syslog_handler
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
    logger = PyLogger.getLogger('tcp', 'app')

    # assert stuff
    py_syslog_handler_mock.assert_called_once

    # stop patch
    py_syslog_handler_patch.stop()
    connect_patch.stop()

  def test_tcp_socket_send(self):
    expected_message = "<14> 2017-05-20 03:21:34,000 %s app testing tcp socket send\n" % self.expected_host_name

    # mock
    socket_mock = Mock()
    socket_constructor_mock = Mock(return_value=socket_mock)
    socket_patch = patch('socket.socket', socket_constructor_mock)

    # patch
    socket_patch.start()

    # do stuff
    logger = PyLogger.getLogger('tcp', 'app')
    logger.info('testing tcp socket send')

    # make sure stuff happened
    socket_mock.sendall.assert_called_once_with(expected_message)

    # stop patch
    socket_patch.stop()


if __name__ == '__main__':
    unittest.main()
