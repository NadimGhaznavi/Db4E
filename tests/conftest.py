# db4e/tests/conftest.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

# tests/conftest.py
import pytest
import os
import shutil
from db4e.db.SQLDb import SQLDb
from db4e.db.DeplDb import DeplDb
from db4e.db.OpsDb import OpsDb
from db4e.mgr.BootstrapMgr import BootstrapMgr
from db4e.constants.DField import DField
from db4e.constants.DDir import DDir
from db4e.constants.DElem import DElem
from db4e.constants.DDef import DDef

TEMPLATES_DIR = "templates"
VENDOR_DIR = "vendor"


class FakeInitializedBootstrapMgr(BootstrapMgr):
    def __init__(self, base_dir):
        # Do NOT call real super().__init__()
        self._initialized = True
        self._base_dir = base_dir
        tests_dir = os.path.dirname(__file__)
        # Copy in dummy templates directory and it's contents
        templates_dir_src = os.path.join(tests_dir, TEMPLATES_DIR)
        shutil.copytree(
            templates_dir_src, self._base_dir + "/" + TEMPLATES_DIR, dirs_exist_ok=True
        )
        # Copy in dummy vendor directory an it's contents
        vendor_dir_src = os.path.join(tests_dir, VENDOR_DIR)
        shutil.copytree(
            vendor_dir_src, self._base_dir + "/" + VENDOR_DIR, dirs_exist_ok=True
        )

    def get_dir(self, aDir):
        if aDir == DDir.DB:
            return self._base_dir
        elif aDir == DDir.VENDOR:
            return self._base_dir + "/" + VENDOR_DIR
        elif aDir == DDir.TEMPLATE:
            return self._base_dir + "/" + TEMPLATES_DIR
        elif aDir == DElem.MONEROD:
            return DElem.MONEROD
        elif aDir == DElem.P2POOL:
            return DElem.P2POOL
        elif aDir == DElem.XMRIG:
            return DElem.XMRIG

        raise KeyError(f"Unknown dir request: {aDir}")

    def is_initialized(self):
        return True


class FakeUnitializedBootstrapMgr(BootstrapMgr):
    def __init__(self):
        # Do NOT call real super().__init__()
        self._initialized = False
        self._base_dir = "/not/implemented"

    def is_initialized(self):
        return False

    def get_dir(self, aDir):
        if aDir == DDir.DB:
            return self._base_dir
        raise KeyError(f"Unknown dir request: {aDir}")


@pytest.fixture
def uninitialized_bootstrap_mgr():
    return FakeUnitializedBootstrapMgr()


@pytest.fixture
def initialized_bootstrap_mgr(tmp_path):
    """
    Uses tmp_path, a built-in pytest fixture.
    """
    return FakeInitializedBootstrapMgr(base_dir=str(tmp_path))


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def uninitialized_sql_db():
    fake_bs = FakeUnitializedBootstrapMgr()
    db = SQLDb(db_type=DField.SERVER, bs_mgr=fake_bs)
    return db


@pytest.fixture
def initialized_sql_db(tmp_path):
    fake_bs = FakeInitializedBootstrapMgr(base_dir=str(tmp_path))
    db = SQLDb(db_type=DField.SERVER, bs_mgr=fake_bs)
    return db


@pytest.fixture
def initialized_depl_db(initialized_sql_db):
    sql_db = initialized_sql_db
    return DeplDb(sql_db=sql_db)


@pytest.fixture
def initialized_ops_db(initialized_sql_db):
    sql_db = initialized_sql_db
    return OpsDb(sql_db=sql_db)
