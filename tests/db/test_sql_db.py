# db4e/tests/db/test_sql_db.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from db4e.db.SQLDb import SQLDb
from db4e.mgr.BootstrapMgr import BootstrapMgr
from db4e.constants.DField import DField
from db4e.constants.DDir import DDir
from db4e.constants.DSQL import (
    ELEM_TABLE_LIST,
    MINING_TABLE_LIST,
    HOURLY_MINING_TABLE_LIST,
    OPS_TABLE_LIST,
)


class FakeUnitializedBootstrapMgr(BootstrapMgr):
    def __init__(self):
        # Do NOT call real super().__init__()
        self._initialized = False

    def is_initialized(self):
        return False

    def get_dir(self, aDir):
        if aDir == DDir.DB:
            return self._base_dir
        raise KeyError(f"Unknown dir request: {aDir}")


class FakeInitializedBootstrapMgr(BootstrapMgr):
    def __init__(self, base_dir):
        # Do NOT call real super().__init__()
        self._initialized = True
        self._base_dir = base_dir

    def get_dir(self, aDir):
        if aDir == DDir.DB:
            return self._base_dir

    def is_initialized(self):
        return True


def test_uninitialized_sql_db_is_uninitialized():
    sql_db = SQLDb(db_type=DField.SERVER, bs_mgr=FakeUnitializedBootstrapMgr())
    assert sql_db.is_initialized() is False


