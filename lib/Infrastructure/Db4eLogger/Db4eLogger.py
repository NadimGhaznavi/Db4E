"""
lib/Infrastructure/Db4eLogger/Db4eLogger.py
"""

import os, sys
import logging

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eDbLogHandler.Db4eDbLogHandler import Db4eDbLogHandler

LOG_LEVELS = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

class Db4eLogger:
    def __init__(self, component):
        self._component = component
        logger_name = f'db4e.{component}'
        self._logger = logging.getLogger(logger_name)

        # Get the config settings
        ini = Db4eConfig()
        ch_log_level = LOG_LEVELS[ini.config['logging']['log_level'].lower()]

        # Set the logger log level, should always be 'debug'
        self._logger.setLevel(LOG_LEVELS['debug'])

        # Console handler            
        ch = logging.StreamHandler()
        ch.setLevel(ch_log_level)
        ch.setFormatter(logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'))
        self._logger.addHandler(ch)

        # DB handler
        dbh = Db4eDbLogHandler()
        dbh.setLevel(logging.DEBUG)
        self._logger.addHandler(dbh)

        self._logger.propagate = False

    def shutdown(self):
        # Exit cleanly
        logging.shutdown() # Flush all handlers

    # Basic log message handling, wraps Python's logging object
    def info(self, message, extra=None):
        extra = extra or {} # Make sure extra isn't 'None'
        extra['component'] = self._component
        self._logger.info(message, extra=extra)

    def debug(self, message, extra=None):
        extra = extra or {} 
        extra['component'] = self._component
        self._logger.debug(message, extra=extra)

    def warning(self, message, extra=None):
        extra = extra or {} 
        extra['component'] = self._component
        self._logger.warning(message, extra=extra)

    def error(self, message, extra=None):
        extra = extra or {} 
        extra['component'] = self._component
        self._logger.error(message, extra=extra)

    def critical(self, message, extra=None):
        extra = extra or {} 
        extra['component'] = self._component
        self._logger.critical(message, extra=extra)
