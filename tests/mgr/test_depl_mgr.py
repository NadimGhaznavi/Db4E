# db4e/tests/mgr/test_depl_mgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import os

from db4e.mgr.DeplMgr import DeplMgr
from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig
from db4e.recs.monero.XMRigRemote import XMRigRemote

from db4e.constants.DDir import DDir
from db4e.constants.DDef import DDef
from db4e.constants.DElem import DElem


def test_add_deployment_monerod_full_integration(
    initialized_sql_db,
    initialized_bootstrap_mgr,
    initialized_depl_db,
    initialized_ops_db,
):
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr
    depl_db = initialized_depl_db
    ops_db = initialized_ops_db
    depl_mgr = DeplMgr(sql_db=sql_db, bs_mgr=bs_mgr, depl_db=depl_db, ops_db=ops_db)
    mon_a = MoneroD()
    mon_a.instance("test_monerod")
    depl_mgr.add_deployment(mon_a)
    # Confirm entry was added to the DB
    rows = sql_db.execute_query("SELECT * from monerod")
    assert len(rows) == 1
    assert rows[0]["instance"] == "test_monerod"

    mon_a = MoneroD(rec=rows[0])
    assert mon_a.instance() == "test_monerod"

    # Confirm the log_file attribute was set correctly
    vendor_dir = bs_mgr.get_dir(DDir.VENDOR)
    logfile = os.path.join(
        vendor_dir, DDir.MONEROD, "test_monerod", DDef.LOG_DIR, DDef.MONEROD_LOG_FILE
    )
    assert mon_a.log_file() == logfile

    # Confirm that the blockchain directory was created
    blockchain_dir = os.path.join(
        vendor_dir, DDir.MONEROD, "test_monerod", DDef.BLOCKCHAIN_DIR
    )
    assert os.path.exists(blockchain_dir)

    # Confirm that the run directory was created
    run_dir = os.path.join(vendor_dir, DDir.MONEROD, "test_monerod", DDef.RUN_DIR)
    assert os.path.exists(run_dir)

    # Confirm that the STDIN attribute was set correctly
    stdin_path = os.path.join(
        vendor_dir, DDir.MONEROD, "test_monerod", DDef.RUN_DIR, DDef.MONEROD_STDIN_PIPE
    )
    assert stdin_path == mon_a.stdin_path()

    # Confirm that the startup INI file was correctly generated
    startup_ini = os.path.join(
        vendor_dir, DElem.MONEROD, DDef.CONF_DIR, "test_monerod" + DDef.INI_SUFFIX
    )
    assert os.path.exists(startup_ini)

    config = {}
    with open(startup_ini) as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key] = value.strip('"')

    assert config["INSTANCE"] == "test_monerod"
    assert config["IP_ALL"] == "0.0.0.0"
    assert config["ZMQ_PUB_PORT"] == "18083"
    assert config["ZMQ_RPC_PORT"] == "18082"
    assert config["P2P_BIND_PORT"] == "18080"
    assert config["RPC_BIND_PORT"] == "18081"
    assert config["OUT_PEERS"] == "16"
    assert config["IN_PEERS"] == "16"
    assert config["LOG_LEVEL"] == "0"
    assert config["MAX_LOG_FILES"] == "7"
    assert config["MAX_LOG_SIZE"] == "10000000"
    assert config["SHOW_TIME_STATS"] == "1"
    assert config["PRIORITY_NODE_1"] == "p2pmd.xmrvsbeast.com"
    assert config["PRIORITY_NODE_1_PORT"] == "18080"
    assert config["PRIORITY_NODE_2"] == "nodes.hashvault.pro"
    assert config["PRIORITY_NODE_2_PORT"] == "18080"
    assert config["STDIN_PATH"] == stdin_path
    assert config["LOG_FILE"] == logfile
    assert config["MONEROD_DIR"] == vendor_dir + "/" + DDir.MONEROD
    assert (
        config["BLOCKCHAIN_DIR"]
        == vendor_dir + "/" + DDir.MONEROD + "/test_monerod/blockchain"
    )

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 1
    assert rows[0]["tracked_instance"] == "test_monerod"
    assert rows[0]["tracked_type"] == "monerod"


def test_add_deployment_monerod_remote(
    initialized_sql_db,
    initialized_bootstrap_mgr,
    initialized_depl_db,
    initialized_ops_db,
):
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr
    depl_db = initialized_depl_db
    ops_db = initialized_ops_db
    depl_mgr = DeplMgr(sql_db=sql_db, bs_mgr=bs_mgr, depl_db=depl_db, ops_db=ops_db)
    mon_a = MoneroDRemote()
    mon_a.instance("test_monerod_remote")
    depl_mgr.add_deployment(mon_a)

    rows = sql_db.execute_query("SELECT * from monerod_remote")
    assert len(rows) == 1
    assert rows[0]["instance"] == "test_monerod_remote"


