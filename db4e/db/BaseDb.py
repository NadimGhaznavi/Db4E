# db4e/db/BaseDb.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

# Supporting modules
from datetime import datetime

# The SQLite interface module
from db4e.db.SQLDb import SQLDb

# The logging module
from db4e.util.Db4ELogger import Db4ELogger

# Column definitions
from db4e.constants.DSQL import DCol, DTable

# Monero classes
from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig
from db4e.recs.monero.XMRigRemote import XMRigRemote

# Mining classes
from db4e.recs.mining.BlockFoundEvent import BlockFoundEvent
from db4e.recs.mining.ChainHashrate import ChainHashrate
from db4e.recs.mining.ChainMiners import ChainMiners
from db4e.recs.mining.MinerHashrate import MinerHashrate
from db4e.recs.mining.PoolHashrate import PoolHashrate
from db4e.recs.mining.ShareFoundEvent import ShareFoundEvent
from db4e.recs.mining.SharePosition import SharePosition
from db4e.recs.mining.XMRPayment import XMRPayment

# Ops record classes
from db4e.recs.ops.CurrentUptime import CurrentUptime
from db4e.recs.ops.TotalUptime import TotalUptime
from db4e.recs.ops.TUILogLine import TUILogLine

# Constants
from db4e.constants.DElem import DElem


CLASS_TO_TABLE_MAP = {
    # Deployment records
    Db4E: DTable.DB4E,
    MoneroD: DTable.MONEROD,
    MoneroDRemote: DTable.MONEROD_REMOTE,
    P2Pool: DTable.P2POOL,
    P2PoolRemote: DTable.P2POOL_REMOTE,
    P2PoolInternal: DTable.P2POOL_INTERNAL,
    XMRig: DTable.XMRIG,
    XMRigRemote: DTable.XMRIG_REMOTE,
    # Mining records
    BlockFoundEvent: DTable.BLOCK_FOUND_EVENT,
    ChainHashrate: DTable.CHAIN_HASHRATE,
    ChainMiners: DTable.CHAIN_MINERS,
    MinerHashrate: DTable.MINER_HASHRATE,
    PoolHashrate: DTable.POOL_HASHRATE,
    ShareFoundEvent: DTable.SHARE_FOUND_EVENT,
    SharePosition: DTable.SHARE_POSITION,
    XMRPayment: DTable.XMR_PAYMENT,
    # Ops records
    CurrentUptime: DTable.CURRENT_UPTIME,
    TotalUptime: DTable.TOTAL_UPTIME,
    TUILogLine: DTable.TUI_LOG_LINE,
}

CLASS_STR_TO_TABLE_MAP = {
    DElem.DB4E: DTable.DB4E,
    DElem.MONEROD: DTable.MONEROD,
    DElem.MONEROD_REMOTE: DTable.MONEROD_REMOTE,
    DElem.P2POOL: DTable.P2POOL,
    DElem.P2POOL_REMOTE: DTable.P2POOL_REMOTE,
    DElem.P2POOL_INTERNAL: DTable.P2POOL_INTERNAL,
    DElem.XMRIG: DTable.XMRIG,
    DElem.XMRIG_REMOTE: DTable.XMRIG_REMOTE,
}

CLASS_STR_TO_CLASS_MAP = {
    DElem.DB4E: Db4E,
    DElem.MONEROD: MoneroD,
    DElem.MONEROD_REMOTE: MoneroDRemote,
    DElem.P2POOL: P2Pool,
    DElem.P2POOL_REMOTE: P2PoolRemote,
    DElem.P2POOL_INTERNAL: P2PoolInternal,
    DElem.XMRIG: XMRig,
    DElem.XMRIG_REMOTE: XMRigRemote,
}

TABLE_TO_CLASS_STR_MAP = {v: k for k, v in CLASS_STR_TO_TABLE_MAP.items()}

TABLE_TO_CLASS_MAP = {v: k for k, v in CLASS_TO_TABLE_MAP.items()}