def test_initialized_sql_db_is_initialized(tmp_dir):
    sql_db = SQLDb(db_type=DField.SERVER, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    assert sql_db.is_initialized() is True


def test_sql_db_creates_sync_meta(tmp_dir):
    sql_db = SQLDb(db_type=DField.SERVER, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    rows = sql_db.execute_query("SELECT * FROM sync_meta")
    assert len(rows) > 0
    # Check required columns exist
    first = rows[0]
    assert "table_name" in first.keys()
    assert "last_sync_ts" in first.keys()
    sql_db.close()


def test_unitialized_sql_db_check_initialized():
    sql_db = SQLDb(db_type=DField.SERVER, bs_mgr=FakeUnitializedBootstrapMgr())
    sql_db.check_initialized()
    assert sql_db.is_initialized() is False


def test_initialized_sql_db_check_initialized_server(tmp_dir):
    sql_db = SQLDb(db_type=DField.SERVER, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.check_initialized()
    assert sql_db.is_initialized() is True


def test_initialized_sql_db_check_initialized_client(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.check_initialized()
    assert sql_db.is_initialized() is True


def test_sql_db_close(tmp_dir):
    sql_db = SQLDb(db_type=DField.SERVER, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    assert sql_db._conn is not None
    assert sql_db._cursor is not None
    assert sql_db._cursor is not None
    assert sql_db._initialized is True
    sql_db.close()
    assert sql_db._conn is None
    assert sql_db._cursor is None
    assert sql_db._cursor is None
    assert sql_db._initialized is False


def test_sql_db_execute_query(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.execute_query(
        "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)"
    )
    sql_db.execute_query("INSERT INTO test (name) VALUES (?)", ("Alice",))
    sql_db.execute_query("INSERT INTO test (name) VALUES (?)", ("Bob",))
    rows = sql_db.execute_query("SELECT * FROM test")
    assert len(rows) == 2
    assert rows[0][1] == "Alice"
    assert rows[1][1] == "Bob"
    sql_db.close()


def test_sql_db_executescript(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO test (name) VALUES ('Alice');
        INSERT INTO test (name) VALUES ('Bob');
        """
    )
    rows = sql_db.execute_query("SELECT * FROM test")
    assert len(rows) == 2
    assert rows[0][1] == "Alice"
    assert rows[1][1] == "Bob"
    sql_db.close()


def test_sql_db_execute_merge(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
        INSERT INTO test (name, age) VALUES ('Alice', 10);
        INSERT INTO test (name, age) VALUES ('Bob', 12);
        """
    )
    sql_db.execute_merge(
        "INSERT OR IGNORE INTO test (name, age) VALUES (?, ?)",
        [
            {"name": "Charlie", "age": 14},
            {"name": "David", "age": 16},
        ],
    )
    rows = sql_db.execute_query("SELECT * FROM test")
    assert len(rows) == 4
    assert rows[0][1] == "Alice"
    assert rows[1][1] == "Bob"
    assert rows[2][1] == "Charlie"
    assert rows[3][1] == "David"
    assert rows[0][2] == 10
    assert rows[1][2] == 12
    assert rows[2][2] == 14
    assert rows[3][2] == 16
    sql_db.close()


def test_sql_db_find_one(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
        INSERT INTO test (name, age) VALUES ('Alice', 10);
        INSERT INTO test (name, age) VALUES ('Bob', 12);
        """
    )
    row = sql_db.find_one("SELECT * FROM test WHERE name=?", ("Alice",))
    assert row[1] == "Alice"
    assert row[2] == 10
    row = sql_db.find_one("SELECT * FROM test WHERE name=?", ("Charlie",))
    assert row is None
    sql_db.close()


def test_sql_db_find_many(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
        INSERT INTO test (name, age) VALUES ('Alice', 10);
        INSERT INTO test (name, age) VALUES ('Bob', 12);
        """
    )
    rows = sql_db.find_many("test")
    assert len(rows) == 2
    assert rows[0][1] == "Alice"
    assert rows[1][1] == "Bob"
    sql_db.close()


def test_sql_db_get_last_sync(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.execute_query(
        "UPDATE sync_meta SET last_sync_ts = 99 WHERE table_name = ?",
        ("monerod",),
    )

    assert sql_db.get_last_sync("monerod") == 99
    assert sql_db.get_last_sync("p2pool") == 0

    sql_db.close()


def test_sql_db_get_max_updated_ts(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, updated_ts INTEGER);
        INSERT INTO test (name, age, updated_ts) VALUES ('Alice', 10, 0);
        INSERT INTO test (name, age, updated_ts) VALUES ('Bob', 12, 2);
        INSERT INTO test (name, age, updated_ts) VALUES ('Charlie', 12, 1);
        """
    )
    assert sql_db.get_max_updated_ts("test") == 2
    sql_db.close()


def test_sql_db_init_db(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))

    for elem in (
        ELEM_TABLE_LIST + MINING_TABLE_LIST + HOURLY_MINING_TABLE_LIST + OPS_TABLE_LIST
    ):
        row = sql_db.find_one(f"SELECT * FROM sync_meta WHERE table_name=?", (elem,))
        assert row[1] == 0


def test_sql_db_initialize(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeUnitializedBootstrapMgr())

    assert sql_db.is_initialized() is False
    assert sql_db._conn is None
    assert sql_db._cursor is None
    assert sql_db._initialized is False

    sql_db.initialize(tmp_dir)

    assert sql_db.is_initialized() is True
    assert sql_db._conn is not None
    assert sql_db._cursor is not None
    assert sql_db._initialized is True

    sql_db.close()


def test_sql_db_insert_one(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO test (name) VALUES ('Alice');
        INSERT INTO test (name) VALUES ('Bob');
        """
    )
    id = sql_db.insert_one("INSERT INTO test (name) VALUES (?)", ("Charlie",))
    assert id == 3
    row = sql_db.find_one("SELECT * FROM test WHERE id=?", (id,))
    assert row[1] == "Charlie"
    sql_db.close()


def test_sql_db_update_one(tmp_dir):
    sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=FakeInitializedBootstrapMgr(tmp_dir))
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, updated_ts INTEGER);
        INSERT INTO test (name, age, updated_ts) VALUES ('Alice', 10, 0);
        INSERT INTO test (name, age, updated_ts) VALUES ('Bob', 12, 2);
        INSERT INTO test (name, age, updated_ts) VALUES ('Charlie', 12, 1);
        """
    )
    sql_db.update_one("UPDATE test SET age=? WHERE id=?", (14, 1))
    row = sql_db.find_one("SELECT * FROM test WHERE id=?", (1,))
    assert row[2] == 14
    sql_db.close()
