# db4e/db/SQLDb.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import os, sqlite3
from pathlib import Path

from db4e.util.Db4ELogger import Db4ELogger
from db4e.mgr.BootstrapMgr import BootstrapMgr


from db4e.constants.DFile import DFile
from db4e.constants.DDef import DDef
from db4e.constants.DDir import DDir
from db4e.constants.DField import DField
from db4e.constants.DSQL import (
    DCol,
    ELEM_TABLE_LIST,
    HOURLY_MINING_TABLE_LIST,
    MINING_TABLE_LIST,
    OPS_TABLE_LIST,
    HEALTH_STATE_TABLE_LIST,
)
from db4e.constants.DModule import DModule


class SQLDb:
    """
    The ``SQLDb`` class sits at the lowest layer of the Data Abstraction Layer
    and provides direct access to the underlying SQLite database file.

    It is responsible for:

    - Establishing and maintaining the SQLite connection.
    - Executing queries, scripts, inserts, updates, and merges.
    - Initializing DB schema metadata (``sync_meta`` table).
    - Acting as a thin wrapper over ``sqlite3`` with additional Db4E-specific logic.
    """

    def __init__(self, db_type: str, bs_mgr: BootstrapMgr, log_file=None):
        """
        Initialize a new ``SQLDb`` instance.

        Initialization includes:

        - Recording database type (server/client).
        - Checking BootstrapMgr state.
        - Optionally setting up logging.
        - Connecting to the database immediately if BootstrapMgr is already initialized.

        :param db_type: The database type (e.g., ``DField.SERVER`` or ``DField.CLIENT``).
        :type db_type: str
        :param bs_mgr: Bootstrap manager providing directory and configuration context.
        :type bs_mgr: BootstrapMgr
        :param log_file: Optional log file path for ``Db4ELogger``.
        :type log_file: str or None
        :return: A new SQLDb object.
        :rtype: SQLDb
        """
        self.bs_mgr = bs_mgr
        self._db_type = db_type

        if db_type == DField.SERVER:
            self._db_dir = os.path.join(DDef.DB4E_INSTALL_DIR, DDir.DB)
            self._db_file = os.path.join(
                DDef.DB4E_INSTALL_DIR, DDir.DB, DFile.SERVER_DB
            )

        elif db_type == DField.CLIENT:
            home_dir = Path.home()
            self._db_dir = os.path.join(home_dir, DDir.DOT_DB4E)
            self._db_file = os.path.join(home_dir, DDir.DOT_DB4E, DFile.CLIENT_DB)

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
        if log_file:
            self.log = Db4ELogger(db4e_module=DModule.SQL_DB, log_file=log_file)
        else:
            self.log = None

        self._sync_meta_initialized = True
        self._init_db()

    def close(self):
        """
        Close the connection to the SQLite database.

        This resets the internal connection, cursor, and initialization flag.
        """
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None
            self._initialized = False

    def execute_query(self, sql, params=None):
        """
        Execute a SQL query and return all resulting rows.

        :param sql: SQL query string.
        :type sql: str
        :param params: Optional query parameters.
        :type params: list or tuple or dict or None
        :return: List of rows returned by the query.
        :rtype: list
        :raises RuntimeError: If the database has not been initialized.
        """
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        # print(f"execute_query: sql: {sql}, params: {params}")
        self._cursor.execute(sql, params or [])
        self._conn.commit()
        return self._cursor.fetchall()

    def executescript(self, sql):
        """
        Execute a multi-statement SQL script.

        :param sql: The SQL script to execute.
        :type sql: str
        :raises RuntimeError: If the database has not been initialized.
        """
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        self._cursor.executescript(sql)
        self._conn.commit()

    def execute_merge(self, sql, rows):
        """
        Execute repeated parameterized SQL statements for bulk insertion/merge.

        :param sql: SQL statement containing parameter placeholders.
        :type sql: str
        :param rows: Iterable of dictionary-like row mappings.
        :type rows: list[dict]
        """
        for row in rows:
            self._cursor.execute(sql, tuple(row[k] for k in row.keys()))
        self._conn.commit()

    def find_one(self, sql: str, params: tuple = ()):
        """
        Execute a SQL query and return a single row.

        :param sql: SQL query string.
        :type sql: str
        :param params: Optional query parameters.
        :type params: tuple
        :return: First matching row or ``None`` if no results.
        :rtype: sqlite3.Row or None
        :raises RuntimeError: If the database has not been initialized.
        """
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        self._cursor.execute(sql, params)
        return self._cursor.fetchone() or None

    def find_many(self, table: str):
        """
        Fetch all rows from a given table.

        :param table: Table name to query.
        :type table: str
        :return: List of rows from the table.
        :rtype: list
        :raises RuntimeError: If the database has not been initialized.
        """
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        self._cursor.execute(f"SELECT * FROM {table}")
        return self._cursor.fetchall()

    def get_last_sync(self, table_name: str) -> int:
        """
        Retrieve the last synchronization timestamp for a table.

        :param table_name: Name of the table.
        :type table_name: str
        :return: Last sync timestamp, or ``0`` if not set.
        :rtype: int
        """
        try:
            row = self.find_one(
                "SELECT last_sync_ts FROM sync_meta WHERE table_name = ?", (table_name,)
            )
            return row[DCol.LAST_SYNC_TS] if row else 0
        except Exception as e:
            print("Error fetching last sync timestamp:", e)

    def get_max_updated_ts(self, table_name: str) -> int:
        """
        Retrieve the maximum ``updated_ts`` value from a table.

        :param table_name: Name of the table to scan.
        :type table_name: str
        :return: Maximum timestamp, or ``0`` if table is empty.
        :rtype: int
        """
        try:
            row = self.find_one(f"SELECT MAX({DCol.UPDATED_TS}) FROM {table_name}")
            if row:
                return row[0]
            else:
                return 0
        except Exception as e:
            print("Error fetching max updated_ts:", e)

    def _init_db(self):
        """
        Initialize internal metadata tables.

        Creates ``sync_meta`` if necessary and ensures each table has a
        corresponding row tracking its ``last_sync_ts``.
        """
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
            + HEALTH_STATE_TABLE_LIST
        ):
            self.execute_query(
                "INSERT OR IGNORE INTO sync_meta (table_name, last_sync_ts) VALUES (?, 0)",
                (table_name,),
            )

    def insert_one(self, sql, values):
        """
        Insert a single row into the database.

        :param sql: SQL insert statement containing placeholders.
        :type sql: str
        :param values: Tuple or list of values to bind.
        :type values: tuple or list
        :return: Last inserted row ID.
        :rtype: int
        :raises RuntimeError: If the database has not been initialized.
        """
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")
        self._cursor.execute(sql, values)
        self._conn.commit()
        return self._cursor.lastrowid

    def is_initialized(self):
        """
        Check whether the database connection has been fully initialized.

        :return: ``True`` if initialized, otherwise ``False``.
        :rtype: bool
        """
        return self._initialized

    def update_one(self, sql, values):
        """
        Execute a parameterized SQL update statement.

        :param sql: SQL update statement containing placeholders.
        :type sql: str
        :param values: Tuple or list of values to bind.
        :type values: tuple or list
        :return: Number of rows affected by the update.
        :rtype: int
        """
        # Execute update
        # print(f"sql: {sql}\nvalues: {values}")
        self._cursor.execute(sql, values)
        self._conn.commit()
        return self._cursor.rowcount

    def update_last_sync(self, table_name: str, ts: int):
        """
        Update or insert the ``last_sync_ts`` value for a table in ``sync_meta``.

        :param table_name: Table name whose sync timestamp is being updated.
        :type table_name: str
        :param ts: New last-sync timestamp.
        :type ts: int
        """
        self.execute_query(
            """
            INSERT INTO sync_meta (table_name, last_sync_ts)
            VALUES (?, ?)
            ON CONFLICT(table_name)
            DO UPDATE SET last_sync_ts = excluded.last_sync_ts
            """,
            (table_name, ts),
        )
