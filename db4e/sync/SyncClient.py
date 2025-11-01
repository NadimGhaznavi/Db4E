"""
db4e/sync/SyncClient.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

import httpx
import time
import asyncio

from db4e.util.Db4ELogger import Db4ELogger
from db4e.db.SQLDb import SQLDb
from db4e.constants.DSQL import DTable, DCol

SYNC_SCHEDULE = {
    # Deployment tables
    DTable.DB4E: 5,
    DTable.MONEROD: 5,
    DTable.MONEROD_REMOTE: 5,
    DTable.P2POOL: 5,
    DTable.P2POOL_INTERNAL: 5,
    DTable.P2POOL_REMOTE: 5,
    DTable.XMRIG: 5,
    DTable.XMRIG_REMOTE: 5,
    # Operations tables
    DTable.CURRENT_UPTIME: 30,
    DTable.TOTAL_UPTIME: 30,
    DTable.TUI_LOG_LINE: 5,
    # Mining tables
    DTable.BLOCK_FOUND_EVENT: 60,
    DTable.CHAIN_HASHRATE: 60,
    DTable.CHAIN_MINERS: 60,
    DTable.MINER_HASHRATE: 60,
    DTable.POOL_HASHRATE: 60,
    DTable.SHARE_FOUND_EVENT: 60,
    DTable.SHARE_POSITION: 60,
    DTable.XMR_PAYMENT: 60,
}


class SyncClient:
    """Standalone SyncClient integrated with the TUI."""

    def __init__(self, sql_db: SQLDb, server_url: str, log_file=None):
        """Constructor"""
        if log_file:
            self.log = Db4ELogger(db4e_module=__name__, log_file=log_file)
        self.sql_db = sql_db
        self.server_url = server_url.rstrip("/")
        self._running = False
        self._task = None

    async def sync_table(self, table_name: str, since_ts: int = 0, limit: int = 1000):
        url = f"{self.server_url}/sync/{table_name}?since={since_ts}&limit={limit}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                payload = resp.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"[SyncClient] Failed to sync {table_name}: {e}")
            return {}

        rows = payload.get("rows", [])
        for row in rows:
            self._merge_row(table_name, row)
        return payload

    def _merge_row(self, table_name, row):
        """Insert or update a single row in the local DB."""
        # Don't include the generated updated_ts column
        row.pop(DCol.UPDATED_TS, None)
        cols = list(row.keys())
        placeholders = ", ".join(["?"] * len(cols))
        updates = ", ".join(f"{col}=excluded.{col}" for col in cols if col != "id")
        sql = f"""
            INSERT INTO {table_name} ({', '.join(cols)})
            VALUES ({placeholders})
            ON CONFLICT(id) DO UPDATE SET {updates};
        """
        self.sql_db.execute_query(sql, tuple(row.values()))

    async def _sync_loop(self):
        """Main sync scheduler loop."""
        self._running = True
        last_sync_times = {tbl: 0 for tbl in SYNC_SCHEDULE}
        while self._running:
            start_time = time.time()
            for table, interval in SYNC_SCHEDULE.items():
                last_sync = last_sync_times[table]
                if start_time - last_sync >= interval:
                    print(f"[SyncClient] Checking {table} - last sync: {last_sync}")
                    since_ts = self.sql_db.get_last_sync(table)
                    await self.sync_table(table, since_ts=since_ts)
                    self.sql_db.update_last_sync(table, int(time.time()))
                    last_sync_times[table] = start_time

            # Sleep a bit before checking again
            await asyncio.sleep(1)

    async def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._sync_loop())

    async def stop(self):
        self._running = False
        if self._task:
            await self._task
            self._task = None
