# db4e/tests/mgr/test_depl_mgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from db4e.mgr.DeplMgr import DeplMgr
from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig
from db4e.recs.monero.XMRigRemote import XMRigRemote


def test_add_deployment_monerod(
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

    rows = sql_db.execute_query("SELECT * from monerod")
    assert len(rows) == 1
    assert rows[0]["instance"] == "test_monerod"


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


def test_add_deployment_p2pool(
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
    depl_db.insert_one(db4e)

    p2p_a = P2Pool()
    p2p_a.instance("test_p2pool")
    depl_mgr.add_deployment(p2p_a)

    rows = sql_db.execute_query("SELECT * from p2pool")
    assert len(rows) == 1
    assert rows[0]["instance"] == "test_p2pool"


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
