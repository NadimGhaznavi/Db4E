# db4e/tests/conftest.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

# tests/conftest.py
import pytest
from db4e.db.SQLDb import SQLDb
from db4e.mgr.BootstrapMgr import BootstrapMgr
from db4e.constants.DField import DField
from db4e.constants.DDir import DDir


class FakeBootstrapMgr(BootstrapMgr):
    def __init__(self, base_dir):
        # Do NOT call real super().__init__()
        self._base_dir = base_dir
        self._initialized = True

    def is_initialized(self):
        return True

    def get_dir(self, aDir):
        if aDir == DDir.DB:
            return self._base_dir
        raise KeyError(f"Unknown dir request: {aDir}")


class FakeUnitializedBootstrapMgr(BootstrapMgr):
    def __init__(self):
        # Do NOT call real super().__init__()
        self._initialized = False

    def is_initialized(self):
        return False


@pytest.fixture
def uninitialized_bootstrap_mgr():
    return FakeUnitializedBootstrapMgr()


@pytest.fixture
def initialized_sql_db(tmp_path):
    """
    Uses tmp_path, a built-in pytest fixture.
    """
    fake_bs = FakeBootstrapMgr(base_dir=str(tmp_path))
    db = SQLDb(db_type=DField.SERVER, bs_mgr=fake_bs)
    return db


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path
