"""
db4e/Modules/Db4ELogger.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

import os, sys
import logging
from datetime import datetime, timezone
import traceback
from pymongo import MongoClient
import time

from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DDef import DDef



LOG_LEVELS = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

class Db4ELogger:
    def __init__(self, db4e_module: str, db=False, log_file=None):
        logger_name = f'{db4e_module}'
        self._db4e_module = db4e_module
        self._logger = logging.getLogger(logger_name)

        # Set the logger log level, should always be 'debug'
        debug_log_level = LOG_LEVELS[DField.DEBUG]
        self._logger.setLevel(debug_log_level)

        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

        # Optional file handler
        if log_file:
            fh = logging.FileHandler(log_file)
            fh.setLevel(debug_log_level)
            fh.setFormatter(formatter)
            self._logger.addHandler(fh)

        # Optional DB handler
        if db:
            dbh = Db4eDbLogHandler()
            dbh.setLevel(debug_log_level)
            self._logger.addHandler(dbh)

        self._logger.propagate = False

    def shutdown(self):
        # Exit cleanly
        logging.shutdown() # Flush all handlers

    # Basic log message handling, wraps Python's logging object
    def info(self, message, extra=None):
        extra = extra or {} # Make sure extra isn't 'None'
        extra[DField.ELEMENT_TYPE] = self._db4e_module
        self._logger.info(message, extra=extra)

    def debug(self, message, extra=None):
        extra = extra or {} 
        extra[DField.ELEMENT_TYPE] = self._db4e_module
        self._logger.debug(message, extra=extra)

    def warning(self, message, extra=None):
        extra = extra or {} 
        extra[DField.ELEMENT_TYPE] = self._db4e_module
        self._logger.warning(message, extra=extra)

    def error(self, message, extra=None):
        extra = extra or {} 
        extra[DField.ELEMENT_TYPE] = self._db4e_module
        self._logger.error(message, extra=extra)

    def critical(self, message, extra=None):
        extra = extra or {} 
        extra[DField.ELEMENT_TYPE] = self._db4e_module
        self._logger.critical(message, extra=extra)
            

class Db4eDbLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()

        self._db_server      = DDef.DB_SERVER
        self._db_port        = DDef.DB_PORT

        # Flag for connection status
        self.connected = False
        # Database handle
        self._db = None

    def emit(self, record):
        log_entry = {
            DField.TIMESTAMP: datetime.now(timezone.utc),
            DField.LEVEL: record.levelname,
            DField.MESSAGE: record.getMessage(),
        }
        # Copy any custom attributes from the record
        for attr in (DField.ELEMENT_TYPE, DField.MINER, DField.NEW_FILE, DField.FILE_TYPE):  # list whatever custom fields you expect
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
        retries = 3
        while retries > 0:
            retries -= 1
            try:
                client = MongoClient(f"mongodb://{db_server}:{db_port}/")
            except:
                print(f'Could not connect to DB ({db_server}:{db_port}), waiting {DDef.DB_RETRY_TIMEOUT} seconds')
                if retries == 0:
                    raise RuntimeError(f"Could not connect to MongoDB: {db_server}:{db_port}")
                time.sleep(DDef.DB_RETRY_TIMEOUT)
        self.connected = True
        self._db = client[DDef.DB_NAME]        

    def log_db_message(self, log_entry):
        db = self.db()
        col = db[DDef.LOG_COLLECTION]
        col.insert_one(log_entry)

