import logging
from logging.handlers import SysLogHandler
import socket

SYSLOG_TCP_PORT = logging.handlers.SYSLOG_TCP_PORT
AFTER_IDLE_SEC = 1
INTERVAL_SEC = 3
MAX_FAILS = 5


class PySysLogHandler(SysLogHandler):
    def __init__(self, address=('localhost', SYSLOG_TCP_PORT), facility=SysLogHandler.LOG_USER,
                 socktype=socket.SOCK_STREAM, terminator='\n'):
        """
        Initialize a handler.

        If address is specified as a string, a UNIX socket is used. To log to a
        local syslogd, "SysLogHandler(address="/dev/log")" can be used.
        If facility is not specified, LOG_USER is used. If socktype is
        specified as socket.SOCK_DGRAM or socket.SOCK_STREAM, that specific
        socket type will be used. For Unix sockets, you can also specify a
        socktype of None, in which case socket.SOCK_DGRAM will be used, falling
        back to socket.SOCK_STREAM. Lines will be terminated by terminator when
        emitted; by default they are null-terminated.
        """
        print address
        SysLogHandler.__init__(self, address=address, facility=facility, socktype=socktype)
        self.terminator = terminator
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if hasattr(socket, 'TCP_KEEPIDLE'):
            # socket.TCP_KEEPIDLE does not exist on OSX
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, AFTER_IDLE_SEC)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, INTERVAL_SEC)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, MAX_FAILS)

    def emit(self, record):
        """
        Emit a record.

        The record is formatted, and then sent to the syslog server. If
        exception information is present, it is NOT sent to the server.
        """
        try:
            msg = self.format(record) + self.terminator
            """
            We need to convert record level to lowercase, maybe this will change in the future.
            """
            prio = '<%d>' % self.encodePriority(self.facility, self.mapPriority(record.levelname))
            # Message is a string. Convert to bytes as required by RFC 5424
            if type(msg) is unicode:
                msg = msg.encode('utf-8')
            msg = prio + msg
            if self.unixsocket:
                try:
                    self.socket.send(msg)
                except socket.error:
                    self.socket.close()  # See issue 17981
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            elif self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            else:
                try:
                    self.socket.sendall(msg)
                except socket.error, err:
                    if err.errno == 32:
                        # Broken Pipe
                        try:
                            self.socket.close()
                        except:
                            pass
                        self.socket = socket.socket(socket.AF_INET, self.socktype)
                        self.socket.connect(self.address)
                        self.socket.sendall(msg)
                    else:
                        raise
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
