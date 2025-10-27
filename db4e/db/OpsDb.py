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
from datetime import datetime

# Ops classes
from db4e.recs.ops.CurrentUptime import CurrentUptime
from db4e.recs.ops.TotalUptime import TotalUptime
from db4e.recs.ops.TUILogLine import TUILogLine
from db4e.constants.DSQL import DTable

# The module that interfaces with SQLite3
from db4e.db.SQLDb import SQLDb
from db4e.db.BaseDb import BaseDb

# Db4E logging module
from db4e.util.Db4ELogger import Db4ELogger

# Constants
from db4e.constants.DModule import DModule
from db4e.constants.DSQL import DCol


class OpsDb(BaseDb):

    def __init__(self, sql_db: SQLDb, log_file=None):
        super().__init__(sql_db=sql_db, log_file=log_file)

    def get_ops_events(self):
        pass

    def add_start_event(self, elem_type, instance):
        self.check_initialized()
        # Create a new current_uptime record
        cur_uptime = CurrentUptime(tracked_type=elem_type, tracked_instance=instance)
        cur_uptime.start_time(int(round(time.time())))
        self.insert_one(cur_uptime)

    def add_stop_event(self, elem_type, instance):
        self.check_initialized()
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

    def add_tui_log_line(
        self,
        tracked_instance,
        tracked_type,
        status,
        operation,
        message,
        details=None,
        updated_y=None,
        updated_mo=None,
        updated_d=None,
        updated_h=None,
        updated_mi=None,
        updated_s=None,
    ):
        self.check_initialized()
        log_line = TUILogLine(
            tracked_instance=tracked_instance,
            tracked_type=tracked_type,
            status=status,
            operation=operation,
            message=message,
            details=details,
        )

        # Timestamp data has been provided
        if updated_y:
            log_line.updated_year(updated_y)
            log_line.updated_month(updated_mo)
            log_line.updated_day(updated_d)
            log_line.updated_hour(updated_h)
            log_line.updated_minute(updated_mi)
            log_line.updated_second(updated_s)

        # We need to add timestamp data
        else:
            now = datetime.now()
            log_line.updated_year(now.year)
            log_line.updated_month(now.month)
            log_line.updated_day(now.day)
            log_line.updated_hour(now.hour)
            log_line.updated_minute(now.minute)
            log_line.updated_second(now.second)

        self.insert_one(log_line)

    def add_tui_log_line_data(self, log_line_data):
        self.check_initialized()
        for log_line in log_line_data:
            if DCol.DETAILS in log_line:
                details = log_line["details"]
            else:
                details = None
            self.add_tui_log_line(
                tracked_instance=log_line[DCol.TRACKED_INSTANCE],
                tracked_type=log_line[DCol.TRACKED_TYPE],
                status=log_line[DCol.STATUS],
                operation=log_line[DCol.OPERATION],
                message=log_line[DCol.MESSAGE],
                details=details,
            )

    def clear_tui_log(self):
        self.check_initialized()
        self.sql_db.execute_query(f"DELETE FROM {DTable.TUI_LOG_LINE}")

    def get_open_cur_uptime_rec(self, elem_type, instance) -> CurrentUptime:
        self.check_initialized()
        sql = f"SELECT * FROM current_uptime WHERE tracked_type=? AND tracked_instance=? AND stop_time IS NULL"
        return self.sql_db.execute_query(sql, (elem_type, instance))[0]

    def get_total_uptime_rec(self, elem_type, instance) -> TotalUptime:
        self.check_initialized()
        sql = f"SELECT * FROM total_uptime WHERE tracked_type=? AND tracked_instance=?"
        return self.sql_db.execute_query(sql, (elem_type, instance))[0]

    def get_tui_log(self):
        self.check_initialized()
        recs = self.sql_db.execute_query(f"SELECT * FROM {DTable.TUI_LOG_LINE}")
        log_lines = []
        for rec in recs:
            log_lines.append(TUILogLine(rec=rec))
        return log_lines

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
