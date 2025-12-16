# db4e/tests/mgr/test_depl_mgr_del_deployment.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import os

from db4e.mgr.DeplMgr import DeplMgr
from db4e.recs.monero.MoneroD import MoneroD


def test_del_deployment_monerod(
    initialized_depl_mgr, initialized_bootstrap_mgr, initialized_sql_db
):
    depl_mgr = initialized_depl_mgr
    bs_mgr = initialized_bootstrap_mgr
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
    for row in rows:
        for key in row.keys():
            print(f"{key}: {row[key]}")

    assert 1 == 2
