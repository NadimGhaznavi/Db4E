# db4e/tests/mgr/test_xmrig_remote.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from db4e.mgr.DeplMgr import DeplMgr

from db4e.recs.monero.XMRigRemote import XMRigRemote


def test_new_xmrig_remote_complete(
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

    # Get a XMRigRemote instance for testing
    xm_a = XMRigRemote()
    xm_a.instance("xm_a")
    xm_a = depl_mgr.add_deployment(xm_a)

    rows = sql_db.execute_query("SELECT * from xmrig_remote")
    assert len(rows) == 1

    rec = rows[0]
    assert rec["instance"] == "xm_a"
    assert rec["ip_addr"] is None

    assert xm_a.instance() == "xm_a"
    assert xm_a.ip_addr() is None
