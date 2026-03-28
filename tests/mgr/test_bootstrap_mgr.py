# db4e/tests/mgr/test_bootstrap_mgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


import os, sys, json
import pytest

from unittest.mock import patch, Mock
from db4e.mgr.BootstrapMgr import BootstrapMgr
from db4e.constants.DDir import DDir
from db4e.constants.DElem import DElem
from db4e.constants.DDef import DDef
from db4e.constants.DFile import DFile
from db4e.constants.DField import DField


def test_unitialized_is_initialized(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    bs_mgr = BootstrapMgr()
    assert bs_mgr.is_initialized() is False


def test_uninitialized_get_dir_db(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    mgr = BootstrapMgr()
    with pytest.raises(RuntimeError):
        mgr.get_dir(DDir.DB)


def test_get_dir_db4e():
    mgr = BootstrapMgr()

    # Get the module object that contains BootstrapMgr
    module = sys.modules[BootstrapMgr.__module__]
    # Get the __file__ attribute of the module
    module_file = module.__file__
    # Calculate the correct value
    module_dir = os.path.dirname(module_file)
    expected = os.path.abspath(os.path.join(module_dir, ".."))
    # Get the value returned by BootstrapMgr
    result = mgr.get_dir(DElem.DB4E)
    # Compare the results
    assert result == expected


def test_get_dir_install():
    mgr = BootstrapMgr()

    module = sys.modules[BootstrapMgr.__module__]
    module_file = module.__file__
    module_dir = os.path.dirname(module_file)
    expected = os.path.abspath(os.path.join(module_dir, "..", "..", "..", "..", ".."))
    result = mgr.get_dir(DDir.INSTALL)
    assert result == expected


def test_get_dir_template():
    mgr = BootstrapMgr()

    module = sys.modules[BootstrapMgr.__module__]
    module_file = module.__file__
    module_dir = os.path.dirname(module_file)
    expected = os.path.abspath(
        os.path.join(module_dir, "..", "..", DElem.DB4E, DDef.TEMPLATES_DIR)
    )
    result = mgr.get_dir(DDir.TEMPLATE)
    assert result == expected


def test_unitialized_get_dir_logrotate(monkeypatch, tmp_path):
    # Redirect HOME to a temporary directory with no .db4e file
    monkeypatch.setenv("HOME", str(tmp_path))
    mgr = BootstrapMgr()
    with pytest.raises(RuntimeError):
        mgr.get_dir(DDir.LOGROTATE)


def test_get_dir_logrotate(tmp_dir):
    mgr = BootstrapMgr()
    mgr.initialize(tmp_dir)
    expected = os.path.join(tmp_dir, DDef.LOGROTATE)
    result = mgr.get_dir(DDir.LOGROTATE)
    assert result == expected


def test_get_dir_monerod():
    mgr = BootstrapMgr()
    expected = DElem.MONEROD
    result = mgr.get_dir(DElem.MONEROD)
    assert result == expected


def test_get_dir_p2pool():
    mgr = BootstrapMgr()
    expected = DElem.P2POOL
    result = mgr.get_dir(DElem.P2POOL)
    assert result == expected


def test_unitialized_get_dir_vendor(monkeypatch, tmp_path):
    # Redirect HOME to a clean temporary directory so no config exists
    monkeypatch.setenv("HOME", str(tmp_path))

    mgr = BootstrapMgr()

    # Assert that calling get_dir(DDir.VENDOR) raises RuntimeError
    with pytest.raises(RuntimeError):
        mgr.get_dir(DDir.VENDOR)


def test_initialized_get_dir_vendor(tmp_path, monkeypatch):
    # Switch HOME into a clean test directory
    monkeypatch.setenv("HOME", str(tmp_path))

    mgr = BootstrapMgr()

    # Create a fake vendor directory
    vendor_dir = tmp_path / "vendor"

    # Initialize BootstrapMgr using the real API
    mgr.initialize(str(vendor_dir))

    # Assert the manager is indeed "initialized"
    assert mgr.is_initialized()

    # Now test get_dir(DDir.VENDOR)
    result = mgr.get_dir(DDir.VENDOR)

    assert result == str(vendor_dir)


def test_get_dir_xmrig():
    mgr = BootstrapMgr()
    expected = DElem.XMRIG
    result = mgr.get_dir(DElem.XMRIG)
    assert result == expected


def test_get_file_python():
    mgr = BootstrapMgr()

    module = sys.modules[BootstrapMgr.__module__]
    module_file = module.__file__
    module_dir = os.path.dirname(module_file)
    expected = os.path.abspath(
        os.path.join(module_dir, "..", "..", "..", "..", "..", DDir.BIN, DDef.PYTHON)
    )
    result = mgr.get_file(DFile.PYTHON)
    assert result == expected


def test_get_logrotate_template_db4e(tmp_path):
    mgr = BootstrapMgr()

    # Make BootstrapMgr think it's initialized
    mgr._config[DField.VENDOR_DIR] = "/fake/vendor"

    fake_tmpl_dir = tmp_path / "templates"
    fake_tmpl_dir.mkdir()

    # Patch get_dir to return our fake template dir
    with patch.object(mgr, "get_dir", return_value=str(fake_tmpl_dir)):
        result = mgr.get_logrotate_template(DElem.DB4E)

    expected = os.path.abspath(
        os.path.join(
            fake_tmpl_dir,
            DElem.DB4E,
            DDef.CONF_DIR,
            f"{DElem.DB4E}-{DDef.LOGROTATE}{DDef.CONF_SUFFIX}",
        )
    )
    assert result == expected


def test_get_logrotate_template_p2pool(tmp_path):
    mgr = BootstrapMgr()

    # Make BootstrapMgr think it's initialized
    mgr._config[DField.VENDOR_DIR] = "/fake/vendor"

    fake_tmpl_dir = tmp_path / "templates"
    fake_tmpl_dir.mkdir()

    # Patch get_dir to return our fake template dir
    with patch.object(mgr, "get_dir", return_value=str(fake_tmpl_dir)):
        result = mgr.get_logrotate_template(DElem.P2POOL)

    expected = os.path.abspath(
        os.path.join(
            fake_tmpl_dir,
            DElem.P2POOL,
            DDef.CONF_DIR,
            f"{DElem.P2POOL}-{DDef.LOGROTATE}{DDef.CONF_SUFFIX}",
        )
    )

    assert result == expected


def test_get_logrotate_template_xmrig(tmp_path):
    mgr = BootstrapMgr()

    # Make BootstrapMgr think it's initialized
    mgr._config[DField.VENDOR_DIR] = "/fake/vendor"

    fake_tmpl_dir = tmp_path / "templates"
    fake_tmpl_dir.mkdir()

    # Patch get_dir to return our fake template dir
    with patch.object(mgr, "get_dir", return_value=str(fake_tmpl_dir)):
        result = mgr.get_logrotate_template(DElem.XMRIG)

    expected = os.path.abspath(
        os.path.join(
            fake_tmpl_dir,
            DElem.XMRIG,
            DDef.CONF_DIR,
            f"{DElem.XMRIG}-{DDef.LOGROTATE}{DDef.CONF_SUFFIX}",
        )
    )

    assert result == expected


import os
import pytest
from unittest.mock import patch


def test_get_template_various(tmp_path):
    mgr = BootstrapMgr()

    fake_tmpl_dir = tmp_path / "templates"
    fake_tmpl_dir.mkdir()

    # Define the mapping from argument -> return value
    dir_map = {
        DDir.TEMPLATE: str(fake_tmpl_dir),
        DElem.MONEROD: "monerod-0.18.3",
        DElem.P2POOL: "p2pool-1.6.6",
        DElem.XMRIG: "xmrig-6.18.0",
    }

    # side_effect function takes the argument passed to get_dir
    def fake_get_dir(arg):
        return dir_map[arg]

    with patch.object(mgr, "get_dir", side_effect=fake_get_dir):
        # MONEROD
        monerod_result = mgr.get_template(DElem.MONEROD)
        expected_monerod = os.path.join(
            fake_tmpl_dir, dir_map[DElem.MONEROD], DDef.CONF_DIR, DDef.MONEROD_CONFIG
        )
        assert monerod_result == expected_monerod

        # P2POOL
        p2pool_result = mgr.get_template(DElem.P2POOL)
        expected_p2pool = os.path.join(
            fake_tmpl_dir, dir_map[DElem.P2POOL], DDef.CONF_DIR, DDef.P2POOL_CONFIG
        )
        assert p2pool_result == expected_p2pool

        # XMRIG
        xmrig_result = mgr.get_template(DElem.XMRIG)
        expected_xmrig = os.path.join(
            fake_tmpl_dir, dir_map[DElem.XMRIG], DDef.CONF_DIR, DDef.XMRIG_CONFIG
        )
        assert xmrig_result == expected_xmrig

        # Unsupported element type
        with pytest.raises(ValueError):
            mgr.get_template("UNKNOWN_ELEMENT")
