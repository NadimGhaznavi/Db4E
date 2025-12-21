# db4e/tests/mgr/test_monerod_remote.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from db4e.mgr.DeplMgr import DeplMgr

from db4e.recs.monero.MoneroDRemote import MoneroDRemote

from db4e.constants.DDef import DDef


def test_new_monerod_remote_complete(
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

    # Get a MoneroDRemote instance for testing
    mon_a = MoneroDRemote()
    mon_a.instance("mon_a")
    mon_a = depl_mgr.add_deployment(mon_a)

    rows = sql_db.execute_query("SELECT * from monerod_remote")
    assert len(rows) == 1

    rec = rows[0]
    assert rec["instance"] == "mon_a"
    assert rec["ip_addr"] == ""
    assert rec["rpc_bind_port"] == DDef.RPC_BIND_PORT
    assert rec["zmq_pub_port"] == DDef.ZMQ_PUB_PORT

    assert mon_a.instance() == "mon_a"
    assert mon_a.ip_addr() == ""
    assert mon_a.rpc_bind_port() == DDef.RPC_BIND_PORT
    assert mon_a.zmq_pub_port() == DDef.ZMQ_PUB_PORT
