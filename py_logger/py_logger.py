import logging
import os
import socket
from py_syslog_handler import PySysLogHandler

# always log in this format.

TCP_LOGGING_HOST = os.environ.get('SYSLOG_HOST', 'localhost')
TCP_LOGGING_PORT = int(os.environ.get('SYSLOG_PORT', logging.handlers.SYSLOG_TCP_PORT))
LOG_LINE_TERMINATOR = '\n'


class PyLogger:
    pyLogger = None

    def __init__(self, method='stdout'):
        print ("Loggin Method: %s" % method)
        self.version = '.1'
        # Check the environment to turn on remote syslog logging
        self.rootLogger = self.getLogger(method)

    @classmethod
    def getLogger(cls, method, app_name):
        LOGGING_FORMAT = '%(asctime)s ' + socket.gethostname() + app_name + '%(message)s'
        # first do the basic config to the root logger
        logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)
        # get a handle to this logger
        logger = logging.getLogger() # no args = root logger
        print "method is %s" % method
        if method == 'tcp':
            # this line will go to the stdout handler since we
            # haven't added a socket one yet
            logging.info("Setting up tcp handler %s:%s" %
                         (TCP_LOGGING_HOST, TCP_LOGGING_PORT))
            # in tcp mode, additionally add a SysLogHandler
            # pass (host, port) as tuple, specify to use TCP socket
            tcpHandler = PySysLogHandler((TCP_LOGGING_HOST, TCP_LOGGING_PORT),
                                              socktype=socket.SOCK_STREAM,
                                              terminator=LOG_LINE_TERMINATOR)
            tcpHandler.setLevel(logging.INFO)
            tcpHandler.setFormatter(logging.Formatter(LOGGING_FORMAT))
            # attach it to the root logger
            logger.addHandler(tcpHandler)
        logging.info("Logging configured") # smoke test
        return logger # return it in case we want to do stuff to it.

    def createJsonString(self, log_type, logDict):
        logDict['log_type'] = log_type
        return json.dumps(logDict)

    @classmethod
    def getPyLogger(cls, method='stdout', app_name='app'):
        if cls.pyLogger == None:
            if os.environ.get('TCP_SYSLOG_LOGGING') is 'true':
                method = 'tcp'
            print "Getting spark logging, method is %s" % method
            cls.pyLogger = cls.getLogger(method, app_name)

        return cls.pyLogger

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