def test_add_deployment_p2pool_full_integration(
    initialized_sql_db,
    initialized_bootstrap_mgr,
    initialized_depl_db,
    initialized_ops_db,
):
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr
    depl_db = initialized_depl_db
    ops_db = initialized_ops_db
    depl_mgr = DeplMgr(sql_db=sql_db, bs_mgr=bs_mgr, depl_db=depl_db, ops_db=ops_db)

    # P2Pool creation calls on db4e.group() to be created...
    db4e = Db4E()
    db4e.instance(DElem.DB4E)
    db4e.user_wallet("test_wallet_value")
    depl_db.insert_one(db4e)

    p2p_a = P2Pool()
    p2p_a.instance("test_p2pool")

    mon_a = MoneroD()
    mon_a.instance("test_monerod")
    mon_a.ip_addr("10.10.10.10")
    mon_a = depl_mgr.add_deployment(mon_a)

    p2p_a.parent(mon_a.id())
    p2p_a.parent_remote(0)
    p2p_a.any_ip("172.0.0.1")

    depl_mgr.add_deployment(p2p_a)

    rows = sql_db.execute_query("SELECT * from p2pool")
    assert len(rows) == 1
    assert rows[0]["instance"] == "test_p2pool"

    vendor_dir = bs_mgr.get_dir(DDir.VENDOR)
    log_file = os.path.join(
        vendor_dir, DDir.P2POOL, "test_p2pool", DDef.LOG_DIR, DDef.P2POOL_LOG_FILE
    )
    assert p2p_a.log_file() == log_file

    log_dir = os.path.join(vendor_dir, DDir.P2POOL, "test_p2pool", DDef.LOG_DIR)
    assert os.path.exists(log_dir)

    api_dir = os.path.join(vendor_dir, DDir.P2POOL, "test_p2pool", DDef.API_DIR)
    assert os.path.exists(api_dir)

    run_dir = os.path.join(vendor_dir, DDir.P2POOL, "test_p2pool", DDef.RUN_DIR)
    assert os.path.exists(run_dir)

    stdin_path = os.path.join(
        vendor_dir, DDir.P2POOL, "test_p2pool", DDef.RUN_DIR, DDef.P2POOL_STDIN_PIPE
    )
    assert stdin_path == p2p_a.stdin_path()
    assert p2p_a.stdin_path() == stdin_path

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 2
    assert rows[0]["tracked_instance"] == "test_monerod"
    assert rows[0]["tracked_type"] == "monerod"
    assert rows[1]["tracked_instance"] == "test_p2pool"
    assert rows[1]["tracked_type"] == "p2pool"

    startup_ini = os.path.join(
        vendor_dir, DElem.P2POOL, DDef.CONF_DIR, "test_p2pool" + DDef.INI_SUFFIX
    )
    assert os.path.exists(startup_ini)
    config = {}
    with open(startup_ini) as f:
        for line in f:
            if "=" in line:
                print(line, end="")
                key, value = line.strip().split("=", 1)
                config[key] = value.strip('"')

    assert config["WALLET"] == "test_wallet_value"
    assert config["P2P_DIR"] == vendor_dir + "/" + DDir.P2POOL
    assert config["MONERO_NODE"] == "10.10.10.10"
    assert config["ZMQ_PUB_PORT"] == "18083"
    assert config["ANY_IP"] == "172.0.0.1"
    assert config["STRATUM_PORT"] == "3333"
    assert config["LOG_LEVEL"] == "0"
    assert config["IN_PEERS"] == "16"
    assert config["OUT_PEERS"] == "16"
    assert config["API_DIR"] == api_dir
    assert config["RUN_DIR"] == run_dir
    assert config["LOG_DIR"] == log_dir
    assert config["CHAIN"] == "minisidechain"

    expected_keys = {
        "WALLET",
        "P2P_DIR",
        "MONERO_NODE",
        "ZMQ_PUB_PORT",
        "ANY_IP",
        "STRATUM_PORT",
        "LOG_LEVEL",
        "IN_PEERS",
        "OUT_PEERS",
        "API_DIR",
        "RUN_DIR",
        "LOG_DIR",
        "CHAIN",
    }

    assert expected_keys.issubset(config.keys())


def test_add_deployment_p2pool_remote(
    initialized_sql_db,
    initialized_bootstrap_mgr,
    initialized_depl_db,
    initialized_ops_db,
):
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr
    depl_db = initialized_depl_db
    ops_db = initialized_ops_db
    depl_mgr = DeplMgr(sql_db=sql_db, bs_mgr=bs_mgr, depl_db=depl_db, ops_db=ops_db)

    p2p_a = P2PoolRemote()
    p2p_a.instance("test_p2pool_remote")
    depl_mgr.add_deployment(p2p_a)

    rows = sql_db.execute_query("SELECT * from p2pool_remote")
    assert len(rows) == 1
    assert rows[0]["instance"] == "test_p2pool_remote"


def test_add_deployment_xmrig(
    initialized_sql_db,
    initialized_bootstrap_mgr,
    initialized_depl_db,
    initialized_ops_db,
):
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr
    depl_db = initialized_depl_db
    ops_db = initialized_ops_db
    depl_mgr = DeplMgr(sql_db=sql_db, bs_mgr=bs_mgr, depl_db=depl_db, ops_db=ops_db)

    # XMRig instances use db4e.group()
    db4e = Db4E()
    depl_db.insert_one(db4e)

    xmrig_a = XMRig()
    xmrig_a.instance("test_xmrig")
    depl_mgr.add_deployment(xmrig_a)

    rows = sql_db.execute_query("SELECT * from xmrig")
    assert len(rows) == 1
    assert rows[0]["instance"] == "test_xmrig"


def test_add_deployment_xmrig_remote(
    initialized_sql_db,
    initialized_bootstrap_mgr,
    initialized_depl_db,
    initialized_ops_db,
):
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr
    depl_db = initialized_depl_db
    ops_db = initialized_ops_db
    depl_mgr = DeplMgr(sql_db=sql_db, bs_mgr=bs_mgr, depl_db=depl_db, ops_db=ops_db)

    xmrig_a = XMRigRemote()
    xmrig_a.instance("test_xmrig_remote")
    depl_mgr.add_deployment(xmrig_a)

    rows = sql_db.execute_query("SELECT * from xmrig_remote")
    assert len(rows) == 1
    assert rows[0]["instance"] == "test_xmrig_remote"
