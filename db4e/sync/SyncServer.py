"""
db4e/sync/SyncServer.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.sync.BaseSync import BaseSync
from fastapi import APIRouter, Query
import time


from db4e.db.SQLDb import SQLDb

router = APIRouter(prefix="/sync", tags=["sync"])


class SyncServer:
    """
    Sync server helper for serving updated table rows.
    """

    def __init__(self, sql_db: SQLDb, log_file=None):
        """
        Initialize the sync server with an SQL database handle.

        :param sql_db: SQL database handle for table access.
        :type sql_db: SQLDb
        :param log_file: Optional log file path (unused).
        :type log_file: str or None
        :return: None
        :rtype: None
        """
        self.sql_db = sql_db

    def get_rows_since(self, table_name: str, since_ts: int = 0, limit: int = 1000):
        """
        Return rows updated after a given timestamp.

        :param table_name: Table name to query.
        :type table_name: str
        :param since_ts: Timestamp cutoff (exclusive).
        :type since_ts: int
        :param limit: Maximum number of rows to return.
        :type limit: int
        :return: Rows as dictionaries.
        :rtype: list
        """
        sql = f"""
            SELECT *
            FROM {table_name}
            WHERE updated_ts > ?
            ORDER BY updated_ts ASC
            LIMIT ?
        """
        return [dict(r) for r in self.sql_db.execute_query(sql, (since_ts, limit))]


sync_server: SyncServer | None = None


def init_sync_server(sql_db: SQLDb):
    """
    Initialize the global sync server instance.

    :param sql_db: SQL database handle for the sync server.
    :type sql_db: SQLDb
    :return: FastAPI router for sync endpoints.
    :rtype: APIRouter
    """
    global sync_server
    sync_server = SyncServer(sql_db)
    return router


@router.get("/{table_name}")
async def get_table_data(
    table_name: str,
    since_ts: int = Query(0, alias="since"),
    limit: int = Query(1000),
):
    """
    Return rows for a table updated after the provided timestamp.

    :param table_name: Table name to query.
    :type table_name: str
    :param since_ts: Timestamp cutoff (exclusive).
    :type since_ts: int
    :param limit: Maximum number of rows to return.
    :type limit: int
    :return: Response payload with rows and latest timestamp.
    :rtype: dict
    """
    if not sync_server:
        raise RuntimeError("SyncServer not initialized")
    # print(f"Table: {table_name}, since: {since_ts}, limit: {limit}")
    rows = sync_server.get_rows_since(table_name, since_ts, limit)
    latest = max((r["updated_ts"] for r in rows), default=since_ts)
    return {
        "table": table_name,
        "rows": rows,
        "latest": latest,
    }
