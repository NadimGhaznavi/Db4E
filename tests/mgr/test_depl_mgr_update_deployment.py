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
from db4e.recs.monero.P2PoolInternal import P2PoolInternal

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
