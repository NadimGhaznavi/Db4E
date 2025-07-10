"""
tests/Modules/test_DeploymentMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
from unittest.mock import MagicMock
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Constants.Fields import (
    DB4E_FIELD, USER_WALLET_FIELD, VENDOR_DIR_FIELD
)

def test_configmgr_init(config):
    depl_mgr = DeploymentMgr(config)
    assert depl_mgr is not None

