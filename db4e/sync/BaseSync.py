"""
db4e/sync/BaseSync.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

import time
from db4e.util.Db4ELogger import Db4ELogger


# db4e/sync/BaseSync.py
import time
from datetime import datetime


class BaseSync:
    def __init__(self, sql_db, ops_db=None, depl_db=None, mining_db=None, log=None):
        self.sql_db = sql_db
        self.ops_db = ops_db
        self.depl_db = depl_db
        self.mining_db = mining_db
        self.log = log

        # per-table sync timestamps
        self.last_sync = {}

    def get_last_sync(self, table_name: str) -> int:
        """Fetch last sync timestamp for a given table from sync_meta."""
        row = self.sql_db.fetchone(
            "SELECT last_sync_ts FROM sync_meta WHERE table_name = ?", (table_name,)
        )
        return row[0] if row else 0  # default: 0 = sync everything

    def update_last_sync(self, table_name: str, ts: int):
        """Persist updated last sync timestamp."""
        self.sql_db.execute(
            """
            INSERT INTO sync_meta (table_name, last_sync_ts)
            VALUES (?, ?)
            ON CONFLICT(table_name)
            DO UPDATE SET last_sync_ts=excluded.last_sync_ts
            """,
            (table_name, ts),
        )

    def get_updated_rows(self, table_name, since_ts):
        sql = f"""
            SELECT * FROM {table_name}
            WHERE updated_ts > ?
            ORDER BY updated_ts ASC
        """
        return self.sql_db.execute_query(sql, (since_ts,))
