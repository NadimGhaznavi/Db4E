"""
db4e/db/SQLDb.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import os, sqlite3
from datetime import datetime

from db4e.util.Db4ELogger import Db4ELogger

from db4e.constants.DFile import DFile
from db4e.constants.DField import DField
from db4e.constants.DSQL import DTable
from db4e.constants.DModule import DModule


class SQLDb:

    def __init__(self, db_type: str, log_file=None):
        """Constructor"""
        self._db_type = db_type
        self._db_dir = None
        self._conn = None
        self._cursor = None
        self._initialized = False
        if log_file:
            self.log = Db4ELogger(db4e_module=DModule.SQL_DB, log_file=log_file)
        else:
            self.log = None

    def close(self):
        """Close the connection to the database"""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None
            self._initialized = False

    def execute_query(self, sql, params=None):
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        self._cursor.execute(sql, params or [])
        self._conn.commit()
        return self._cursor.fetchall()

    def executescript(self, sql):
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        self._cursor.executescript(sql)
        self._conn.commit()

    def initialize(self, db_dir: str):
        self._db_dir = db_dir
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        if self._db_type == DField.SERVER:
            self._db_file = os.path.join(db_dir, DFile.SERVER_DB)
        elif self._db_type == DField.CLIENT:
            self._db_file = os.path.join(db_dir, DFile.CLIENT_DB)
        else:
            raise ValueError(f"Unrecognized db_type: {self._db_type}")

        # Connect to SQLite, get a cursor and initialize the DB
        self._conn = sqlite3.connect(self._db_file)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._cursor = self._conn.cursor()
        self._initialized = True

    def insert_one(self, sql, values):
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        self._cursor.execute(sql, values)
        self._conn.commit()
        return self._cursor.lastrowid

    def is_initialized(self):
        return self._initialized

    def update_one(self, sql, values):
        """Generic update method for any model with a __dict__() returning field:value mapping."""
        # Execute update
        print(f"sql: {sql}\nvalues: {values}")
        self._cursor.execute(sql, values)
        self._conn.commit()
        return self._cursor.rowcount
