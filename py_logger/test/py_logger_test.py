from py_logger import PyLogger
import unittest
from mock import Mock, patch
import logging

class PyLogger_test(unittest.TestCase):
  def setUp(self):
    self.test_spark_logger = PyLogger.getLogger

  def test_is_json():
    test_json = '{"key": "value"}'
    should_be_json = self.test_spark_logger.is_json(test_json)
    assert should_be_json == true



if __name__ == '__main__':
    unittest.main()
