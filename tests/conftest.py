# tests/conftest.py
import sys
import pytest
from db4e.Modules.ConfigMgr import ConfigMgr

@pytest.fixture
def config(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['test_script', '-b'])
    cfg = ConfigMgr("0.16.1")

    cfg.config = {
        "db": {
            "retry_timeout": 5,
            "server": "localhost",
            "port": 27017,
            "max_backups": 7,
            "name": "db4e",
            "collection": "mining",
            "depl_collection": "depl",
            "log_collection": "logging",
            "log_retention_days": 7,
            "metrics_collection": "metrics",

        }
    }





    return cfg