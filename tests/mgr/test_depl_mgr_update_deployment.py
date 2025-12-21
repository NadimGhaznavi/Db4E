# db4e/tests/mgr/test_depl_mgr_update_deployment.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import os
import socket

from db4e.mgr.InstallMgr import InstallMgr
from db4e.mgr.DeplMgr import DeplMgr

from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig

from db4e.constants.DElem import DElem
from db4e.constants.DDir import DDir
from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField
from db4e.constants.DDef import DDef


def test_update_db4e(
    initialized_depl_mgr,
    initialized_sql_db,
    initialized_bootstrap_mgr,
    initialized_depl_db,
):
    depl_mgr = initialized_depl_mgr
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr
    depl_db = initialized_depl_db

    vendor_dir = bs_mgr.get_dir(DDir.VENDOR)

    # Get a Db4E instance for testing
    db4e = Db4E()
    db4e.instance(DElem.DB4E)
    db4e.user_wallet("user_wallet")
    db4e.vendor_dir(vendor_dir)
    depl_db.insert_one(db4e)

    rows = sql_db.execute_query("SELECT * from db4e")
    assert len(rows) == 1
    assert rows[0]["instance"] == DElem.DB4E
    assert rows[0]["user_wallet"] == "user_wallet"
    assert rows[0]["vendor_dir"] == vendor_dir

    # Update user wallet
    db4e.user_wallet("new_user_wallet")
    depl_mgr.update_deployment(db4e)

    rows = sql_db.execute_query("SELECT * from db4e")
    assert len(rows) == 1
    assert rows[0]["instance"] == DElem.DB4E
    assert rows[0]["user_wallet"] == "new_user_wallet"
    assert rows[0]["vendor_dir"] == vendor_dir

    # Confirm that the primary server setting is initialized as disabled
    assert rows[0]["primary_server"] == DField.DISABLE
    assert rows[0]["primary_remote"] == DField.DISABLE

    rows = sql_db.execute_query("SELECT * from tui_log_line")

    assert len(rows) == 2
    assert rows[0]["tracked_instance"] == DLabel.DB4E
    assert rows[0]["tracked_type"] == DElem.DB4E
    assert rows[0]["message"] == DLabel.USER_WALLET
    assert rows[0]["details"] is not None

    # We need a Monero instance to test with
    mon_a = MoneroD()
    mon_a.instance("mon_a")
    mon_a = depl_mgr.add_deployment(mon_a)

    # We need internal P2Pool instances for testing
    install_mgr = InstallMgr(bs_mgr=bs_mgr)
    install_mgr._deploy_internal_p2pools(db4e=db4e)

    # Set a primary server
    db4e.primary_server(mon_a.id())
    db4e.primary_remote(0)
    depl_mgr.update_deployment(db4e)

    rows = sql_db.execute_query("SELECT * from db4e")
    assert len(rows) == 1
    row = rows[0]
    assert row["primary_server"] == mon_a.id()
    assert row["primary_remote"] == 0

    # Confirm that the internal P2Pool instances are now using the primary server
    rows = sql_db.execute_query("SELECT * from p2pool_internal")
    assert len(rows) == 3

    for row in rows:
        assert row["parent"] == mon_a.id()
        assert row["parent_remote"] == 0

    db4e.primary_server(DField.DISABLE)
    db4e.primary_remote(DField.DISABLE)
    depl_mgr.update_deployment(db4e)

    rows = sql_db.execute_query("SELECT * from db4e")
    assert len(rows) == 1
    row = rows[0]
    assert row["primary_server"] == DField.DISABLE
    assert row["primary_remote"] == DField.DISABLE


