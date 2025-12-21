# db4e/tests/mgr/test_monerod.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from db4e.mgr.DeplMgr import DeplMgr

from db4e.recs.monero.MoneroD import MoneroD

from db4e.constants.DElem import DElem
from db4e.constants.DDef import DDef
from db4e.constants.DDir import DDir

import os
import socket


def test_new_monerod_complete(
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

    # Get a MoneroD instance for testing
    mon_a = MoneroD()
    mon_a.instance("mon_a")
    mon_a = depl_mgr.add_deployment(mon_a)

    rows = sql_db.execute_query("SELECT * from monerod")
    assert len(rows) == 1

    rec = rows[0]
    assert rec["instance"] == "mon_a"
    blockchain_dir = os.path.join(
        vendor_dir, DElem.MONEROD, "mon_a", DDef.BLOCKCHAIN_DIR
    )
    assert rec["blockchain_dir"] == blockchain_dir
    config_file = os.path.join(
        vendor_dir, DElem.MONEROD, DDef.CONF_DIR, "mon_a" + DDef.INI_SUFFIX
    )
    assert rec["config_file"] == config_file
    assert rec["in_peers"] == DDef.IN_PEERS
    assert rec["ip_addr"] == socket.gethostname()
    log_file = os.path.join(
        vendor_dir, DElem.MONEROD, "mon_a", DDef.LOG_DIR, DDef.MONEROD_LOG_FILE
    )
    assert rec["log_file"] == log_file
    assert rec["max_log_files"] == DDef.MAX_LOG_FILES
    assert rec["max_log_size"] == DDef.MAX_LOG_SIZE
    assert rec["out_peers"] == DDef.OUT_PEERS
    assert rec["p2p_bind_port"] == DDef.P2P_BIND_PORT
    assert rec["rpc_bind_port"] == DDef.RPC_BIND_PORT
    assert rec["priority_node_1"] == DDef.PRIORITY_NODE_1
    assert rec["priority_node_2"] == DDef.PRIORITY_NODE_2
    assert rec["priority_port_1"] == DDef.P2P_BIND_PORT
    assert rec["priority_port_2"] == DDef.P2P_BIND_PORT
    assert rec["rpc_bind_port"] == DDef.RPC_BIND_PORT
    assert rec["show_time_stats"] == DDef.SHOW_TIME_STATS
    stdin_path = os.path.join(
        vendor_dir, DElem.MONEROD, "mon_a", DDef.RUN_DIR, DDef.MONEROD_STDIN_PIPE
    )
    assert rec["stdin_path"] == stdin_path

    assert mon_a.instance() == "mon_a"
    assert mon_a.blockchain_dir() == blockchain_dir
    assert mon_a.config_file() == config_file
    assert mon_a.in_peers() == DDef.IN_PEERS
    assert mon_a.ip_addr() == socket.gethostname()
    assert mon_a.log_file() == log_file
    assert mon_a.max_log_files() == DDef.MAX_LOG_FILES
    assert mon_a.max_log_size() == DDef.MAX_LOG_SIZE
    assert mon_a.out_peers() == DDef.OUT_PEERS
    assert mon_a.p2p_bind_port() == DDef.P2P_BIND_PORT
    assert mon_a.rpc_bind_port() == DDef.RPC_BIND_PORT
    assert mon_a.priority_node_1() == DDef.PRIORITY_NODE_1
    assert mon_a.priority_node_2() == DDef.PRIORITY_NODE_2
    assert mon_a.priority_port_1() == DDef.P2P_BIND_PORT
    assert mon_a.priority_port_2() == DDef.P2P_BIND_PORT
    assert mon_a.rpc_bind_port() == DDef.RPC_BIND_PORT
    assert mon_a.show_time_stats() == DDef.SHOW_TIME_STATS
    assert mon_a.stdin_path() == stdin_path
