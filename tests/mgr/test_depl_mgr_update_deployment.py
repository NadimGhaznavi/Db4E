# db4e/tests/mgr/test_depl_mgr_update_deployment.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote

from db4e.constants.DElem import DElem
from db4e.constants.DDir import DDir
from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField


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

    db4e.user_wallet("new_user_wallet")
    depl_mgr.update_deployment(db4e)

    rows = sql_db.execute_query("SELECT * from db4e")
    assert len(rows) == 1
    assert rows[0]["instance"] == DElem.DB4E
    assert rows[0]["user_wallet"] == "new_user_wallet"
    assert rows[0]["vendor_dir"] == vendor_dir

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

    db4e.primary_server(mon_a.id())
    db4e.primary_remote(0)
    depl_mgr.update_deployment(db4e)

    rows = sql_db.execute_query("SELECT * from db4e")
    assert len(rows) == 1
    row = rows[0]
    assert row["primary_server"] == mon_a.id()
    assert row["primary_remote"] == 0

    db4e.primary_server(DField.DISABLE)
    db4e.primary_remote(DField.DISABLE)
    depl_mgr.update_deployment(db4e)

    rows = sql_db.execute_query("SELECT * from db4e")
    assert len(rows) == 1
    row = rows[0]
    assert row["primary_server"] == DField.DISABLE
    assert row["primary_remote"] == DField.DISABLE
