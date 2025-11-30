# db4e/tests/mgr/test_bootstrap_mgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


import os, sys
from db4e.mgr.BootstrapMgr import BootstrapMgr
from db4e.constants.DDir import DDir
from db4e.constants.DElem import DElem
from db4e.constants.DDef import DDef
from db4e.constants.DFile import DFile


def test_unitialized_is_initialized(uninitialized_bootstrap_mgr):
    assert uninitialized_bootstrap_mgr.is_initialized() is False


def test_uninitialized_get_dir_db(uninitialized_bootstrap_mgr):
    try:
        uninitialized_bootstrap_mgr.get_dir(DDir.DB)
        assert False
    except RuntimeError:
        assert True


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


def test_unitialized_get_dir_logrotate():
    mgr = BootstrapMgr()
    try:
        mgr.get_dir(DDir.LOGROTATE)
        assert False
    except RuntimeError:
        assert True


def test_get_dir_logrotate(tmp_dir):
    mgr = BootstrapMgr()
    mgr.initialize(tmp_dir)
    expected = os.path.join(tmp_dir, DDef.LOGROTATE)
    result = mgr.get_dir(DDir.LOGROTATE)
    assert result == expected


def test_get_dir_monerod():
    mgr = BootstrapMgr()
    expected = DElem.MONEROD + "-" + DDef.MONEROD_VERSION
    result = mgr.get_dir(DElem.MONEROD)
    assert result == expected
