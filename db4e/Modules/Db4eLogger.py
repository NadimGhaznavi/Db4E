"""
db4e/Modules/Db4eLogger.py

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

from db4e.Constants.Fields import (
    ELEMENT_TYPE_FIELD, DB4E_FIELD, DEBUG_FIELD,  
    LEVEL_FIELD, MINER_FIELD, NEW_FILE_FIELD, FILE_TYPE_FIELD,
    TIMESTAMP_FIELD)
from db4e.Constants.Defaults import (
    DB_RETRY_TIMEOUT_DEFAULT, LOG_COLLECTION_DEFAULT, 
    DB_NAME_DEFAULT,
    DB_PORT_DEFAULT, DB_SERVER_DEFAULT, DB_RETRY_TIMEOUT_DEFAULT)
from db4e.Constants.Jobs import MESSAGE_FIELD


LOG_LEVELS = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

class Db4eLogger:
    def __init__(self, elem_type: str, db=False, log_file=None):
        logger_name = f'{DB4E_FIELD}.{elem_type}'
        self._elem_type = elem_type
        self._logger = logging.getLogger(logger_name)

        # Set the logger log level, should always be 'debug'
        debug_log_level = LOG_LEVELS[DEBUG_FIELD]
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
            dbh = Db4eDbLogHandler(config)
            dbh.setLevel(debug_log_level)
            self._logger.addHandler(dbh)

        self._logger.propagate = False

    def shutdown(self):
        # Exit cleanly
        logging.shutdown() # Flush all handlers

    # Basic log message handling, wraps Python's logging object
    def info(self, message, extra=None):
        extra = extra or {} # Make sure extra isn't 'None'
        extra[ELEMENT_TYPE_FIELD] = self._elem_type
        self._logger.info(message, extra=extra)

    def debug(self, message, extra=None):
        extra = extra or {} 
        extra[ELEMENT_TYPE_FIELD] = self._elem_type
        self._logger.debug(message, extra=extra)

    def warning(self, message, extra=None):
        extra = extra or {} 
        extra[ELEMENT_TYPE_FIELD] = self._elem_type
        self._logger.warning(message, extra=extra)

    def error(self, message, extra=None):
        extra = extra or {} 
        extra[ELEMENT_TYPE_FIELD] = self._elem_type
        self._logger.error(message, extra=extra)

    def critical(self, message, extra=None):
        extra = extra or {} 
        extra[ELEMENT_TYPE_FIELD] = self._elem_type
        self._logger.critical(message, extra=extra)
            

class Db4eDbLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()

        self._db_server      = DB_SERVER_DEFAULT
        self._db_port        = DB_PORT_DEFAULT

        # Flag for connection status
        self.connected = False
        # Database handle
        self._db = None

    def emit(self, record):
        log_entry = {
            TIMESTAMP_FIELD: datetime.now(timezone.utc),
            LEVEL_FIELD: record.levelname,
            MESSAGE_FIELD: record.getMessage(),
        }
        # Copy any custom attributes from the record
        for attr in (ELEMENT_TYPE_FIELD, MINER_FIELD, NEW_FILE_FIELD, FILE_TYPE_FIELD):  # list whatever custom fields you expect
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
                print(f'Could not connect to DB ({db_server}:{db_port}), waiting {DB_RETRY_TIMEOUT_DEFAULT} seconds')
                if retries == 0:
                    raise RuntimeError(f"Could not connect to MongoDB: {db_server}:{db_port}")
                time.sleep(DB_RETRY_TIMEOUT_DEFAULT)
        self.connected = True
        self._db = client[DB_NAME_DEFAULT]        

    def log_db_message(self, log_entry):
        db = self.db()
        col = db[LOG_COLLECTION_DEFAULT]
        col.insert_one(log_entry)

