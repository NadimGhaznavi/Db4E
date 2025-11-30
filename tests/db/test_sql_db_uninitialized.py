# db4e/tests/db/test_sql_db_uninitialized.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


def test_sql_db_uninitialized(uninitialized_sql_db):
    assert uninitialized_sql_db.is_initialized() is False
