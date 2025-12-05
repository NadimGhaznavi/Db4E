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
