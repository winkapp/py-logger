# Py-Logger
[![CircleCI](https://circleci.com/gh/winkapp/py-logger.svg?style=svg&circle-token=8fa6f919da2f5e604e7e52082cec5f6a26548ab1)](https://circleci.com/gh/winkapp/py-logger)

A python logging library that enables logging via stout or syslog over TCP.

This library makes logs that adhere to the [Syslog Protocol RFC](https://tools.ietf.org/html/rfc5424).

All lines are send with a new line delimiter appended to the end of the line.

## Exmaple log line

<14> 2017-05-22 17:53:10,018 f2391b2845ac tcp_test_logger testing the tcp logger info level

# Usage

## stdout logger
```
from py_logger import PyLogger

logger = PyLogger.getPyLogger('stdout', 'my_app_name')

logger.info('Hello World')
```

## TCP logger
```
from py_logger import PyLogger

logger = PyLogger.getPyLogger('tcp', 'my_app_name')

logger.info('Hello World')
```

# Configuration

# Tests

`docker-compose run tests`
