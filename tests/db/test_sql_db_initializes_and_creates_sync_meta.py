# db4e/tests/db/test_sql_db_initializes_and_creates_sync_meta.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

def test_sql_db_initializes_and_creates_sync_meta(initialized_sql_db):
    # Should be initialized
    assert initialized_sql_db.is_initialized()

    # sync_meta should exist and contain rows
    rows = initialized_sql_db.execute_query("SELECT * FROM sync_meta")
    assert len(rows) > 0

    # Check required columns exist
    first = rows[0]
    assert "table_name" in first.keys()
    assert "last_sync_ts" in first.keys()
