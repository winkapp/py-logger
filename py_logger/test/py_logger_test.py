from py_logger.py_logger import PyLogger
from py_logger.py_syslog_handler import PySysLogHandler
import unittest
from mock import Mock
from mock import patch
import logging

class PyLogger_test(unittest.TestCase):
  def setUp(self):
    self.test_py_logger = PyLogger.getPyLogger()
    self.test_py_logger.setLevel(logging.DEBUG)

  def tearDown(self):
    # Remove any handlers after each test
    map(self.test_py_logger.removeHandler, self.test_py_logger.handlers)

  def test_get_py_logger(self):
    test_message = 'test message'
    expected_message = 'expected_message'

    # mock logging class
    logging_mock = Mock()
    #   basicConfig
    print 'hi'
    patches_dict = {}
    patches_dict['basic_config_patch'] = patch('logging.basicConfig', logging_mock)
    #   getLogger
    # patches_dict['get_logger_patch'] = patch('logging.getLogger', logging_mock)
    #   info
    patches_dict['info_patch'] = patch('logging.info', logging_mock)
    #   addHandler
    patches_dict['add_handler_patch'] = patch('logging.Logger.addHandler', logging_mock)

    # mock PySysLogHandler
    pysyslog_handler_mock = Mock()
    pysyslog_handler_class_mock = Mock(return_value=pysyslog_handler_mock)
    #   setLevel
    patches_dict['set_level_patch'] = patch('py_logger.py_syslog_handler.PySysLogHandler.setLevel', pysyslog_handler_mock)
    #   setFormatter
    patches_dict['set_formater_patch'] = patch('py_logger.py_syslog_handler.PySysLogHandler.setFormatter', pysyslog_handler_mock)


    # Start patches
    for p in patches_dict:
        print p
        patches_dict[p].start()

    # assert stuff

    # stop patches
    for p in patches_dict:
        print p
        patches_dict[p].stop()


if __name__ == '__main__':
    unittest.main()
