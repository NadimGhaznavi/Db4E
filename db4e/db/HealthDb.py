# db4e/db/HealthDb.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0


# Health messages are stored as HealthMsg instances
from db4e.util.Helper import HealthMsg

# Logging DB
from db4e.util.Db4ELogger import Db4ELogger

# The module that interfaces with SQLite3
from db4e.db.SQLDb import SQLDb

# Base domain DB module
from db4e.db.BaseDb import BaseDb

# Db4E constants
from db4e.constants.DModule import DModule
from db4e.constants.DSQL import DTable, DCol


class HealthDb(BaseDb):
    """
    Health database access layer.

    Houses the health messages for the deployed elements.
    """

    def __init__(self, sql_db: SQLDb, log_file=None):
        """
        Initialize the deployment database manager.

        :param sql_db: Initialized SQL database wrapper.
        :type sql_db: SQLDb
        :param log_file: Optional log file path.
        :type log_file: str or None
        """
        super().__init__(sql_db=sql_db, log_file=log_file)
        self.sql_db = sql_db
        self.log = Db4ELogger(db4e_module=DModule.HEALTH_DB, log_file=log_file)

    def get_msgs(self, instance: str, elem_type: str):
        if not self._initialized:
            raise RuntimeError("SQLDb not initialized")

        sql = f"""
            SELECT *
            FROM {DTable.HEALTH_STATE}
            WHERE {DCol.INSTANCE} = ?
            AND {DCol.ELEMENT_TYPE} = ?
        """

        params = (instance, elem_type)
        return self.sql_db.execute_query(sql, params)

    def _init_db(self):
        """
        Initialize the health table in the SQLite database.
        """
        self.sql_db.executescript(
            f"""
            CREATE TABLE IF NOT EXISTS {DTable.HEALTH_STATE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {DCol.INSTANCE} TEXT NOT NULL,
                {DCol.ELEMENT_TYPE} TEXT NOT NULL,
                {DCol.CATEGORY} TEXT NOT NULL,
                {DCol.STATUS} TEXT NOT NULL,
                {DCol.MESSAGE} TEXT,
                {DCol.UPDATED_YEAR} INTEGER NOT NULL,
                {DCol.UPDATED_MONTH} INTEGER NOT NULL,
                {DCol.UPDATED_DAY} INTEGER NOT NULL,
                {DCol.UPDATED_HOUR} INTEGER NOT NULL,
                {DCol.UPDATED_MINUTE} INTEGER NOT NULL,
                {DCol.UPDATED_SECOND} INTEGER NOT NULL,
                UNIQUE({DCol.INSTANCE}, {DCol.ELEMENT_TYPE}, {DCol.CATEGORY})
            );
            """
        )

        # Add an updated_ts column to the table (for syncing)
        self.add_updated_ts_column(DTable.HEALTH_STATE)

    def upsert_one(self, health_msg: HealthMsg):
        msg_dict = self.add_timestamp_data(health_msg.to_dict())

        sql = f"""
            INSERT INTO {DTable.HEALTH_STATE} (
                {DCol.INSTANCE},
                {DCol.ELEMENT_TYPE},
                {DCol.CATEGORY},
                {DCol.STATUS},
                {DCol.MESSAGE},
                {DCol.UPDATED_YEAR},
                {DCol.UPDATED_MONTH},
                {DCol.UPDATED_DAY},
                {DCol.UPDATED_HOUR},
                {DCol.UPDATED_MINUTE},
                {DCol.UPDATED_SECOND}
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT({DCol.INSTANCE}, {DCol.ELEMENT_TYPE}, {DCol.CATEGORY})
            DO UPDATE SET
                {DCol.STATUS} = excluded.{DCol.STATUS},
                {DCol.MESSAGE} = excluded.{DCol.MESSAGE},
                {DCol.UPDATED_YEAR} = excluded.{DCol.UPDATED_YEAR},
                {DCol.UPDATED_MONTH} = excluded.{DCol.UPDATED_MONTH},
                {DCol.UPDATED_DAY} = excluded.{DCol.UPDATED_DAY},
                {DCol.UPDATED_HOUR} = excluded.{DCol.UPDATED_HOUR},
                {DCol.UPDATED_MINUTE} = excluded.{DCol.UPDATED_MINUTE},
                {DCol.UPDATED_SECOND} = excluded.{DCol.UPDATED_SECOND}
        """

        params = (
            health_msg.instance,
            health_msg.elem_type,
            health_msg.category,
            health_msg.status,
            health_msg.message,
            msg_dict[DCol.UPDATED_YEAR],
            msg_dict[DCol.UPDATED_MONTH],
            msg_dict[DCol.UPDATED_DAY],
            msg_dict[DCol.UPDATED_HOUR],
            msg_dict[DCol.UPDATED_MINUTE],
            msg_dict[DCol.UPDATED_SECOND],
        )

        self.sql_db.execute_query(sql, params)
