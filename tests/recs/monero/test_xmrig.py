# db4e/tests/mgr/test_xmrig.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from db4e.mgr.DeplMgr import DeplMgr

from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.XMRig import XMRig

from db4e.constants.DDef import DDef
from db4e.constants.DDir import DDir
from db4e.constants.DElem import DElem

import os


def test_new_xmrig_complete(
    initialized_sql_db,
    initialized_bootstrap_mgr,
    initialized_depl_db,
    initialized_ops_db,
):
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr
    depl_db = initialized_depl_db
    ops_db = initialized_ops_db

    depl_mgr = DeplMgr(bs_mgr=bs_mgr, sql_db=sql_db, depl_db=depl_db, ops_db=ops_db)

    vendor_dir = bs_mgr.get_dir(DDir.VENDOR)

    db4e = Db4E()
    db4e.instance(DElem.DB4E)
    db4e.user_wallet("test_wallet_value")
    db4e.vendor_dir(vendor_dir)
    depl_db.insert_one(db4e)

    mon_a = MoneroD()
    mon_a.instance("mon_a")
    mon_a = depl_mgr.add_deployment(mon_a)

    p2p_a = P2Pool()
    p2p_a.instance("p2p_a")
    p2p_a.parent(mon_a.id())
    p2p_a.parent_remote(0)
    p2p_a = depl_mgr.add_deployment(p2p_a)

    # Get a XMRig instance for testing
    xm_a = XMRig()
    xm_a.instance("xm_a")
    xm_a.parent(p2p_a.id())
    xm_a.parent_remote(0)
    xm_a = depl_mgr.add_deployment(xm_a)

    rows = sql_db.execute_query("SELECT * from xmrig")
    assert len(rows) == 1

    rec = rows[0]
    assert rec["instance"] == "xm_a"
    config_file = os.path.join(
        vendor_dir, DElem.XMRIG, DDef.CONF_DIR, "xm_a" + DDef.JSON_SUFFIX
    )
    assert rec["config_file"] == config_file
    log_file = os.path.join(
        vendor_dir, DElem.XMRIG, DDef.LOG_DIR, "xm_a" + DDef.LOG_SUFFIX
    )
    assert rec["log_file"] == log_file
    logrotate_config = os.path.join(
        vendor_dir, DDef.LOGROTATE, DElem.XMRIG + "-xm_a" + DDef.CONF_SUFFIX
    )
    assert rec["logrotate_config"] == logrotate_config
    assert rec["max_log_files"] == DDef.MAX_LOG_FILES
    assert rec["max_log_size"] == DDef.MAX_LOG_SIZE
    assert rec["num_threads"] == 1
    assert rec["parent"] == p2p_a.id()
    assert rec["parent_remote"] == 0
    assert rec["version"] == DDef.XMRIG_VERSION

    assert xm_a.instance() == "xm_a"
    assert xm_a.config_file() == config_file
    assert xm_a.log_file() == log_file
    assert xm_a.logrotate_config() == logrotate_config
    assert xm_a.max_log_files() == DDef.MAX_LOG_FILES
    assert xm_a.max_log_size() == DDef.MAX_LOG_SIZE
    assert xm_a.num_threads() == 1
    assert xm_a.parent() == p2p_a.id()
    assert xm_a.parent_remote() == 0
    assert xm_a.version() == DDef.XMRIG_VERSION
