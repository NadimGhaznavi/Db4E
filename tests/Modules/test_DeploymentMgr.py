import pytest
from db4e.Modules.DeploymentMgr import DeploymentMgr

def test_configmgr_init(config):
    depl_mgr = DeploymentMgr(config)
    assert depl_mgr is not None
