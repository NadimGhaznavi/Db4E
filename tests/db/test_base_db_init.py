# db4e/tests/db/test_db_init.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import pytest

from db4e.db.BaseDb import BaseDb


class FakeSQLDb:
    def __init__(self, initialized):
        self._initialized = initialized
        self.check_initialized_called = False

    def check_initialized(self):
        self.check_initialized_called = True

    def is_initialized(self):
        return self._initialized


class FakeBaseDb(BaseDb):
    def __init__(self, sql_db):
        super().__init__(sql_db)
        self.init_db_called = False

    def _init_db(self):
        self.init_db_called = True


def test_check_initialized_calls_sql_check_and_init():
    sql = FakeSQLDb(initialized=True)
    base = FakeBaseDb(sql)

    assert base.is_initialized() is False or base.is_initialized() is None

    # Call method under test
    base.check_initialized()

    assert sql.check_initialized_called is True
    assert base.init_db_called is True
    assert base.is_initialized() is True


def test_check_initialized_does_not_init_if_sql_not_ready():
    sql = FakeSQLDb(initialized=False)
    base = FakeBaseDb(sql)

    base.check_initialized()

    assert sql.check_initialized_called is True
    assert base.init_db_called is False
    assert base.is_initialized() is False or base.is_initialized() is None
