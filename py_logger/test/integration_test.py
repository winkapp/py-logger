import os, sys
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(my_path, "..", ".."))

from py_logger.py_logger import PyLogger

stdout_test_logger = PyLogger.getPyLogger('stdout', 'std_test_logger')
stdout_test_logger.info('testing the stdout logger info level')

PyLogger.pyLoggers = {}

tcp_test_logger = PyLogger.getPyLogger('tcp', 'tcp_test_logger')
tcp_test_logger.info('testing the tcp logger info level')

map(stdout_test_logger.removeHandler, stdout_test_logger.handlers)
map(tcp_test_logger.removeHandler, tcp_test_logger.handlers)
