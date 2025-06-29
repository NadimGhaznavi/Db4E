"""
lib/Db4eLogger/Db4eLogger.py

This class is a wrapper around the standard Python logging module.
The module provides *db4e* with clean, consistent logs that are
written to MongoDB.


  This file is part of *db4e*, the *Database 4 Everything* project
  <https://github.com/NadimGhaznavi/db4e>, developed independently
  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
  <https://github.com/NadimGhaznavi/db4e>.
 
  This program is free software: you can redistribute it and/or 
  modify it under the terms of the GNU General Public License as 
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy (LICENSE.txt) of the GNU General 
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""

import os, sys
import logging

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eDbLogHandler.Db4eDbLogHandler import Db4eDbLogHandler
from Db4eOSStrings.Db4eOSStrings import LOG_LEVELS

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
