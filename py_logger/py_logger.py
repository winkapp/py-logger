import logging
import os
import socket
from py_syslog_handler import PySysLogHandler

class PyLogger:
    pyLoggers = {}

    def __init__(self, method='stdout'):
        print ("Loggin Method: %s" % method)
        self.version = '.1'
        # Check the environment to turn on remote syslog logging
        self.rootLogger = self.getLogger(method)

    @classmethod
    def getLogger(cls, method, app_name):
        logging_format = "%%(asctime)s %s %s %%(message)s" % (socket.gethostname(), app_name)

        print "method is %s" % method
        if method == 'tcp':
            # first do the basic config of the logger
            logging.basicConfig(format=logging_format, level=logging.INFO)
            # get a handle to this logger
            logger = logging.getLogger() # no args = root logger
            # config and add a TCP logger handler
            handler = cls.tcpLoggerHandler()
            handler.setFormatter
            logger.addHandler(handler)
        else:
            # The basicConfig is done separately for each type of logger such that things can be easily tested
            # It's not great that it's definited in two places
            # TODO: find a way to test this while setting for all loggers, ran into issue where addHandler was
            # called twice due to it being called with basicConfig and when the tcp handler is added above
            logging.basicConfig(format=logging_format, level=logging.INFO)
            # Get a root logger
            logger = logging.getLogger() # no args = root logger

        return logger # return it in case we want to do stuff to it.

    @classmethod
    def tcpLoggerHandler(cls):
        # get tcp logger config from the environment
        tcp_logging_host = os.environ.get('SYSLOG_HOST', 'localhost')
        tcp_logging_port = int(os.environ.get('SYSLOG_PORT', logging.handlers.SYSLOG_TCP_PORT))
        log_line_terminator = os.environ.get('SYSLOG_LINE_TERMINATOR', '\n')
        # this line will go to the stdout handler since we
        # haven't added a socket one yet
        logging.info("Setting up tcp handler %s:%s" %
                     (tcp_logging_host, tcp_logging_port))
        # in tcp mode, additionally add a SysLogHandler
        # pass (host, port) as tuple, specify to use TCP socket
        tcpHandler = PySysLogHandler(address=(tcp_logging_host, tcp_logging_port),
                                          socktype=socket.SOCK_STREAM,
                                          terminator=log_line_terminator)
        tcpHandler.setLevel(logging.INFO)
        # return handler
        return tcpHandler

    def createJsonString(self, log_type, logDict):
        logDict['log_type'] = log_type
        return json.dumps(logDict)

    @classmethod
    def getPyLogger(cls, method='stdout', app_name='app'):
        if cls.pyLoggers.get(method) == None:
            if os.environ.get('TCP_SYSLOG_LOGGING') is 'true':
                method = 'tcp'
            print "Getting %s logger" % method
            cls.pyLoggers[method] = cls.getLogger(method, app_name)
        return cls.pyLoggers[method]

    def getMlPrefix(self):
        return 'mlAnalytics:'

    # Info logs for normal logging and metrics
    def info(self, log):
        logging.info(log)

    # Info logs for mlAnalytics formated logs for future processesing
    def info_ml_analytics(self, log_type, log):
        assert isinstance(log, dict), "mlAnalytics logs must be a dict"
        logging.info(self.getMlPrefix() + self.createJsonString(log_type, log))

    def debug_ml_analytics(self, logDict):
        logging.debug(self.getMlPrefix() + self.createJsonString('spark_debug', logDict))

    def debug(self, logString):
        logging.debug(logString)

    def debug_type(self, log_type, logDict):
        logging.debug(self.createJsonString(log_type, logDict))

    def warning(self, log_type, logDict):
        logging.warning(self.createJsonString(log_type, logDict))

    def critical(self, log_type, logDict):
        logDict['version'] = self.version
        logDict['MODEL_TYPE'] = os.environ['MODEL_TYPE']
        logging.critical(self.createJsonString(log_type, logDict))

