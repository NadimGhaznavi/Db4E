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
        # Get the config settings
        ini = Db4eConfig()
        ch_log_level = LOG_LEVELS[ini.config['logging']['log_level'].lower()]
        # Get a Python logging instance, include the component to avoid dupes
        self._logger = logging.getLogger(f'db4e.{component}')
        # The logger's log level is hard-coded to debug. 
        self._logger.setLevel(LOG_LEVELS['debug'])
        # Avoid duplicate handlers
        if not getattr(self._logger, '_db4e_initialized', False):
            # Create a console handler
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
            ch.setFormatter(formatter)
            ch.setLevel(ch_log_level)
            self._logger.addHandler(ch)

            # Create a DB handler
            dbh = Db4eDbLogHandler()
            dbh.setLevel(LOG_LEVELS['debug'])
            self._logger.addHandler(dbh)

            # Mark logger as initialized
            self._logger._db4e_initialized = True

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
