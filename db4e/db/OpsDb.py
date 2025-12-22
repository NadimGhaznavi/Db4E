# db4e/db/OpsDb.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

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
from db4e.constants.DSQL import DCol, OPS_TABLE_LIST


class OpsDb(BaseDb):
    """
    Operations database access layer.

    Manages uptime tracking and TUI log line records.
    """

    def __init__(self, sql_db: SQLDb, log_file=None):
        """
        Initialize the operations database manager.

        :param sql_db: Initialized SQL database wrapper.
        :type sql_db: SQLDb
        :param log_file: Optional log file path.
        :type log_file: str or None
        """
        super().__init__(sql_db=sql_db, log_file=log_file)

    def get_ops_events(self):
        """
        Placeholder for ops event retrieval.
        """
        pass

    def add_start_event(self, elem_type, instance_name):
        """
        Record a start event for an element instance.

        :param elem_type: Element type identifier.
        :type elem_type: str
        :param instance_name: Instance name.
        :type instance_name: str
        """
        self.check_initialized()
        # Create a new current_uptime record
        cur_uptime = CurrentUptime(
            tracked_type=elem_type, tracked_instance=instance_name
        )
        cur_uptime.start_time(int(round(time.time())))
        cur_uptime.cur_time(int(round(time.time())))
        self.insert_one(cur_uptime)

    def add_stop_event(self, elem_type, instance_name):
        """
        Record a stop event for an element instance and update uptime totals.

        :param elem_type: Element type identifier.
        :type elem_type: str
        :param instance_name: Instance name.
        :type instance_name: str
        """
        self.check_initialized()
        # Get the current uptime record where the stop event is not set
        rec = self.get_open_cur_uptime_rec(elem_type, instance_name)
        current_uptime = CurrentUptime(
            tracked_type=elem_type, tracked_instance=instance_name, rec=rec
        )

        if not current_uptime:
            self.log.error(
                f"No current uptime record found for {elem_type}/{instance_name}"
            )
            return

        current_uptime.stop_time(int(round(time.time())))
        current_uptime.uptime_secs(
            current_uptime.stop_time() - current_uptime.start_time()
        )
        self.update_one(current_uptime)

        # Update existing or create new total uptime record
        total_uptime_rec = self.get_total_uptime_rec(elem_type, instance_name)
        update = True
        if not total_uptime_rec:
            update = False
            total_uptime = TotalUptime(
                tracked_type=elem_type, tracked_instance=instance_name
            )
        else:
            total_uptime = TotalUptime(rec=total_uptime_rec)

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
        """
        Add a single TUI log line entry.

        :param tracked_instance: Tracked instance name.
        :type tracked_instance: str
        :param tracked_type: Tracked element type.
        :type tracked_type: str
        :param status: Status string.
        :type status: str
        :param operation: Operation string.
        :type operation: str
        :param message: Message label or text.
        :type message: str
        :param details: Optional details text.
        :type details: str or None
        :param updated_y: Optional year override.
        :type updated_y: int or None
        :param updated_mo: Optional month override.
        :type updated_mo: int or None
        :param updated_d: Optional day override.
        :type updated_d: int or None
        :param updated_h: Optional hour override.
        :type updated_h: int or None
        :param updated_mi: Optional minute override.
        :type updated_mi: int or None
        :param updated_s: Optional second override.
        :type updated_s: int or None
        """
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
        """
        Add multiple TUI log line entries from a list of dicts.

        :param log_line_data: Iterable of log line dictionaries.
        :type log_line_data: list[dict]
        """
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

    def check_current_recs(self):
        """
        Close any open current uptime records and roll into total uptime.
        """
        self.check_initialized()
        sql = f"SELECT * FROM current_uptime WHERE stop_time IS NULL"
        recs = self.sql_db.execute_query(sql)
        for rec in recs:
            # Close off any still open current_uptime records (shutdown wasn't clean)
            cur_uptime = CurrentUptime(rec=rec)
            if not cur_uptime.stop_time():
                cur_uptime.stop_time(cur_uptime.cur_time())
            cur_uptime.uptime_secs(cur_uptime.stop_time() - cur_uptime.start_time())
            self.update_one(cur_uptime)

            # Update corresponding total_uptime record if it exists, or create a new
            # one if it doesn't.
            sql = f"SELECT * FROM total_uptime WHERE tracked_type=? AND tracked_instance=?"
            values = (cur_uptime.tracked_type(), cur_uptime.tracked_instance())
            total_uptime_recs = self.sql_db.execute_query(sql, values)
            if total_uptime_recs:
                total_uptime = TotalUptime(rec=total_uptime_recs[0])
                total_uptime.uptime_secs(
                    total_uptime.uptime_secs() + cur_uptime.uptime_secs()
                )
                self.update_one(total_uptime)
            else:
                total_uptime = TotalUptime(
                    tracked_type=cur_uptime.tracked_type(),
                    tracked_instance=cur_uptime.tracked_instance(),
                )
                total_uptime.uptime_secs(cur_uptime.uptime_secs())
                self.insert_one(total_uptime)

    def clear_tui_log(self):
        """
        Remove all TUI log line records.
        """
        self.check_initialized()
        self.sql_db.execute_query(f"DELETE FROM {DTable.TUI_LOG_LINE}")

    def get_open_cur_uptime_rec(self, elem_type, instance) -> CurrentUptime:
        """
        Fetch the open current uptime record for a specific instance.

        :param elem_type: Element type identifier.
        :type elem_type: str
        :param instance: Instance name.
        :type instance: str
        :return: Current uptime record or None.
        :rtype: sqlite3.Row or None
        """
        self.check_initialized()
        sql = f"SELECT * FROM current_uptime WHERE tracked_type=? AND tracked_instance=? AND stop_time IS NULL"
        return self.sql_db.find_one(sql, (elem_type, instance))

    def get_total_uptime_rec(self, elem_type, instance) -> TotalUptime:
        """
        Fetch the total uptime record for a specific instance.

        :param elem_type: Element type identifier.
        :type elem_type: str
        :param instance: Instance name.
        :type instance: str
        :return: Total uptime record or None.
        :rtype: sqlite3.Row or None
        """
        self.check_initialized()
        sql = f"SELECT * FROM total_uptime WHERE tracked_type=? AND tracked_instance=?"
        return self.sql_db.find_one(sql, (elem_type, instance))

    def get_tui_log(self, elem_type=None):
        """
        Fetch TUI log lines ordered by newest first.

        :param elem_type: Optional element type filter (unused).
        :type elem_type: str or None
        :return: List of TUILogLine objects.
        :rtype: list[TUILogLine]
        """
        self.check_initialized()
        recs = self.sql_db.execute_query(
            f"SELECT * FROM {DTable.TUI_LOG_LINE} ORDER BY id DESC"
        )
        log_lines = []
        for rec in recs:
            log_lines.append(TUILogLine(rec=rec))
        return log_lines

    def get_tui_log_lines_since(self, since_ts: int) -> list[dict]:
        """
        Fetch TUI log lines updated after a given timestamp.

        :param since_ts: Unix timestamp to filter by.
        :type since_ts: int
        :return: List of log line dictionaries.
        :rtype: list[dict]
        """
        sql = """
            SELECT *,
                strftime('%s',
                    printf('%04d-%02d-%02d %02d:%02d:%02d',
                        updated_y, updated_mo, updated_d, updated_h, updated_mi, updated_s
                    )
                ) AS updated_ts
            FROM tui_log_line
            WHERE updated_ts > ?
            ORDER BY updated_ts ASC
        """
        results = self.sql_db.execute_query(sql, (since_ts,))
        return [dict(row) for row in results]

    def update_current(self):
        """
        Update the current time for all open uptime records.
        """
        time.time()
        self.check_initialized()
        sql = """UPDATE current_uptime
            SET cur_time = ?
            WHERE stop_time IS NULL
            """
        values = (int(round(time.time())),)
        self.sql_db.execute_query(sql, values)

    def _init_db(self):
        """
        Initialize ops tables in the SQLite database.
        """
        self.sql_db.executescript(
            """
            CREATE TABLE IF NOT EXISTS current_uptime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracked_instance TEXT,
                tracked_type TEXT,
                start_time INTEGER,
                cur_time INTEGER,
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

        # Add "updated_ts" column to the Ops tables.
        for table in OPS_TABLE_LIST:
            self.add_updated_ts_column(table)
