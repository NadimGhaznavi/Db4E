import pytest
from db4e.Modules.DbMgr import DbMgr

def test_configmgr_init(config):
    from db4e.Modules.DbMgr import DbMgr
    db_mgr = DbMgr(config)
    assert db_mgr is not None
