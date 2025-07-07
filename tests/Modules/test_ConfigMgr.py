"""
tests/Modules/test_ConfigMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

import sys
import pytest
from db4e.Modules.ConfigMgr import ConfigMgr

def test_configmgr_init(monkeypatch):
    # Fake command-line args: ['script_name', '-b']
    monkeypatch.setattr(sys, 'argv', ['test_script', '-b'])
    cfg = ConfigMgr("0.16.1")
    assert cfg is not None

def test_configmgr_backup(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['script', '-b'])
    cfg = ConfigMgr("0.16.1")
    assert cfg.get_config().config['db4e']['op'] == 'run_backup'


def test_configmgr_service(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['script', '-s'])
    cfg = ConfigMgr("0.16.1")
    assert cfg.get_config().config['db4e']['op'] == 'run_daemon'


def test_configmgr_default(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['script'])
    cfg = ConfigMgr("0.16.1")
    assert cfg.get_config().config['db4e']['op'] == 'run_ui'


def test_configmgr_version(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['script', '-v'])

    # Intercept sys.exit() and assert it's called
    with pytest.raises(SystemExit) as e:
        ConfigMgr("0.16.1")
    assert e.type == SystemExit
    assert e.value.code == 0