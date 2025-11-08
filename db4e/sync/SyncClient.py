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

from db4e.db.SQLDb import SQLDb
from db4e.db.DeplDb import DeplDb
from db4e.db.OpsDb import OpsDb
from db4e.db.BaseDb import CLASS_STR_TO_TABLE_MAP

from db4e.util.Db4ELogger import Db4ELogger
from db4e.util.FormChecker import FormChecker

from db4e.constants.DSQL import DTable, DCol
from db4e.constants.DSync import DSync
from db4e.constants.DField import DField
from db4e.constants.DStatus import DStatus


SYNC_SCHEDULE = {
    # Deployment tables
    DTable.DB4E: 1,
    DTable.MONEROD: 1,
    DTable.MONEROD_REMOTE: 1,
    DTable.P2POOL: 1,
    DTable.P2POOL_INTERNAL: 1,
    DTable.P2POOL_REMOTE: 1,
    DTable.XMRIG: 1,
    DTable.XMRIG_REMOTE: 1,
    # Operations tables
    DTable.CURRENT_UPTIME: 30,
    DTable.TOTAL_UPTIME: 30,
    DTable.TUI_LOG_LINE: 1,
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

    def __init__(
        self,
        sql_db: SQLDb,
        server_url: str,
        ops_db: OpsDb,
        depl_db: DeplDb,
        log_file=None,
    ):
        """Constructor"""
        if log_file:
            self.log = Db4ELogger(db4e_module=__name__, log_file=log_file)
        self.ops_db = ops_db
        self.sql_db = sql_db
        self.fc = FormChecker(ops_db=ops_db, depl_db=depl_db)
        self.server_url = server_url.rstrip("/")
        self._running = False
        self._task = None

    async def add_deployment(self, depl_request):
        """Send a "create new deployment" request to the sync server."""
        depl_obj = depl_request.get(DField.ELEMENT)
        type_str = depl_request.get(DField.ELEMENT_TYPE).lower()
        depl_table = CLASS_STR_TO_TABLE_MAP[type_str]

        # Check that the form data is complete and there's no instance using that
        # name already.
        if not self.fc.valid(depl_obj):
            return self.ops_db.get_tui_log()

        payload = {
            DSync.TABLE_NAME: depl_table,
            DSync.ELEMENT: depl_obj.to_dict(),
        }
        url = f"{self.server_url}/add/{depl_table}"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                # Force a sync of the deployment table and the Console log table
                await self.sync_table(depl_table, since_ts=0)
                await self.sync_table(DTable.TUI_LOG_LINE, since_ts=0)
                return self.ops_db.get_tui_log()

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            self.ops_db.add_tui_log_line(
                tracked_instance=depl_obj.instance(),
                tracked_type=depl_obj.elem_type().lower(),
                status=DStatus.ERROR,
                operation=DField.NEW,
                message=str(e),
            )
            return self.ops_db.get_tui_log()

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
            print(f"Syncing {table_name} row: {row}")
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
        self.sql_db.update_last_sync(table_name, int(time.time()))

    async def _sync_loop(self):
        """Main sync scheduler loop."""
        self._running = True
        last_sync_times = {tbl: 0 for tbl in SYNC_SCHEDULE}
        while self._running:
            start_time = time.time()
            for table, interval in SYNC_SCHEDULE.items():
                last_sync = last_sync_times[table]
                if start_time - last_sync >= interval:
                    # print(f"[SyncClient] Checking {table} - last sync: {last_sync}")
                    try:
                        since_ts = self.sql_db.get_last_sync(table)
                        await self.sync_table(table, since_ts=since_ts)
                    except RuntimeError:
                        # We get this when the app is run for the first time. The initial
                        # install hasn't been completed and the DB is not initialized
                        pass
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
