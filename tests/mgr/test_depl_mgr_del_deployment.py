# db4e/tests/mgr/test_depl_mgr_del_deployment.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import os

from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig
from db4e.recs.monero.XMRigRemote import XMRigRemote

from db4e.constants.DElem import DElem


def test_del_deployment_monerod(initialized_depl_mgr, initialized_sql_db):
    depl_mgr = initialized_depl_mgr
    sql_db = initialized_sql_db

    mon_a = MoneroD()
    mon_a.instance("mon_a")
    depl_mgr.add_deployment(mon_a)

    mon_b = MoneroD()
    mon_b.instance("mon_b")
    depl_mgr.add_deployment(mon_b)
    assert os.path.exists(mon_b.config_file())

    mon_c = MoneroD()
    mon_c.instance("mon_c")
    depl_mgr.add_deployment(mon_c)

    rows = sql_db.execute_query("SELECT * from monerod")
    assert len(rows) == 3

    depl_mgr.delete_deployment(mon_b)
    assert not os.path.exists(mon_b.config_file())

    rows = sql_db.execute_query("SELECT * from monerod")
    assert len(rows) == 2
    assert rows[0]["instance"] == "mon_a"
    assert rows[1]["instance"] == "mon_c"

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 4


def test_del_deployment_monerod_remote(initialized_depl_mgr, initialized_sql_db):
    depl_mgr = initialized_depl_mgr
    sql_db = initialized_sql_db

    mon_a = MoneroDRemote()
    mon_a.instance("mon_a")
    depl_mgr.add_deployment(mon_a)

    mon_b = MoneroDRemote()
    mon_b.instance("mon_b")
    depl_mgr.add_deployment(mon_b)

    mon_c = MoneroDRemote()
    mon_c.instance("mon_c")
    depl_mgr.add_deployment(mon_c)

    rows = sql_db.execute_query("SELECT * from monerod_remote")
    assert len(rows) == 3

    depl_mgr.delete_deployment(mon_b)

    rows = sql_db.execute_query("SELECT * from monerod_remote")
    assert len(rows) == 2

    rows = sql_db.execute_query("SELECT * from tui_log_line")
    assert len(rows) == 4


def test_del_deployment_p2pool(
    initialized_depl_mgr, initialized_sql_db, initialized_depl_db
):
    depl_mgr = initialized_depl_mgr
    sql_db = initialized_sql_db
    depl_db = initialized_depl_db

    # P2Pool instances use db4e.group()
    db4e = Db4E()
    db4e.instance(DElem.DB4E)
    db4e.user_wallet("test_wallet_value")
    depl_db.insert_one(db4e)

    p2p_a = P2Pool()
    p2p_a.instance("p2p_a")
    depl_mgr.add_deployment(p2p_a)

    # P2Pool required upstream MoneroD before generating a config
    mon_a = MoneroD()
    mon_a.instance("mon_a")
    mon_a.ip_addr("10.10.10.10")
    mon_a = depl_mgr.add_deployment(mon_a)

    p2p_b = P2Pool()
    p2p_b.parent(mon_a.id())
    p2p_b.parent_remote(0)
    p2p_b.instance("p2p_b")
    p2p_b = depl_mgr.add_deployment(p2p_b)
    config_file = p2p_b.config_file()
    print(f"config_file: {config_file}")
    logrotate_config = p2p_b.logrotate_config()
    assert os.path.exists(config_file)
    assert os.path.exists(logrotate_config)

    p2p_c = P2Pool()
    p2p_c.instance("p2p_c")
    depl_mgr.add_deployment(p2p_c)

    rows = sql_db.execute_query("SELECT * from p2pool")
    assert len(rows) == 3

    depl_mgr.delete_deployment(p2p_b)

    assert os.path.exists(config_file) == False
    assert os.path.exists(logrotate_config) == False


def test_del_deployment_p2pool_remote(initialized_depl_mgr, initialized_sql_db):
    depl_mgr = initialized_depl_mgr
    sql_db = initialized_sql_db

    p2p_a = P2PoolRemote()
    p2p_a.instance("p2p_a")
    depl_mgr.add_deployment(p2p_a)

    p2p_b = P2PoolRemote()
    p2p_b.instance("p2p_b")
    depl_mgr.add_deployment(p2p_b)

    p2p_c = P2PoolRemote()
    p2p_c.instance("p2p_c")
    depl_mgr.add_deployment(p2p_c)

    rows = sql_db.execute_query("SELECT * from p2pool_remote")
    assert len(rows) == 3

    depl_mgr.delete_deployment(p2p_b)

    rows = sql_db.execute_query("SELECT * from p2pool_remote")
    assert len(rows) == 2

    for row in rows:
        assert row["instance"] != "p2p_b"


def test_del_xmrig(initialized_depl_mgr, initialized_sql_db, initialized_depl_db):
    depl_mgr = initialized_depl_mgr
    sql_db = initialized_sql_db
    depl_db = initialized_depl_db

    # XMRig instances use db4e.group()
    db4e = Db4E()
    db4e.instance(DElem.DB4E)
    depl_db.insert_one(db4e)

    xmrig_a = XMRig()
    xmrig_a.instance("xmrig_a")
    depl_mgr.add_deployment(xmrig_a)

    # Create an upstream P2Pool instance
    p2p_a = P2Pool()
    p2p_a.instance("p2p_a")
    p2p_a.ip_addr("10.10.10.10")
    p2p_a.stratum_port(3333)
    p2p_a = depl_mgr.add_deployment(p2p_a)

    xmrig_b = XMRig()
    xmrig_b.instance("xmrig_b")
    xmrig_b.parent(p2p_a.id())
    xmrig_b.parent_remote(0)
    depl_mgr.add_deployment(xmrig_b)

    xmrig_c = XMRig()
    xmrig_c.instance("xmrig_c")
    depl_mgr.add_deployment(xmrig_c)

    rows = sql_db.execute_query("SELECT * from xmrig")
    assert len(rows) == 3

    config_file = xmrig_b.config_file()
    logrotate_config = xmrig_b.logrotate_config()
    assert os.path.exists(config_file)
    assert os.path.exists(logrotate_config)

    depl_mgr.delete_deployment(xmrig_b)

    assert os.path.exists(config_file) == False
    assert os.path.exists(logrotate_config) == False

    rows = sql_db.execute_query("SELECT * from xmrig")
    assert len(rows) == 2

    for row in rows:
        assert row["instance"] != "xmrig_b"


def test_del_xmrig_remote(initialized_depl_mgr, initialized_sql_db):
    depl_mgr = initialized_depl_mgr
    sql_db = initialized_sql_db

    xmrig_a = XMRigRemote()
    xmrig_a.instance("xmrig_a")
    depl_mgr.add_deployment(xmrig_a)

    xmrig_b = XMRigRemote()
    xmrig_b.instance("xmrig_b")
    depl_mgr.add_deployment(xmrig_b)

    xmrig_c = XMRigRemote()
    xmrig_c.instance("xmrig_c")
    depl_mgr.add_deployment(xmrig_c)

    rows = sql_db.execute_query("SELECT * from xmrig_remote")
    assert len(rows) == 3

    depl_mgr.delete_deployment(xmrig_b)

    rows = sql_db.execute_query("SELECT * from xmrig_remote")
    assert len(rows) == 2

    for row in rows:
        assert row["instance"] != "xmrig_b"
