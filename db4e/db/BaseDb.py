"""
db4e/db/BaseDb.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

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

TYPE_TO_TABLE_MAP = {
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

TABLE_TO_TYPE_MAP = {v: k for k, v in TYPE_TO_TABLE_MAP.items()}


class BaseDb:

    def __init__(self, sql_db: SQLDb, log_file=None):
        self.sql_db = sql_db
        self.log = Db4ELogger(db4e_module=__name__, log_file=log_file)
        self._initialzed = False

    def add_timestamp_data(self, data):
        """Add timestamp data to a record"""
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

    def check_initialized(self):
        if not self.sql_db.is_initialized():
            raise RuntimeError(f"{__name__}: SQLDb not initialized")

        if not self._initialzed:
            self._init_db()
            self._initialzed = True

    def insert_one(self, db4e_obj):
        self.check_initialized()
        data = db4e_obj.to_dict()
        data = self.add_timestamp_data(data)
        # Stable key order (deterministic SQL generation)
        table_name = TYPE_TO_TABLE_MAP[type(db4e_obj)]
        columns = sorted(data.keys())
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        values = tuple(data[col] for col in columns)
        object_id = self.sql_db.insert_one(sql=sql, values=values)
        db4e_obj.id(object_id)
        return db4e_obj

    def update_one(self, db4e_obj):
        self.check_initialized()
        data = db4e_obj.to_dict()
        data = self.add_timestamp_data(data)
        table_name = TYPE_TO_TABLE_MAP[type(db4e_obj)]
        columns = sorted(data.keys())
        set_clause = ", ".join([f"{col}=?" for col in columns if col != DCol.ID])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE id=?"
        values = tuple(data[col] for col in columns if col != DCol.ID) + (
            db4e_obj.id(),
        )
        self.sql_db.update_one(sql=sql, values=values)
        return db4e_obj
