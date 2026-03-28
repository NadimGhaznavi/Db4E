# db4e/tests/recs/monero/test_p2pool.py
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

from db4e.constants.DDef import DDef
from db4e.constants.DDir import DDir
from db4e.constants.DElem import DElem
from db4e.constants.DField import DField
from db4e.constants.DFile import DFile

import os
import socket


def test_new_p2pool_complete(
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

    # Get a P2Pool instance for testing
    p2p_a = P2Pool()
    p2p_a.instance("p2p_a")
    p2p_a.parent(mon_a.id())
    p2p_a.parent_remote(0)
    p2p_a = depl_mgr.add_deployment(p2p_a)

    rows = sql_db.execute_query("SELECT * from p2pool")
    assert len(rows) == 1

    rec = rows[0]
    assert rec["instance"] == "p2p_a"
    assert rec["any_ip"] == socket.gethostname()
    assert rec["chain"] == DField.MINI_CHAIN
    config_file = os.path.join(
        vendor_dir, DElem.P2POOL, DDef.CONF_DIR, "p2p_a" + DDef.INI_SUFFIX
    )
    assert rec["config_file"] == config_file
    assert rec["in_peers"] == DDef.IN_PEERS
    assert rec["ip_addr"] == ""
    log_file = os.path.join(
        vendor_dir, DElem.P2POOL, "p2p_a", DDef.LOG_DIR, DFile.P2POOL_LOG
    )
    assert rec["log_file"] == log_file
    assert rec["log_level"] == DDef.LOG_LEVEL
    logrotate_config = os.path.join(
        vendor_dir, DDef.LOGROTATE, DElem.P2POOL + "-p2p_a" + DDef.CONF_SUFFIX
    )
    assert rec["logrotate_config"] == logrotate_config
    assert rec["max_log_files"] == DDef.MAX_LOG_FILES
    assert rec["max_log_size"] == DDef.MAX_LOG_SIZE
    assert rec["out_peers"] == DDef.OUT_PEERS
    assert rec["p2p_port"] == DDef.P2P_PORT
    assert rec["parent"] == mon_a.id()
    assert rec["parent_remote"] == 0
    stdin_path = os.path.join(
        vendor_dir, DElem.P2POOL, "p2p_a", DDef.RUN_DIR, DFile.P2POOL_STDIN
    )
    assert rec["stdin_path"] == stdin_path
    assert rec["stratum_port"] == DDef.STRATUM_PORT
    assert rec["user_wallet"] == "test_wallet_value"
    assert rec["version"] == DDef.P2POOL_VERSION

    assert p2p_a.instance() == "p2p_a"
    assert p2p_a.any_ip() == socket.gethostname()
    assert p2p_a.chain() == DField.MINI_CHAIN
    assert p2p_a.config_file() == config_file
    assert p2p_a.in_peers() == DDef.IN_PEERS
    assert p2p_a.ip_addr() == ""
    assert p2p_a.log_file() == log_file
    assert p2p_a.log_level() == DDef.LOG_LEVEL
    assert p2p_a.logrotate_config() == logrotate_config
    assert p2p_a.max_log_files() == DDef.MAX_LOG_FILES
    assert p2p_a.max_log_size() == DDef.MAX_LOG_SIZE
    assert p2p_a.out_peers() == DDef.OUT_PEERS
    assert p2p_a.p2p_port() == DDef.P2P_PORT
    assert p2p_a.parent() == mon_a.id()
    assert p2p_a.parent_remote() == 0
    assert p2p_a.stdin_path() == stdin_path
    assert p2p_a.stratum_port() == DDef.STRATUM_PORT
    assert p2p_a.user_wallet() == "test_wallet_value"
    assert p2p_a.version() == DDef.P2POOL_VERSION
