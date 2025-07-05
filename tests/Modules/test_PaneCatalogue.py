import pytest
from db4e.Modules.PaneCatalogue import PaneCatalogue

def test_configmgr_init():
    pane_catalogue = PaneCatalogue()
    assert pane_catalogue is not None
