"""
db4e/db/BaseDb.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

# Supporting modules
from datetime import datetime

# Column definitions
from db4e.constants.DSQL import DCol, TYPE_TO_TABLE_MAP


class BaseDb:

    def add_timestamp_data(self, data):
        """Add timestamp data to a record"""
        now = datetime.now()
        data.update(
            {
                DCol.UPDATED_YEAR: now.year,
                DCol.UPDATED_MONTH: now.month,
                DCol.UPDATED_DAY: now.day,
                DCol.UPDATED_HOUR: now.hour,
                DCol.UPDATED_MINUTE: now.minute,
                DCol.UPDATED_SECOND: now.second,
            }
        )
        return data

    def insert_one(self, elem):
        data = elem.to_dict()
        data = self.add_timestamp_data(data)
        # Stable key order (deterministic SQL generation)
        table_name = TYPE_TO_TABLE_MAP[type(elem)]
        columns = sorted(data.keys())
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        values = tuple(data[col] for col in columns)
        object_id = self.sql_db.execute_insert_one(sql=sql, values=values)
        elem.id(object_id)
        return elem

    def update_one(self, ops_object):
        data = ops_object.to_dict()
        data = self.add_timestamp_data(data)
        table_name = TYPE_TO_TABLE_MAP[type(ops_object)]
        columns = sorted(data.keys())
        set_clause = ", ".join([f"{col}=?" for col in columns if col != DCol.ID])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE id=?"
        values = tuple(data[col] for col in columns if col != DCol.ID) + (
            ops_object.id(),
        )
        self.sql_db.execute_update_one(sql=sql, values=values)
        return ops_object
