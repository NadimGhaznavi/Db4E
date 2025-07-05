import pytest
from db4e.Modules.PaneMgr import PaneMgr
from db4e.Modules.PaneCatalogue import PaneCatalogue

def test_configmgr_init(config):
    catalogue = PaneCatalogue()
    initialized_flag = True
    pane_mgr = PaneMgr(config, catalogue, initialized_flag)
    
    assert pane_mgr is not None
