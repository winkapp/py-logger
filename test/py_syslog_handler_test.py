from lib.py_syslog_handler import PySysLogHandler
import unittest
from mock import Mock, patch
import logging
import socket

TESTING_FORMAT_STRING = '%(levelname)s\t%(message)s'


class PySysLogHandler_test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logger_name = 'test_logger'
        # what will we log and what do we expect?
        cls.logged_string = 'test_string'
        cls.expected_level = 'DEBUG'  # level we will log with
        cls.expected_prio = '15'  # magic number for DEBUG on this image
        # here's what we expect to come out the other end...
        cls.expected_log = '<{}>{}\t{}\n'.format(
            cls.expected_prio, cls.expected_level, cls.logged_string)

    def setUp(self):
        self.test_logger = logging.getLogger(self.logger_name)
        self.test_logger.setLevel(logging.DEBUG)

    def tearDown(self):
        # Remove any handlers after each test
        map(self.test_logger.removeHandler, self.test_logger.handlers)

    def test_emit(self):
        # mock a socket we can watch
        socket_mock = Mock()
        # make a mock that will replace socket.socket
        # and always return the mocked socket
        socket_class_mock = Mock(return_value=socket_mock)
        # patch socket.socket with the mock
        socket_patch = patch('socket.socket', socket_class_mock)
        socket_patch.start()

        # make a handler to test, setting level and format to something known
        handler = ShuttleSysLogHandler(('localhost', 514), socktype=socket.SOCK_STREAM,
                                       terminator='\n')
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(TESTING_FORMAT_STRING))

        # get a test logger and attach this handler
        self.test_logger.addHandler(handler)

        # run it.
        self.test_logger.debug(self.logged_string)
        socket_mock.sendall.assert_called_once_with(self.expected_log)

        # stop hijacking socket.socket.
        socket_patch.stop()

    def test_emit_sendall_brokenpipe_exception(self):
        # mock a socket we can watch
        socket_mock = Mock()

        broken_pipe_exc = socket.error('Broken pipe')
        broken_pipe_exc.errno = 32
        socket_mock.sendall = Mock(side_effect=[broken_pipe_exc, None])
        # make a mock that will replace socket.socket
        # and always return the mocked socket
        socket_class_mock = Mock(return_value=socket_mock)
        # patch socket.socket with the mock
        socket_patch = patch('socket.socket', socket_class_mock)
        socket_patch.start()

        # make a handler to test, setting level and format to something known
        handler = ShuttleSysLogHandler(('localhost', 514), socktype=socket.SOCK_STREAM,
                                       terminator='\n')
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(TESTING_FORMAT_STRING))

        # get a test logger and attach this handler
        self.test_logger.addHandler(handler)

        # run it.
        self.test_logger.debug(self.logged_string)

        socket_mock.sendall.assert_called_with(self.expected_log)
        self.assertEqual(
            socket_mock.sendall.call_count, 2,
            'Expected "{}" to be called twice. Called {} times.'.format(
                socket_mock.sendall._mock_name or 'mock',
                socket_mock.sendall.call_count))

        # stop hijacking socket.socket.
        socket_patch.stop()

    def test_dgram(self):
        # mock a socket we can watch
        socket_mock = Mock()
        # make a mock that will replace socket.socket
        # and always return the mocked socket
        socket_class_mock = Mock(return_value=socket_mock)
        # patch socket.socket with the mock
        socket_patch = patch('socket.socket', socket_class_mock)
        socket_patch.start()

        # make a handler to test, setting level and format to something known
        handler = ShuttleSysLogHandler(('localhost', 514), socktype=socket.SOCK_DGRAM,
                                       terminator='\n')
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(TESTING_FORMAT_STRING))

        # get a test logger and attach this handler
        self.test_logger.addHandler(handler)

        self.test_logger.setLevel(logging.DEBUG)

        # run it.
        self.test_logger.debug(self.logged_string)
        socket_mock.sendto.assert_called_once_with(self.expected_log, ('localhost', 514))

        # stop hijacking socket.socket.
        socket_patch.stop()

    def test_unixsocket(self):
        # mock a socket we can watch
        socket_mock = Mock()
        # make a mock that will replace socket.socket
        # and always return the mocked socket
        socket_class_mock = Mock(return_value=socket_mock)
        # patch socket.socket with the mock
        socket_patch = patch('socket.socket', socket_class_mock)
        socket_patch.start()

        # make a handler to test, setting level and format to something known
        handler = ShuttleSysLogHandler("/dev/log", socktype=socket.SOCK_DGRAM, terminator='\n')
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(TESTING_FORMAT_STRING))

        # get a test logger and attach this handler
        self.test_logger.addHandler(handler)

        # run it.
        self.test_logger.debug(self.logged_string)
        socket_mock.send.assert_called_once_with(self.expected_log)

        # stop hijacking socket.socket.
        socket_patch.stop()

    def test_unixsocket_exception(self):
        # mock a socket we can watch
        socket_mock = Mock()
        socket_mock.send = Mock(side_effect=[socket.error, None])
        # make a mock that will replace socket.socket
        # and always return the mocked socket
        socket_class_mock = Mock(return_value=socket_mock)
        # patch socket.socket with the mock
        socket_patch = patch('socket.socket', socket_class_mock)
        socket_patch.start()

        # make a handler to test, setting level and format to something known
        handler = ShuttleSysLogHandler("/dev/log", socktype=socket.SOCK_DGRAM, terminator='\n')
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(TESTING_FORMAT_STRING))

        # get a test logger and attach this handler
        self.test_logger.addHandler(handler)

        # run it.
        self.test_logger.debug(self.logged_string)
        socket_mock.send.mock.call_args_list = [self.expected_log, self.expected_log]
        socket_mock.close.assert_called_once_with()

        # stop hijacking socket.socket.
        socket_patch.stop()


if __name__ == '__main__':
    unittest.main()