def test_update_monerod(
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

    mon_a.blockchain_dir("blockchain_dir")
    mon_a.in_peers(2)
    mon_a.ip_addr("10.10.10.10")
    mon_a.max_log_files(2)
    mon_a.max_log_size(200)
    mon_a.out_peers(3)
    mon_a.p2p_bind_port(123)
    mon_a.rpc_bind_port(456)
    mon_a.priority_node_1("p1")
    mon_a.priority_node_2("p2")
    mon_a.priority_port_1("78")
    mon_a.priority_port_2("90")

    depl_mgr.update_deployment(mon_a)

    rows = sql_db.execute_query("SELECT * from monerod")
    assert len(rows) == 1
    row = rows[0]
    assert row["instance"] == "mon_a"
    assert row["blockchain_dir"] == "blockchain_dir"
    assert row["in_peers"] == 2
    assert row["ip_addr"] == "10.10.10.10"
    assert row["max_log_files"] == 2
    assert row["max_log_size"] == 200
    assert row["out_peers"] == 3
    assert row["p2p_bind_port"] == 123
    assert row["rpc_bind_port"] == 456
    assert row["priority_node_1"] == "p1"
    assert row["priority_node_2"] == "p2"
    assert row["priority_port_1"] == 78
    assert row["priority_port_2"] == 90

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 13


def test_update_monerod_remote(
    initialized_bootstrap_mgr,
    initialized_sql_db,
    initialized_depl_db,
    initialized_ops_db,
):
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr
    depl_db = initialized_depl_db
    ops_db = initialized_ops_db

    depl_mgr = DeplMgr(bs_mgr=bs_mgr, sql_db=sql_db, depl_db=depl_db, ops_db=ops_db)

    vendor_dir = bs_mgr.get_dir(DDir.VENDOR)

    # Get a MoneroDRemote instance for testing
    mon_a = MoneroDRemote()
    mon_a.instance("mon_a")
    mon_a = depl_mgr.add_deployment(mon_a)

    mon_a.ip_addr("10.10.10.10")
    mon_a.rpc_bind_port(456)
    mon_a.zmq_pub_port(789)

    depl_mgr.update_deployment(mon_a)

    rows = sql_db.execute_query("SELECT * from monerod_remote")
    assert len(rows) == 1
    row = rows[0]
    assert row["instance"] == "mon_a"
    assert row["ip_addr"] == "10.10.10.10"
    assert row["rpc_bind_port"] == 456
    assert row["zmq_pub_port"] == 789

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 4


def test_update_p2pool(
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

    mon_b = MoneroD()
    mon_b.instance("mon_b")
    mon_b = depl_mgr.add_deployment(mon_b)

    # Get a P2Pool instance for testing
    p2p_a = P2Pool()
    p2p_a.instance("p2p_a")
    p2p_a.parent(mon_a.id())
    p2p_a.parent_remote(0)
    p2p_a = depl_mgr.add_deployment(p2p_a)

    p2p_a.enabled(True)
    p2p_a.in_peers(3)
    p2p_a.out_peers(4)
    p2p_a.p2p_port(12345)
    p2p_a.stratum_port(23456)
    p2p_a.log_level(1)
    p2p_a.parent(mon_b.id())
    p2p_a.parent_remote(0)
    p2p_a.chain(DField.NANO_CHAIN)

    depl_mgr.update_deployment(p2p_a)

    rows = sql_db.execute_query("SELECT * from p2pool")
    assert len(rows) == 1
    row = rows[0]
    assert row["instance"] == "p2p_a"
    assert row["enabled"] == 1
    assert row["in_peers"] == 3
    assert row["out_peers"] == 4
    assert row["p2p_port"] == 12345
    assert row["stratum_port"] == 23456
    assert row["log_level"] == 1
    assert row["parent"] == mon_b.id()
    assert row["parent_remote"] == 0
    assert row["chain"] == DField.NANO_CHAIN

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 11


def test_update_p2pool_remote(
    initialized_bootstrap_mgr,
    initialized_sql_db,
    initialized_depl_db,
    initialized_ops_db,
):
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr
    depl_db = initialized_depl_db
    ops_db = initialized_ops_db

    depl_mgr = DeplMgr(bs_mgr=bs_mgr, sql_db=sql_db, depl_db=depl_db, ops_db=ops_db)

    # Get a P2PoolRemote instance for testing
    p2p_a = P2PoolRemote()
    p2p_a.instance("p2p_a")
    p2p_a = depl_mgr.add_deployment(p2p_a)

    p2p_a.ip_addr("10.10.10.10")
    p2p_a.stratum_port(1234)

    depl_mgr.update_deployment(p2p_a)

    rows = sql_db.execute_query("SELECT * from p2pool_remote")
    assert len(rows) == 1
    row = rows[0]
    assert row["instance"] == "p2p_a"
    assert row["ip_addr"] == "10.10.10.10"
    assert row["stratum_port"] == 1234

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 3


def test_update_p2pool_internal(
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

    install_mgr = InstallMgr(bs_mgr=bs_mgr)
    install_mgr._deploy_internal_p2pools(db4e=db4e)

    mon_a = MoneroD()
    mon_a.instance("mon_a")
    mon_a = depl_mgr.add_deployment(mon_a)

    # Get an internal P2Pool instance for testing
    p2p_a = depl_db.get_deployment(DElem.P2POOL_INTERNAL, DLabel.MAIN_CHAIN)
    p2p_a.enabled(True)
    p2p_a.in_peers(3)
    p2p_a.out_peers(4)
    p2p_a.p2p_port(12345)
    p2p_a.stratum_port(23456)
    p2p_a.log_level(1)
    p2p_a.parent(mon_a.id())
    p2p_a.parent_remote(0)
    p2p_a.chain(DField.NANO_CHAIN)

    depl_mgr.update_deployment(p2p_a)

    rows = sql_db.execute_query("SELECT * from p2pool_internal")
    assert len(rows) == 3
    row = None
    for rec in rows:
        if rec["instance"] == DLabel.MAIN_CHAIN:
            row = rec
            break
    assert row is not None
    assert row["enabled"] == 1
    assert row["in_peers"] == 3
    assert row["out_peers"] == 4
    assert row["p2p_port"] == 12345
    assert row["stratum_port"] == 23456
    assert row["log_level"] == 1
    assert row["parent"] == mon_a.id()
    assert row["parent_remote"] == 0
    assert row["chain"] == DField.NANO_CHAIN

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 12


def test_update_xmrig(
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

    p2p_a = P2Pool()
    p2p_a.instance("p2p_a")
    p2p_a.ip_addr("10.10.10.10")
    p2p_a.stratum_port(3333)
    p2p_a = depl_mgr.add_deployment(p2p_a)

    p2p_b = P2Pool()
    p2p_b.instance("p2p_b")
    p2p_b.ip_addr("10.10.10.11")
    p2p_b.stratum_port(4444)
    p2p_b = depl_mgr.add_deployment(p2p_b)

    # Get a XMRig instance for testing
    xm_a = XMRig()
    xm_a.instance("xm_a")
    xm_a.parent(p2p_a.id())
    xm_a.parent_remote(0)
    xm_a = depl_mgr.add_deployment(xm_a)

    xm_a.enabled(True)
    xm_a.num_threads(2)
    xm_a.parent(p2p_b.id())
    xm_a.parent_remote(0)

    depl_mgr.update_deployment(xm_a)

    rows = sql_db.execute_query("SELECT * from xmrig")
    assert len(rows) == 1
    row = rows[0]
    assert row["instance"] == "xm_a"
    assert row["enabled"] == 1
    assert row["num_threads"] == 2
    assert row["parent"] == p2p_b.id()
    assert row["parent_remote"] == 0
    assert row["version"] == DDef.XMRIG_VERSION

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 6