class BaseDb:
    """
    BaseDb
    ======

    Provides the abstract base class for all database access layers in Db4E.

    This module defines:

    - Static mappings between record classes and database tables.
    - Bidirectional mappings between class identifiers and record types.
    - ``BaseDb``: an abstract parent class that wraps ``SQLDb`` and provides
    timestamp handling, insert/update helpers, and initialization patterns.

    Concrete database managers must subclass ``BaseDb`` and implement ``_init_db()``.
    """
    def __init__(self, sql_db: SQLDb, log_file=None):
        """
        Initialize the base database manager.

        :param sql_db: The underlying SQL database interface.
        :type sql_db: SQLDb
        :param log_file: Optional log file path for the manager.
        :type log_file: str or None
        """
        self.sql_db = sql_db
        self.log = Db4ELogger(db4e_module=__name__, log_file=log_file)
        self._initialized = False
        if sql_db.is_initialized():
            self.initialize()


    def add_timestamp_data(self, data):
        """
        Add individual timestamp columns to a row dictionary.

        Adds the following keys:

        - ``updated_y`` — year  
        - ``updated_mo`` — month  
        - ``updated_d`` — day  
        - ``updated_h`` — hour  
        - ``updated_mi`` — minute  
        - ``updated_s`` — second  

        :param data: Dictionary representing a database row.
        :type data: dict
        :return: The same dictionary with timestamp fields added.
        :rtype: dict
        """
        now = datetime.now()
        data.update(
            {
                DCol.UPDATED_YEAR: now.year,
                DCol.UPDATED_MONTH: now.month,
                DCol.UPDATED_DAY: now.day,
                DCol.UPDATED_HOUR: now.hour,
                DCol.UPDATED_MINUTE: now.minute,
                DCol.UPDATED_SECOND: now.second,
            }
        )
        return data

    def add_updated_ts_column(self, table_name):
        """
        Add a computed (generated) ``updated_ts`` column to a table, if missing.

        ``updated_ts`` is stored as a Unix timestamp computed from the existing
        ``updated_*`` fields. An index is also created on ``updated_ts``.

        This method silently ignores ``ALTER TABLE`` errors if the column
        already exists.

        :param table_name: Name of the table to modify.
        :type table_name: str
        """
        # Avoid raising an exception because the index already exists
        try:
            self.sql_db.executescript(
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN updated_ts INTEGER
                    GENERATED ALWAYS AS (
                        (strftime('%s', 
                            printf('%04d-%02d-%02d %02d:%02d:%02d',
                                updated_y, updated_mo, updated_d, updated_h, updated_mi, updated_s
                            )
                        ))
                    ) VIRTUAL;
                """
            )
        except:
            pass

        index = f"idx_{table_name}_updated_ts"
        self.sql_db.executescript(
            f"""
                CREATE INDEX IF NOT EXISTS {index}
                ON {table_name}(updated_ts);    
            """
        )

    def check_initialized(self):
        """
        Ensure both the underlying SQL database and this manager are initialized.

        If ``sql_db`` becomes initialized, this method will also trigger
        ``initialize()`` so the subclass can perform table setup.
        """
        self.sql_db.check_initialized()
        if self.sql_db.is_initialized():
            self.initialize()
        else:
            self._initialized = False

    def initialize(self):
        """
        Initialize the database manager.

        Calls ``_init_db()`` — subclasses must implement this method to create
        tables and perform table-specific setup.
        """
        self._init_db()
        self._initialized = True

    def _init_db(self):
        """
        Abstract hook for database initialization.

        Subclasses must override this to create their required tables.

        :raises NotImplementedError: Always.
        """        
        raise NotImplementedError

    def get_records_since(self, table_name: str, since_ts: int, hourly=False):
        """
        Retrieve records updated after a given timestamp.

        :param table_name: Table to query.
        :type table_name: str
        :param since_ts: Timestamp threshold.
        :type since_ts: int
        :param hourly: Use ``updated_hourly_ts`` instead of ``updated_ts``.
        :type hourly: bool
        :return: Rows updated since the timestamp.
        :rtype: list[sqlite3.Row]
        """
        self.check_initialized()
        ts_col = "updated_hourly_ts" if hourly else "updated_ts"

        sql = f"""
            SELECT * FROM {table_name}
            WHERE {ts_col} > ?
            ORDER BY {ts_col} ASC
        """
        return self.sql_db.execute_query(sql, (since_ts,))

    def insert_one(self, db4e_obj):
        """
        Insert a new record into its mapped table.

        Workflow:

        - Convert the record object to a dict.
        - Add timestamp columns.
        - Determine the correct table based on its class.
        - Perform deterministic column sorting for stable SQL generation.
        - Insert the row and update the object's ``id``.

        :param db4e_obj: Record object to insert.
        :type db4e_obj: Db4EBase (or subclass)
        :return: The same object with its ``id`` populated.
        :rtype: object
        """
        self.check_initialized()
        data = db4e_obj.to_dict()
        data = self.add_timestamp_data(data)
        # Stable key order (deterministic SQL generation)
        table_name = CLASS_TO_TABLE_MAP[type(db4e_obj)]
        columns = sorted(data.keys())
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        values = tuple(data[col] for col in columns)
        object_id = self.sql_db.insert_one(sql=sql, values=values)
        db4e_obj.id(object_id)
        return db4e_obj

    def is_initialized(self):
        """
        Check whether this database manager has completed initialization.

        :return: ``True`` if initialized, otherwise ``False``.
        :rtype: bool
        """
        return self._initialized

    def update_one(self, db4e_obj):
        """
        Update an existing record in its mapped table.

        Workflow:

        - Convert the record to a dict.
        - Add timestamp fields.
        - Build a dynamic ``SET`` clause for all non-ID columns.
        - Bind values in deterministic column order.

        :param db4e_obj: Record object containing updated values.
        :type db4e_obj: object
        :return: The updated object.
        :rtype: object
        """
        self.check_initialized()
        data = db4e_obj.to_dict()
        data = self.add_timestamp_data(data)
        table_name = CLASS_TO_TABLE_MAP[type(db4e_obj)]
        columns = sorted(data.keys())
        set_clause = ", ".join([f"{col}=?" for col in columns if col != DCol.ID])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE id=?"
        values = tuple(data[col] for col in columns if col != DCol.ID) + (
            db4e_obj.id(),
        )
        print(f"BaseDb:update_one(): SQL: {sql}\nVALUES: {values}")
        self.sql_db.update_one(sql=sql, values=values)
        return db4e_obj

    def upsert_records(self, table_name: str, rows):
        """
        Insert or update (UPSERT) a list of row dictionaries into a table.

        Uses SQLite ``ON CONFLICT(id) DO UPDATE`` to merge changes.

        :param table_name: Target table.
        :type table_name: str
        :param rows: Rows to upsert, typically from ``sqlite3.Row`` mappings.
        :type rows: list[dict]
        """
        if not rows:
            return
        self.check_initialized()

        # Extract column names from the first row
        columns = rows[0].keys()
        placeholders = ", ".join(["?"] * len(columns))
        col_list = ", ".join(columns)

        sql = f"""
            INSERT INTO {table_name} ({col_list})
            VALUES ({placeholders})
            ON CONFLICT(id) DO UPDATE SET
            {", ".join([f"{col}=excluded.{col}" for col in columns if col != "id"])}
        """
        for row in rows:
            values = tuple(row[c] for c in columns)
            self.sql_db.execute_query(sql, values)
