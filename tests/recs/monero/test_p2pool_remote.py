# db4e/tests/recs/monero/test_p2pool_remote.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from db4e.mgr.DeplMgr import DeplMgr

from db4e.recs.monero.P2PoolRemote import P2PoolRemote

from db4e.constants.DDef import DDef


def test_new_p2pool_remote_complete(
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

    # Get a P2PoolRemote instance for testing
    p2p_a = P2PoolRemote()
    p2p_a.instance("p2p_a")
    p2p_a = depl_mgr.add_deployment(p2p_a)

    rows = sql_db.execute_query("SELECT * from p2pool_remote")
    assert len(rows) == 1

    rec = rows[0]
    assert rec["instance"] == "p2p_a"
    assert rec["ip_addr"] == ""
    assert rec["stratum_port"] == DDef.STRATUM_PORT

    assert p2p_a.instance() == "p2p_a"
    assert p2p_a.ip_addr() == ""
    assert p2p_a.stratum_port() == DDef.STRATUM_PORT
