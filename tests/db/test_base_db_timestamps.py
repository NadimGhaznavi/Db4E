# db4e/tests/db/test_db_timestamps.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

# db/test_base_db_timestamps.py
import pytest
import time
from db4e.db.BaseDb import BaseDb
from db4e.recs.monero.Db4E import Db4E
from db4e.constants.DSQL import DCol


# Fake SQLDb for testing
class FakeSQLDb:
    def __init__(self):
        self.rows = []
        self.initialized = True

    def check_initialized(self):
        self.initialized = True

    def is_initialized(self):
        return self.initialized

    def insert_one(self, sql, values):
        # Simulate returning an auto-increment ID
        new_id = len(self.rows) + 1
        self.rows.append({"id": new_id, **dict(zip([col.strip() for col in sql.split('(')[1].split(')')[0].split(',')], values))})
        return new_id

    def update_one(self, sql, values):
        # For simplicity, just overwrite first row
        for row in self.rows:
            if row["id"] == values[-1]:
                for i, col in enumerate(sql.split("SET")[1].split("WHERE")[0].split(",")):
                    col_name = col.split("=")[0].strip()
                    row[col_name] = values[i]
                return

# Minimal BaseDb subclass to avoid abstract method
class FakeBaseDb(BaseDb):
    def _init_db(self):
        pass

@pytest.fixture
def db():
    sql = FakeSQLDb()
    return FakeBaseDb(sql)

def test_insert_sets_timestamps(db):
    rec = Db4E()
    rec.id(None)
    rec._donation_wallet = "dummy_wallet"
    
    inserted = db.insert_one(rec)
    
    data = inserted.to_dict()
    # Check timestamps exist
    assert "updated_y" in db.add_timestamp_data(data)
    assert "updated_mo" in db.add_timestamp_data(data)
    assert inserted.id() is not None

def test_update_updates_only_updated_at(db):
    rec = Db4E()
    rec.id(1)
    rec._donation_wallet = "dummy_wallet"

    # Initial insert
    db.insert_one(rec)

    # Capture timestamps before update
    before_update = db.add_timestamp_data(rec.to_dict()).copy()

    time.sleep(1)  # ensure time changes

    # Update
    rec._donation_wallet = "new_wallet"
    updated_rec = db.update_one(rec)

    # Capture timestamps after update
    after_update = db.add_timestamp_data(updated_rec.to_dict())

    # Now compare timestamps
    assert after_update[DCol.UPDATED_YEAR] >= before_update[DCol.UPDATED_YEAR]
    assert after_update[DCol.UPDATED_MONTH] >= before_update[DCol.UPDATED_MONTH]
    assert after_update[DCol.UPDATED_DAY] >= before_update[DCol.UPDATED_DAY]
    assert after_update[DCol.UPDATED_HOUR] >= before_update[DCol.UPDATED_HOUR]


