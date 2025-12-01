# db4e/tests/db/test_db.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import pytest
from unittest.mock import patch
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.db.BaseDb import BaseDb
from db4e.constants.DSQL import DCol


def test_init(initialized_sql_db):
    with patch.object(BaseDb, "_init_db", return_value=True):
        base_db = BaseDb(sql_db=initialized_sql_db)
    assert base_db._initialized is True


def test_add_timestamp_data(initialized_sql_db):
    with patch.object(BaseDb, "_init_db", return_value=True):
        base_db = BaseDb(sql_db=initialized_sql_db)
    data = {"id": 1}
    result = base_db.add_timestamp_data(data)
    assert DCol.UPDATED_YEAR in result
    assert DCol.UPDATED_MONTH in result
    assert DCol.UPDATED_DAY in result
    assert DCol.UPDATED_HOUR in result
    assert DCol.UPDATED_MINUTE in result
    assert DCol.UPDATED_SECOND in result


def test_updated_ts_column(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, updated_y INTEGER, updated_mo INTEGER, updated_d INTEGER, updated_h INTEGER, updated_mi INTEGER, updated_s INTEGER);
        INSERT INTO test (name, updated_y, updated_mo, updated_d, updated_h, updated_mi, updated_s) VALUES ('Alice', 1970, 1, 29, 11, 59, 49);
        """
    )
    with patch.object(BaseDb, "_init_db", return_value=True):
        base_db = BaseDb(sql_db=sql_db)
    base_db.add_updated_ts_column("test")
    rows = sql_db.execute_query("SELECT updated_ts FROM test")
    assert len(rows) == 1
    

def test_unitialized_check_initialized(uninitialized_sql_db):
    base_db = BaseDb(sql_db=uninitialized_sql_db)
    assert base_db._initialized is False
    base_db.check_initialized()
    assert base_db._initialized is False


def test_initialized_check_initialized(initialized_sql_db):
    with patch.object(BaseDb, "_init_db", return_value=True):
        base_db = BaseDb(sql_db=initialized_sql_db)
        base_db.check_initialized()
    assert base_db._initialized is True


def test_init_db(initialized_sql_db):
    with patch.object(BaseDb, "_init_db", return_value=True):
        base_db = BaseDb(sql_db=initialized_sql_db)
    assert base_db._initialized is True
    with pytest.raises(NotImplementedError):
        base_db.check_initialized()


def test_get_records_since(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, updated_ts INTEGER);
        INSERT INTO test (name, age, updated_ts) VALUES ('Alice', 10, 0);
        INSERT INTO test (name, age, updated_ts) VALUES ('Bob', 12, 2);
        INSERT INTO test (name, age, updated_ts) VALUES ('Charlie', 12, 1);
        """
    )
    with patch.object(BaseDb, "_init_db", return_value=True):
        base_db = BaseDb(sql_db=initialized_sql_db)
        rows = base_db.get_records_since("test", 1)
    assert len(rows) == 1
    assert rows[0][1] == "Bob"
    assert rows[0][2] == 12
    assert rows[0][3] == 2
    

def test_insert_one(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS p2pool_remote (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instance TEXT,
            ip_addr TEXT,
            stratum_port INTEGER,
            updated_y INTEGER,
            updated_mo INTEGER,
            updated_d INTEGER,
            updated_h INTEGER,
            updated_mi INTEGER,
            updated_s INTEGER
        );
        """
    )
    some_pool = P2PoolRemote()
    some_pool.instance('TestPool')
    with patch.object(BaseDb, "_init_db", return_value=True):
        base_db = BaseDb(sql_db=initialized_sql_db)
        base_db.add_updated_ts_column("p2pool_remote")
        base_db.insert_one(some_pool)
    rows = sql_db.execute_query("SELECT * FROM p2pool_remote")
    assert len(rows) == 1
    assert rows[0][1] == 'TestPool'
    

def test_initialized_sql_db_is_initialized(initialized_sql_db):
    with patch.object(BaseDb, "_init_db", return_value=True):
        base_db = BaseDb(sql_db=initialized_sql_db)
    assert base_db.is_initialized()


def test_uninitialized_sql_db_is_initialized(uninitialized_sql_db):
    base_db = BaseDb(sql_db=uninitialized_sql_db)
    assert base_db.is_initialized() is False


def test_update_one(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS p2pool_remote (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instance TEXT,
            ip_addr TEXT,
            stratum_port INTEGER,
            updated_y INTEGER,
            updated_mo INTEGER,
            updated_d INTEGER,
            updated_h INTEGER,
            updated_mi INTEGER,
            updated_s INTEGER
        );
        """
    )
    some_pool = P2PoolRemote()
    some_pool.instance('TestPool')
    with patch.object(BaseDb, "_init_db", return_value=True):
        base_db = BaseDb(sql_db=initialized_sql_db)
        base_db.add_updated_ts_column("p2pool_remote")
        some_pool = base_db.insert_one(some_pool)
        some_pool.ip_addr('10.10.10.10')
        base_db.update_one(some_pool)
        row = sql_db.find_one("SELECT * FROM p2pool_remote WHERE id=?", (some_pool.id(),))
        assert row[2] == '10.10.10.10'


def test_upsert_records(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
        CREATE TABLE IF NOT EXISTS p2pool_remote (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instance TEXT,
            ip_addr TEXT,
            stratum_port INTEGER,
            updated_y INTEGER,
            updated_mo INTEGER,
            updated_d INTEGER,
            updated_h INTEGER,
            updated_mi INTEGER,
            updated_s INTEGER
        );
        """
    )
    pool_a = P2PoolRemote()
    pool_a.instance('TestPoolA')
    pool_b = P2PoolRemote()
    pool_b.instance('TestPoolB')
    pool_b.ip_addr('10.10.10.10')
    with patch.object(BaseDb, "_init_db", return_value=True):
        base_db = BaseDb(sql_db=initialized_sql_db)
        base_db.add_updated_ts_column("p2pool_remote")
        base_db.insert_one(pool_a)
        base_db.insert_one(pool_b)
        pool_b.ip_addr('10.10.10.11')
        pool_c = P2PoolRemote()
        pool_c.instance('TestPoolC')
        rows = [pool_a.to_dict(), pool_b.to_dict(), pool_c.to_dict()]
        base_db.upsert_records("p2pool_remote", rows)
        rows = sql_db.find_many("p2pool_remote")
        assert len(rows) == 3
        assert rows[0][1] == 'TestPoolA'
        assert rows[1][1] == 'TestPoolB'
        assert rows[2][1] == 'TestPoolC'
        assert rows[1][2] == '10.10.10.11'

     