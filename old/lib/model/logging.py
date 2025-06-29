"""
lib/model/logging.py

This module implements a key component of the Data Abstraction Layer.
Aside from the Db4edDbLogHandler class, this is the only class that
interfaces with MongoDB.


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
from datetime import datetime, timezone
import traceback
from pymongo import MongoClient
import time

LOG_LEVELS = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

# Setup the db4e paths
DB4E_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 
DB4E_LIB_DIR = os.path.join(DB4E_DIR, 'lib')
DB4E_COMPONENTS_DIR = os.path.join(DB4E_LIB_DIR, 'components')
DB4E_MODEL_DIR = os.path.join(DB4E_LIB_DIR, 'model')
sys.path.append(DB4E_LIB_DIR)
sys.path.append(DB4E_COMPONENTS_DIR)
sys.path.append(DB4E_MODEL_DIR)
from settings import Db4eConfig

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
            

class Db4eDbLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()

        ini = Db4eConfig()
        self._retry_timeout  = ini.config['db']['retry_timeout']
        self._db_server      = ini.config['db']['server']
        self._db_port        = ini.config['db']['port']
        self._db_name        = ini.config['db']['name']
        self._log_collection = ini.config['db']['log_collection']

        # Flag for connection status
        self.connected = False
        # Database handle
        self._db = None

    def emit(self, record):
        log_entry = {
            'timestamp': datetime.now(timezone.utc),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        # Copy any custom attributes from the record
        for attr in ('component', 'miner', 'new_file', 'file_type'):  # list whatever custom fields you expect
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)

        try:
            self.log_db_message(log_entry)
        except Exception as e:
            print(f"Db4eDbLogHandler: Failed to log to DB: {e}", file=sys.stderr)
            traceback.print_exc()

    def db(self):
        if not self.connected:
            self.connect()
        return self._db
    
    def connect(self):
        db_server = self._db_server
        db_port = self._db_port
        db_name = self._db_name
        retry_timeout = self._retry_timeout
        try:
            client = MongoClient(f"mongodb://{db_server}:{db_port}/")
        except:
            self.log.critical(f'Could not connect to DB ({db_server}:{db_port}), waiting {retry_timeout} seconds')
            time.sleep(retry_timeout)
        self.connected = True
        self._db = client[db_name]        

    def log_db_message(self, log_entry):
        db = self.db()
        log_col = self._log_collection 
        col = db[log_col]
        col.insert_one(log_entry)

