"""
tests/Modules/test_PaneCatalogue.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""
from db4e.Modules.PaneCatalogue import PaneCatalogue

def test_configmgr_init():
    pane_catalogue = PaneCatalogue()
    assert pane_catalogue is not None
