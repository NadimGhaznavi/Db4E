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
from db4e.db.BaseDb import CLASS_TO_TABLE_MAP, CLASS_STR_TO_TABLE_MAP

from db4e.recs.monero.Db4E import Db4E

from db4e.mgr.BootstrapMgr import BootstrapMgr

from db4e.util.Db4ELogger import Db4ELogger
from db4e.util.FormChecker import FormChecker

from db4e.recs.monero.P2Pool import P2Pool

from db4e.constants.DSQL import DTable, DCol
from db4e.constants.DSync import DSync
from db4e.constants.DField import DField
from db4e.constants.DStatus import DStatus
from db4e.constants.DLabel import DLabel
from db4e.constants.DElem import DElem
from db4e.constants.DSync import DSync


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
    # Health State table
    DTable.HEALTH_STATE: 5,
}


class SyncClient:
    """
    Sync client that coordinates deployments and table synchronization.
    """

    def __init__(
        self,
        sql_db: SQLDb,
        server_url: str,
        ops_db: OpsDb,
        depl_db: DeplDb,
        bs_mgr: BootstrapMgr,
        log_file=None,
    ):
        """
        Initialize the sync client with DB handles and server configuration.

        :param sql_db: SQL database handle for local sync state.
        :type sql_db: SQLDb
        :param server_url: Sync server base URL.
        :type server_url: str
        :param ops_db: Operations database handle.
        :type ops_db: OpsDb
        :param depl_db: Deployment database handle.
        :type depl_db: DeplDb
        :param bs_mgr: Bootstrap manager for install paths.
        :type bs_mgr: BootstrapMgr
        :param log_file: Optional log file path for the logger.
        :type log_file: str or None
        :return: None
        :rtype: None
        """
        if log_file:
            self.log = Db4ELogger(db4e_module=__name__, log_file=log_file)
        self.ops_db = ops_db
        self.sql_db = sql_db
        self.bs_mgr = bs_mgr
        self.fc = FormChecker(ops_db=ops_db, depl_db=depl_db)
        self.server_url = server_url.rstrip("/")
        self._running = False
        self._task = None

    async def add_deployment(self, depl_request):
        """
        Send a "create new deployment" request to the sync server.

        :param depl_request: Deployment request payload.
        :type depl_request: dict
        :return: TUI log contents.
        :rtype: list
        """
        depl_obj = depl_request.get(DField.ELEMENT)
        type_str = depl_request.get(DField.ELEMENT_TYPE).lower()
        depl_table = CLASS_STR_TO_TABLE_MAP[type_str]

        # Check if an instance with the same name already exists
        if self.fc.instance_exists(depl_obj):
            return self.ops_db.get_tui_log()

        # Check that the form data is complete
        if not self.fc.valid(depl_obj):
            return self.ops_db.get_tui_log()

        # Special case: Don't allow p2pool instances called Main, Mini or Nano
        # These are reserved for the internal p2pool instances
        if type(depl_obj) == P2Pool and depl_obj.instance() in [
            DLabel.MAIN_CHAIN,
            DLabel.MINI_CHAIN,
            DLabel.NANO_CHAIN,
        ]:
            self.ops_db.add_tui_log_line(
                tracked_instance=depl_obj.instance(),
                tracked_type=DElem.P2POOL,
                operation=DField.NEW,
                status=DStatus.ERROR,
                message="Invalid Name",
                details="Main, Mini, and Nano are reserved names",
            )
            return

        payload = {
            DSync.TABLE_NAME: depl_table,
            DSync.ELEMENT: depl_obj.to_dict(),
        }
        url = f"{self.server_url}/add/{depl_table}"

        return await self._send_request(
            depl_table=depl_table, depl_obj=depl_obj, url=url, payload=payload
        )

    async def delete_deployment(self, depl_request):
        """
        Send a "delete deployment" request to the sync server.

        :param depl_request: Deployment request payload.
        :type depl_request: dict
        :return: TUI log contents.
        :rtype: list
        """
        depl_obj = depl_request.get(DField.ELEMENT)
        type_str = depl_request.get(DField.ELEMENT_TYPE).lower()
        depl_table = CLASS_STR_TO_TABLE_MAP[type_str]

        payload = {
            DSync.TABLE_NAME: depl_table,
            DSync.ELEMENT: depl_obj.to_dict(),
        }
        url = f"{self.server_url}/delete/{depl_table}"

        return await self._send_request(
            depl_table=depl_table, depl_obj=depl_obj, url=url, payload=payload
        )

    async def disable_deployment(self, depl_request):
        """
        Send a "disable deployment" request to the sync server.
        """
        depl_obj = depl_request.get(DField.ELEMENT)
        type_str = depl_request.get(DField.ELEMENT_TYPE).lower()
        depl_table = CLASS_STR_TO_TABLE_MAP[type_str]

        payload = {
            DSync.ELEMENT: depl_obj.to_dict(),
            DSync.TABLE_NAME: depl_table,
        }
        url = f"{self.server_url}/disable"

        return await self._send_request(
            depl_table=depl_table, depl_obj=depl_obj, url=url, payload=payload
        )

    async def enable_deployment(self, depl_request):
        """
        Send a "enable deployment" request to the sync server.
        """
        depl_obj = depl_request.get(DField.ELEMENT)
        type_str = depl_request.get(DField.ELEMENT_TYPE).lower()
        depl_table = CLASS_STR_TO_TABLE_MAP[type_str]

        payload = {
            DSync.ELEMENT: depl_obj.to_dict(),
            DSync.TABLE_NAME: depl_table,
        }
        url = f"{self.server_url}/enable"

        return await self._send_request(
            depl_table=depl_table, depl_obj=depl_obj, url=url, payload=payload
        )

    async def get_log(self, depl_request):
        """
        Send a "get log" request to the sync server
        """
        depl_obj = depl_request.get(DField.ELEMENT)
        type_str = depl_request.get(DField.ELEMENT_TYPE).lower()
        depl_table = CLASS_STR_TO_TABLE_MAP[type_str]

        payload = {
            DSync.ELEMENT: depl_obj.to_dict(),
            DSync.TABLE_NAME: depl_table,
        }
        url = f"{self.server_url}/get_log"
        return await self._send_log_request(
            depl_table=depl_table, depl_obj=depl_obj, url=url, payload=payload
        )

    def _merge_row(self, table_name, row):
        """
        Insert or update a single row in the local DB.

        :param table_name: Table name to update.
        :type table_name: str
        :param row: Row payload to merge.
        :type row: dict
        :return: None
        :rtype: None
        """
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
        max_updated_ts = self.sql_db.get_max_updated_ts(table_name)
        self.sql_db.update_last_sync(table_name, max_updated_ts)

    async def ping(self):
        url = f"{self.server_url}/ping"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json={DSync.PING: True})
                resp.raise_for_status()
                return True

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return False

    async def _send_log_rquest(self, depl_table, depl_obj, url, payload):
        """
        Send a JSON request to the sync server and refresh local tables.

        :param depl_table: Deployment table name.
        :type depl_table: str
        :param depl_obj: Deployment object being updated.
        :type depl_obj: object
        :param url: Target URL for the request.
        :type url: str
        :param payload: Request JSON payload.
        :type payload: dict
        :return: Log lines
        :rturn: list
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                return resp[DSync.LOG_LINES]

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            elem_type = CLASS_TO_TABLE_MAP[type(depl_obj)]
            self.ops_db.add_tui_log_line(
                tracked_instance=depl_obj.instance(),
                tracked_type=elem_type,
                status=DStatus.ERROR,
                operation=DField.NEW,
                message=str(e),
            )

    async def _send_request(self, depl_table, depl_obj, url, payload):
        """
        Send a JSON request to the sync server and refresh local tables.

        :param depl_table: Deployment table name.
        :type depl_table: str
        :param depl_obj: Deployment object being updated.
        :type depl_obj: object
        :param url: Target URL for the request.
        :type url: str
        :param payload: Request JSON payload.
        :type payload: dict
        :return: TUI log contents.
        :rtype: list
        """
        # print(
        #    f"update_last_sync(): depl_table: {depl_table}, depl_obj: {depl_obj}, url: {url}, payload: {payload}"
        # )
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                # Force a sync of the deployment table and the Console log table
                await self.sync_table(depl_table, since_ts=0)
                await self.sync_table(DTable.TUI_LOG_LINE, since_ts=0)
                return self.ops_db.get_tui_log()

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            elem_type = CLASS_TO_TABLE_MAP[type(depl_obj)]
            self.ops_db.add_tui_log_line(
                tracked_instance=depl_obj.instance(),
                tracked_type=elem_type,
                status=DStatus.ERROR,
                operation=DField.NEW,
                message=str(e),
            )
            return self.ops_db.get_tui_log()

    async def start(self):
        """
        Start the background sync loop task.

        :return: None
        :rtype: None
        """
        if not self._task:
            self._task = asyncio.create_task(self._sync_loop())

    async def stop(self):
        """
        Stop the background sync loop task.

        :return: None
        :rtype: None
        """
        self._running = False
        if self._task:
            await self._task
            self._task = None

    async def _sync_loop(self):
        """
        Run the main sync scheduler loop.

        :return: None
        :rtype: None
        """
        self._running = True
        last_sync_times = {tbl: 0 for tbl in SYNC_SCHEDULE}
        while self._running:
            start_time = time.time()
            for table, interval in SYNC_SCHEDULE.items():
                last_sync = last_sync_times[table]
                if start_time - last_sync >= interval:
                    try:
                        since_ts = self.sql_db.get_last_sync(table)
                        await self.sync_table(table, since_ts=since_ts)
                    except RuntimeError:
                        pass
                    last_sync_times[table] = start_time

            # Sleep a bit before checking again
            await asyncio.sleep(1)

    async def sync_table(self, table_name: str, since_ts: int = 0, limit: int = 1000):
        """
        Synchronize a table from the server into the local DB.

        :param table_name: Table name to sync.
        :type table_name: str
        :param since_ts: Timestamp cutoff (exclusive).
        :type since_ts: int
        :param limit: Maximum number of rows to fetch.
        :type limit: int
        :return: Sync payload containing rows and metadata.
        :rtype: dict
        """
        url = f"{self.server_url}/sync/{table_name}?since={since_ts}&limit={limit}"
        # url = f"{self.server_url}/sync/{table_name}?since=0"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                payload = resp.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return {}
        rows = payload.get("rows", [])
        for row in rows:
            self._merge_row(table_name, row)
        return payload

    async def update_deployment(self, depl_request):
        """
        Send an "update deployment" request to the sync server.

        :param depl_request: Deployment request payload.
        :type depl_request: dict
        :return: TUI log contents.
        :rtype: list
        """
        depl_obj = depl_request.get(DField.ELEMENT)
        depl_table = CLASS_TO_TABLE_MAP[type(depl_obj)]

        # Check that the form data is complete
        if not self.fc.valid(depl_obj):
            return self.ops_db.get_tui_log()

        payload = {
            DSync.TABLE_NAME: depl_table,
            DSync.ELEMENT: depl_obj.to_dict(),
        }
        url = f"{self.server_url}/update/{depl_table}"

        # We need to handle the case where the user updated the vendor director
        # that houses the SQLite DB.
        # db_closed = False
        # if type(depl_obj) == Db4E and depl_obj.vendor_dir() != self.bs_mgr.get_dir(
        #    DDir.VENDOR
        # ):
        #    self.sql_db.close()
        #    db_closed = True

        await self._send_request(
            depl_table=depl_table, depl_obj=depl_obj, url=url, payload=payload
        )

        # if db_closed:
        #    self.sql_db.initialize(db_dir=self.bs_mgr.get_dir(DDir.VENDOR))

        return self.ops_db.get_tui_log()
