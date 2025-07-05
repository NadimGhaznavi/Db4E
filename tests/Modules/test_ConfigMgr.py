import sys
from db4e.Modules.ConfigMgr import ConfigMgr

def test_configmgr_init(monkeypatch):
    # Fake command-line args: ['script_name', '-b']
    monkeypatch.setattr(sys, 'argv', ['test_script', '-b'])
    cfg = ConfigMgr("0.16.1")
    assert cfg is not None
