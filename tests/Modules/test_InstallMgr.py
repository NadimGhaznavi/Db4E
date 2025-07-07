"""
tests/Modules/test_InstallMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
from db4e.Modules.InstallMgr import InstallMgr

def test_configmgr_init(config):
    install_mgr = InstallMgr(config)
    assert install_mgr is not None

