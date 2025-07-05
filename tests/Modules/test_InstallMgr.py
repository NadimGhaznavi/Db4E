import pytest
from db4e.Modules.InstallMgr import InstallMgr

def test_configmgr_init(config):
    from db4e.Modules.InstallMgr import InstallMgr
    install_mgr = InstallMgr(config)
    assert install_mgr is not None
