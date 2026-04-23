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
import time

from db4e.constants.DField import DField
from db4e.constants.DElem import DElem
from db4e.constants.DDef import DDef


LOG_LEVELS = {
    DField.INFO: logging.INFO,
    DField.DEBUG: logging.DEBUG,
    DField.WARNING: logging.WARNING,
    DField.ERROR: logging.ERROR,
    DField.CRITICAL: logging.CRITICAL,
}


class Db4ELogger:
    """
    Logger wrapper for Db4E modules with optional DB logging.
    """

    def __init__(self, db4e_module: str, db=False, log_file=None):
        """
        Initialize a logger for a Db4E module.

        :param db4e_module: Module name or identifier for log entries.
        :type db4e_module: str
        :param db: Whether to log to the database.
        :type db: bool
        :param log_file: Optional log file path.
        :type log_file: str or None
        :return: None
        :rtype: None
        """
        logger_name = f"{db4e_module}"
        self._db4e_module = db4e_module
        self._logger = logging.getLogger(logger_name)

        # Set the logger log level, should always be 'debug'
        debug_log_level = LOG_LEVELS[DField.DEBUG]
        self._logger.setLevel(debug_log_level)

        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Optional file handler
        if log_file:
            has_file = any(
                isinstance(h, logging.FileHandler)
                and getattr(h, "baseFilename", None) == log_file
                for h in self._logger.handlers
            )
            if not has_file:
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
        """
        Shutdown logging and flush handlers.

        :return: None
        :rtype: None
        """
        # Exit cleanly
        logging.shutdown()  # Flush all handlers

    # Basic log message handling, wraps Python's logging object
    def info(self, message, extra=None):
        """
        Log an info message.

        :param message: Log message.
        :type message: str
        :param extra: Optional extra fields to attach.
        :type extra: dict or None
        :return: None
        :rtype: None
        """
        extra = extra or {}  # Make sure extra isn't 'None'
        extra[DField.ELEMENT_TYPE] = self._db4e_module
        self._logger.info(message, extra=extra)

    def debug(self, message, extra=None):
        """
        Log a debug message.

        :param message: Log message.
        :type message: str
        :param extra: Optional extra fields to attach.
        :type extra: dict or None
        :return: None
        :rtype: None
        """
        extra = extra or {}
        extra[DField.ELEMENT_TYPE] = self._db4e_module
        self._logger.debug(message, extra=extra)

    def warning(self, message, extra=None):
        """
        Log a warning message.

        :param message: Log message.
        :type message: str
        :param extra: Optional extra fields to attach.
        :type extra: dict or None
        :return: None
        :rtype: None
        """
        extra = extra or {}
        extra[DField.ELEMENT_TYPE] = self._db4e_module
        self._logger.warning(message, extra=extra)

    def error(self, message, extra=None):
        """
        Log an error message.

        :param message: Log message.
        :type message: str
        :param extra: Optional extra fields to attach.
        :type extra: dict or None
        :return: None
        :rtype: None
        """
        extra = extra or {}
        extra[DField.ELEMENT_TYPE] = self._db4e_module
        self._logger.error(message, extra=extra)

    def critical(self, message, extra=None):
        """
        Log a critical message.

        :param message: Log message.
        :type message: str
        :param extra: Optional extra fields to attach.
        :type extra: dict or None
        :return: None
        :rtype: None
        """
        extra = extra or {}
        extra[DField.ELEMENT_TYPE] = self._db4e_module
        self._logger.critical(message, extra=extra)


class Db4eDbLogHandler(logging.Handler):
    """
    Logging handler that writes records to MongoDB.
    """

    def __init__(self):
        """
        Initialize the MongoDB-backed log handler.

        :return: None
        :rtype: None
        """
        super().__init__()

        self._db_server = DDef.DB_SERVER
        self._db_port = DDef.DB_PORT

        # Flag for connection status
        self.connected = False
        # Database handle
        self._db = None

    def emit(self, record):
        """
        Emit a log record to the database.

        :param record: Log record to emit.
        :type record: logging.LogRecord
        :return: None
        :rtype: None
        """
        log_entry = {
            DField.TIMESTAMP: datetime.now(timezone.utc),
            DField.LEVEL: record.levelname,
            DField.MESSAGE: record.getMessage(),
        }
        # Copy any custom attributes from the record
        for attr in (
            DField.ELEMENT_TYPE,
            DField.MINER,
            DField.NEW_FILE,
            DField.FILE_TYPE,
        ):  # list whatever custom fields you expect
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)

        try:
            self.log_db_message(log_entry)
        except Exception as e:
            print(f"Db4eDbLogHandler: Failed to log to DB: {e}", file=sys.stderr)
            traceback.print_exc()

    def db(self):
        """
        Return a MongoDB database handle, connecting if needed.

        :return: Database handle.
        :rtype: object
        """
        if not self.connected:
            self.connect()
        return self._db

    def connect(self):
        """
        Connect to the MongoDB server with retry.

        :return: None
        :rtype: None
        """
        db_server = self._db_server
        db_port = self._db_port
        retries = 3
        while retries > 0:
            retries -= 1
            try:
                client = MongoClient(f"mongodb://{db_server}:{db_port}/")
            except:
                print(
                    f"Could not connect to DB ({db_server}:{db_port}), waiting {DDef.DB_RETRY_TIMEOUT} seconds"
                )
                if retries == 0:
                    raise RuntimeError(
                        f"Could not connect to MongoDB: {db_server}:{db_port}"
                    )
                time.sleep(DDef.DB_RETRY_TIMEOUT)
        self.connected = True
        self._db = client[DDef.DB_NAME]

    def log_db_message(self, log_entry):
        """
        Insert a log entry into the log collection.

        :param log_entry: Log entry payload.
        :type log_entry: dict
        :return: None
        :rtype: None
        """
        db = self.db()
        col = db[DDef.LOG_COLLECTION]
        col.insert_one(log_entry)
