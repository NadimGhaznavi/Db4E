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
from db4e.mgr.BootstrapMgr import BootstrapMgr


from db4e.constants.DFile import DFile
from db4e.constants.DDir import DDir
from db4e.constants.DField import DField
from db4e.constants.DSQL import (
    DCol,
    ELEM_TABLE_LIST,
    HOURLY_MINING_TABLE_LIST,
    MINING_TABLE_LIST,
    OPS_TABLE_LIST,
)
from db4e.constants.DModule import DModule


class SQLDb:

    def __init__(self, db_type: str, bs_mgr: BootstrapMgr, log_file=None):
        """Constructor"""
        self.bs_mgr = bs_mgr
        self._db_type = db_type
        self._db_dir = None
        self._conn = None
        self._cursor = None
        self._sync_meta_initialized = False

        if bs_mgr.is_initialized():
            self.initialize(db_dir=bs_mgr.get_dir(DDir.DB))
            self._initialized = True
        else:
            self._initialized = False

        if log_file:
            self.log = Db4ELogger(db4e_module=DModule.SQL_DB, log_file=log_file)
        else:
            self.log = None

        if self.is_initialized():
            self._sync_meta_initialized = True
            self._init_db()

    def check_initialized(self):
        if self.is_initialized():
            return
        else:
            if self.bs_mgr.is_initialized():
                self._initialized = True
            else:
                self._initialized = False

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

    def execute_merge(self, sql, rows):
        for row in rows:
            self._cursor.execute(sql, tuple(row[k] for k in row.keys()))
        self._conn.commit()

    def find_one(self, sql: str, params: tuple = ()):
        """Execute a query and return a single row (or None)."""
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        self._cursor.execute(sql, params)
        return self._cursor.fetchone()

    def find_many(self, table: str):
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        self._cursor.execute(f"SELECT * FROM {table}")
        return self._cursor.fetchall()

    def get_last_sync(self, table_name: str) -> int:
        """Fetch last sync timestamp for a given table from sync_meta."""
        try:
            row = self.find_one(
                "SELECT last_sync_ts FROM sync_meta WHERE table_name = ?", (table_name,)
            )
            return row[DCol.LAST_SYNC_TS] if row else 0
        except Exception as e:
            print("Error fetching last sync timestamp:", e)

    def _init_db(self):
        self.executescript(
            """
            CREATE TABLE IF NOT EXISTS sync_meta (
                table_name TEXT PRIMARY KEY,
                last_sync_ts INTEGER
            );
            """
        )
        for table_name in (
            ELEM_TABLE_LIST
            + MINING_TABLE_LIST
            + HOURLY_MINING_TABLE_LIST
            + OPS_TABLE_LIST
        ):
            self.execute_query(
                "INSERT OR IGNORE INTO sync_meta (table_name, last_sync_ts) VALUES (?, 0)",
                (table_name,),
            )

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

        # Initialize the DB
        if not self._sync_meta_initialized:
            self._sync_meta_initialized = True
            self._init_db()

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
        # print(f"sql: {sql}\nvalues: {values}")
        self._cursor.execute(sql, values)
        self._conn.commit()
        return self._cursor.rowcount

    def update_last_sync(self, table_name: str, ts: int):
        """Persist updated last sync timestamp."""
        self.execute_query(
            """
            INSERT INTO sync_meta (table_name, last_sync_ts)
            VALUES (?, ?)
            ON CONFLICT(table_name)
            DO UPDATE SET last_sync_ts = excluded.last_sync_ts
            """,
            (table_name, ts),
        )
