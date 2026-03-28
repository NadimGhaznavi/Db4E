# db4e/tests/db/test_ops_db.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import time

from db4e.constants.DSQL import OPS_TABLE_LIST
from db4e.db.OpsDb import OpsDb
from db4e.recs.monero.Db4E import Db4E
from db4e.constants.DElem import DElem


def create_ops_tables(sql_db, ops_db):
    sql_db.executescript(
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
        ops_db.add_updated_ts_column(table)


def get_tui_log_line_data():
    test_instance = {
        "tracked_instance": "test_instance",
        "tracked_type": "test_type",
        "status": "test_status",
        "operation": "test_operation",
        "message": "test_message",
        "details": "test_details",
    }
    test_data = []
    for i in range(10):
        test_data.append(test_instance)
    return test_data


def test_initialized_init(initialized_sql_db):
    ops_db = OpsDb(sql_db=initialized_sql_db)
    assert ops_db._initialized is True


def test_uninitialized_init(uninitialized_sql_db):
    ops_db = OpsDb(sql_db=uninitialized_sql_db)
    assert ops_db._initialized is False


def test_add_start_event(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)

    ops_db.add_start_event(DElem.DB4E, DElem.DB4E)

    now = time.time()
    year = int(time.strftime("%Y", time.localtime(now)))
    month = int(time.strftime("%m", time.localtime(now)))
    day = int(time.strftime("%d", time.localtime(now)))
    hour = int(time.strftime("%H", time.localtime(now)))
    minute = int(time.strftime("%M", time.localtime(now)))
    second = int(time.strftime("%S", time.localtime(now)))

    rows = sql_db.execute_query("SELECT * from current_uptime")
    assert len(rows) == 1
    assert rows[0]["tracked_instance"] == DElem.DB4E  # tracked_instance
    assert rows[0]["tracked_type"] == DElem.DB4E  # tracked_type
    assert rows[0]["start_time"] <= int(round(now))  # start_time
    # next column is cur_time
    assert rows[0]["stop_time"] is None  # stop_time
    assert rows[0]["updated_y"] <= year  # updated_y
    assert rows[0]["updated_mo"] <= month  # updated_mo
    assert rows[0]["updated_d"] <= day  # updated_d
    assert rows[0]["updated_h"] <= hour  # updated_h
    assert rows[0]["updated_mi"] <= minute  # updated_mi
    assert rows[0]["updated_s"] <= second  # updated_s


def test_add_stop_event(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)

    ops_db.add_start_event(DElem.DB4E, DElem.DB4E)
    time.sleep(2)
    ops_db.add_stop_event(DElem.DB4E, DElem.DB4E)

    rows = sql_db.execute_query("SELECT * from current_uptime")
    assert len(rows) == 1
    assert rows[0]["tracked_instance"] == DElem.DB4E
    assert rows[0]["tracked_type"] == DElem.DB4E
    assert rows[0]["start_time"] <= int(round(time.time()))
    assert rows[0]["stop_time"] <= int(round(time.time()))
    assert rows[0]["uptime_secs"] >= 2

    rows = sql_db.execute_query("SELECT * from total_uptime")
    assert len(rows) == 1
    assert rows[0]["tracked_instance"] == DElem.DB4E
    assert rows[0]["tracked_type"] == DElem.DB4E
    assert rows[0]["uptime_secs"] >= 2

    ops_db.add_start_event(DElem.DB4E, DElem.DB4E)
    time.sleep(2)
    ops_db.add_stop_event(DElem.DB4E, DElem.DB4E)

    rows = sql_db.execute_query("SELECT * from total_uptime")
    assert len(rows) == 1
    assert rows[0]["uptime_secs"] >= 4


def test_add_tui_log_line(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)
    test_data = get_tui_log_line_data()[0]
    ops_db.add_tui_log_line(
        tracked_instance=test_data["tracked_instance"],
        tracked_type=test_data["tracked_type"],
        status=test_data["status"],
        operation=test_data["operation"],
        message=test_data["message"],
    )
    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 1
    assert rows[0]["tracked_instance"] == test_data["tracked_instance"]
    assert rows[0]["tracked_type"] == test_data["tracked_type"]
    assert rows[0]["status"] == test_data["status"]
    assert rows[0]["operation"] == test_data["operation"]
    assert rows[0]["message"] == test_data["message"]
    assert rows[0]["details"] is None


def test_add_tui_log_line_data(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)
    test_data = get_tui_log_line_data()
    ops_db.add_tui_log_line_data(test_data)
    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 10
    for row in rows:
        assert row["tracked_instance"] == test_data[0]["tracked_instance"]
        assert row["tracked_type"] == test_data[0]["tracked_type"]
        assert row["status"] == test_data[0]["status"]
        assert row["operation"] == test_data[0]["operation"]
        assert row["message"] == test_data[0]["message"]
        assert row["details"] == test_data[0]["details"]


def test_current_recs(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)
    ops_db.add_start_event(DElem.DB4E, DElem.DB4E)
    # Simulate an unexpected restart where the stop_time wasn't set.
    ops_db = OpsDb(sql_db=sql_db)
    ops_db.check_current_recs()
    rows = sql_db.execute_query("SELECT * from current_uptime")
    assert len(rows) == 1
    assert rows[0]["stop_time"] is not None


def test_clear_tui_log(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)

    test_data = get_tui_log_line_data()
    for row in test_data:
        ops_db.add_tui_log_line(
            tracked_instance=row["tracked_instance"],
            tracked_type=row["tracked_type"],
            status=row["status"],
            operation=row["operation"],
            message=row["message"],
        )

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 10

    ops_db.clear_tui_log()
    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 0


def test_get_open_cur_uptime_rec(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)
    ops_db.add_start_event(DElem.DB4E, DElem.DB4E)
    ops_db.add_start_event(DElem.MONEROD, "foo")
    ops_db.add_start_event(DElem.P2POOL, "bar")

    rows = sql_db.execute_query("SELECT * from current_uptime")
    assert len(rows) == 3
    for row in rows:
        assert row["stop_time"] is None

    rec = ops_db.get_open_cur_uptime_rec(DElem.DB4E, DElem.DB4E)
    assert rec["tracked_instance"] == DElem.DB4E
    assert rec["tracked_type"] == DElem.DB4E
    assert rec["stop_time"] is None

    rec = ops_db.get_open_cur_uptime_rec(DElem.MONEROD, "foo")
    assert rec["tracked_instance"] == "foo"
    assert rec["tracked_type"] == DElem.MONEROD
    assert rec["stop_time"] is None

    rec = ops_db.get_open_cur_uptime_rec(DElem.P2POOL, "bar")
    assert rec["tracked_instance"] == "bar"
    assert rec["tracked_type"] == DElem.P2POOL
    assert rec["stop_time"] is None


def test_get_total_uptime_rec(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)
    ops_db.add_start_event(DElem.DB4E, DElem.DB4E)
    ops_db.add_start_event(DElem.MONEROD, "foo")
    ops_db.add_start_event(DElem.P2POOL, "bar")
    time.sleep(1)
    ops_db.add_stop_event(DElem.DB4E, DElem.DB4E)
    ops_db.add_stop_event(DElem.MONEROD, "foo")
    ops_db.add_stop_event(DElem.P2POOL, "bar")

    rec = ops_db.get_total_uptime_rec(DElem.DB4E, DElem.DB4E)
    assert rec
    rec = ops_db.get_total_uptime_rec(DElem.MONEROD, "foo")
    assert rec
    rec = ops_db.get_total_uptime_rec(DElem.P2POOL, "bar")
    assert rec


def test_get_tui_log(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)
    test_data = get_tui_log_line_data()
    for row in test_data:
        ops_db.add_tui_log_line(
            tracked_instance=row["tracked_instance"],
            tracked_type=row["tracked_type"],
            status=row["status"],
            operation=row["operation"],
            message=row["message"],
        )

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 10
    log_lines = ops_db.get_tui_log()
    assert len(log_lines) == 10


def test_get_tui_log_lines_since(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)

    for i in range(10):
        sql_db.execute_query(
            "INSERT INTO tui_log_line (tracked_instance, tracked_type, status, operation, message, details, updated_y, updated_mo, updated_d, updated_h, updated_mi, updated_s) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "test_instance",
                "test_type",
                "test_status",
                "test_operation",
                "test_message",
                "test_details",
                2025,
                12,
                4,
                15,
                1,
                i,
            ),
        )

    rows = ops_db.get_tui_log_lines_since(1764860465)
    assert len(rows) == 4


def test_update_current(initialized_sql_db):
    sql_db = initialized_sql_db
    ops_db = OpsDb(sql_db=sql_db)
    create_ops_tables(sql_db=sql_db, ops_db=ops_db)
    ops_db.add_start_event(DElem.DB4E, DElem.DB4E)
    ops_db.add_stop_event(DElem.DB4E, DElem.DB4E)
    ops_db.add_start_event(DElem.MONEROD, "foo")
    ops_db.add_start_event(DElem.P2POOL, "bar")

    rows = sql_db.execute_query("SELECT * from current_uptime")
    assert len(rows) == 3
    for row in rows:
        if row["tracked_instance"] == DElem.DB4E:
            assert row["stop_time"] is not None
        else:
            assert row["stop_time"] is None

    ops_db.update_current()

    rows = sql_db.execute_query("SELECT * from current_uptime")
    for row in rows:
        assert row["cur_time"] is not None
