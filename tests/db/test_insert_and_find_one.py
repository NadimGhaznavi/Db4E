# db4e/tests/db/test_insert_and_find_one.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


def test_insert_and_find_one(initialized_sql_db):
    # Create a test table
    initialized_sql_db.executescript(
        """
    CREATE TABLE test_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        updated_ts INTEGER
    );
    """
    )

    # Insert
    row_id = initialized_sql_db.insert_one(
        "INSERT INTO test_table (name, updated_ts) VALUES (?, ?)", ("alpha", 123)
    )

    # Verify
    row = initialized_sql_db.find_one(
        "SELECT id, name, updated_ts FROM test_table WHERE id = ?", (row_id,)
    )
    assert row["name"] == "alpha"
    assert row["updated_ts"] == 123
