import pytest

def test_configmgr_init(config):
    from db4e.Modules.DeploymentMgr import DeploymentMgr
    depl_mgr = DeploymentMgr(config)
    assert depl_mgr is not None
