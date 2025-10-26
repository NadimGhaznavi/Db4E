"""
db4e/db/OpsDb.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

# Supporting modules
import time

# Ops classes
from db4e.recs.ops.CurrentUptime import CurrentUptime
from db4e.recs.ops.TotalUptime import TotalUptime
from db4e.recs.ops.TUILogLine import TUILogLine


# The module that interfaces with SQLite3
from db4e.db.SQLDb import SQLDb

# Db4E logging module
from db4e.util.Db4ELogger import Db4ELogger

# Constants
from db4e.constants.DModule import DModule


class OpsDb:

    def __init__(self, sql_db: SQLDb, log_file=None):
        self.sql_db = sql_db
        if log_file:
            self.log = Db4ELogger(db4e_module=DModule.OPS_DB, log_file=log_file)
        self._init_db()
        # TODO close off any open current_uptime records

    def get_ops_events(self):
        pass

    def add_start_event(self, elem_type, instance):
        # Create a new current_uptime record
        cur_uptime = CurrentUptime(tracked_type=elem_type, tracked_instance=instance)
        cur_uptime.start_time(int(round(time.time())))
        self.insert_one(cur_uptime)

    def add_stop_event(self, elem_type, instance):
        # Get the current uptime record where the stop event is not set
        rec = self.get_open_cur_uptime_rec(elem_type, instance)
        current_uptime = CurrentUptime(
            tracked_type=elem_type, tracked_instance=instance, rec=rec
        )

        if not current_uptime:
            self.log.error(f"No current uptime record found for {elem_type}/{instance}")
            return

        current_uptime.stop_time(int(round(time.time())))
        current_uptime.uptime_secs(
            current_uptime.stop_time() - current_uptime.start_time()
        )
        self.update_one(current_uptime)

        # Update existing or create new total uptime record
        total_uptime = self.get_total_uptime_rec(elem_type, instance)
        update = True
        if not total_uptime:
            update = False
            total_uptime = TotalUptime(elem_type=elem_type, instance=instance)
        total_uptime.uptime_secs(
            total_uptime.uptime_secs() + current_uptime.uptime_secs()
        )
        if update:
            self.update_one(total_uptime)
        else:
            self.insert_one(total_uptime)

    def get_open_cur_uptime_rec(self, elem_type, instance) -> CurrentUptime:
        sql = f"SELECT * FROM current_uptime WHERE tracked_type=? AND tracked_instance=? AND stop_time IS NULL"
        return self.sql_db.execute_query(sql, (elem_type, instance))[0]

    def get_total_uptime_rec(self, elem_type, instance) -> TotalUptime:
        sql = f"SELECT * FROM total_uptime WHERE tracked_type=? AND tracked_instance=?"
        return self.sql_db.execute_query(sql, (elem_type, instance))[0]

    def _init_db(self):
        self.sql_db.executescript(
            """
            CREATE TABLE IF NOT EXISTS current_uptime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracked_instance TEXT,
                tracked_type TEXT,
                start_time INTEGER,
                stop_time INTEGER,
                uptime_secs INTEGER,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS total_uptime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracked_instance TEXT,
                tracked_type TEXT,
                start_time INTEGER,
                stop_time INTEGER,
                uptime_secs INTEGER,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS tui_log_line (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracked_instance TEXT,
                tracked_type TEXT,
                status TEXT,
                operation TEXT,
                message TEXT,
                details TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );
            """
        )
