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

from db4e.constants.DFile import DFile
from db4e.constants.DField import DField
from db4e.constants.DSQL import DTable


class SQLDb:

    def __init__(self, db_type: str):
        """Constructor"""

        self._db_type = db_type
        self._db_dir = None
        self._conn = None
        self._cursor = None
        self._initialized = False
        self.initialize()

    def close(self):
        """Close the connection to the database"""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None
            self._initialized = False

    def execute_insert_one(self, sql, values):
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        self._cursor.execute(sql, values)
        self._conn.commit()
        return self._cursor.lastrowid

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

    def is_initialized(self):
        return self._initialized

    def update_one(self, elem):
        """Generic update method for any model with a __dict__() returning field:value mapping."""
        data = elem.__dict__()  # Your model’s dict with DField constants as keys
        now = datetime.now()

        table_name = ELEM_TABLE_MAP[type(elem)]

        # The timestamps for these records are from the P2Pool log file. We want to make sure
        # the record's timestamp matches the string in the log file to "replay" a log
        if table_name not in [DTable.BLOCK_FOUND_EVENT]:
            data.update(
                {
                    "updated_y": now.year,
                    "updated_mo": now.month,
                    "updated_d": now.day,
                    "updated_h": now.hour,
                    "updated_mi": now.minute,
                    "updated_s": now.second,
                }
            )

        # These records are "hourly" records. Only one record should exist "per hour".
        elif table_name in [DTable.CHAIN_HASHRATE]:
            data.update(
                {
                    "updated_y": now.year,
                    "updated_mo": now.month,
                    "updated_d": now.day,
                    "updated_h": now.hour,
                }
            )

        # Stable ordering for deterministic SQL generation
        columns = sorted(data.keys())

        # Build the SQL SET clause: column1=?, column2=?, ...
        set_clause = ", ".join([f"{col}=?" for col in columns])

        # Get the record_id from the object
        record_id = elem.id()

        sql = f"UPDATE {table_name} SET {set_clause} WHERE id=?"
        values = tuple(data[col] for col in columns) + (record_id,)

        # Execute update
        self._cursor.execute(sql, values)
        self._conn.commit()

        return self._cursor.rowcount
