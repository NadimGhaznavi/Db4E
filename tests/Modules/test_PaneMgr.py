"""
tests/Modules/test_PaneMgr.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""
from db4e.Modules.PaneMgr import PaneMgr
from db4e.Modules.PaneCatalogue import PaneCatalogue

def test_configmgr_init(config):
    catalogue = PaneCatalogue()
    initialized_flag = True
    pane_mgr = PaneMgr(config, catalogue, initialized_flag)
    
    assert pane_mgr is not None
