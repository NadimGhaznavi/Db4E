# db4e/tests/mgr/test_install_mgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import os
from db4e.mgr.InstallMgr import InstallMgr
from db4e.recs.monero.Db4E import Db4E

from db4e.constants.DDir import DDir
from db4e.constants.DElem import DElem
from db4e.constants.DField import DField
from db4e.constants.DDef import DDef
from db4e.constants.DLabel import DLabel
from db4e.constants.DFile import DFile


def test_deploy_internal_p2pools(
    initialized_depl_db, initialized_sql_db, initialized_bootstrap_mgr
):
    depl_db = initialized_depl_db
    sql_db = initialized_sql_db
    bs_mgr = initialized_bootstrap_mgr

    db4e = Db4E()
    db4e.instance(DElem.DB4E)
    db4e.user_wallet("test_wallet_value")
    db4e.vendor_dir(bs_mgr.get_dir(DDir.VENDOR))
    depl_db.insert_one(db4e)

    install_mgr = InstallMgr(bs_mgr=bs_mgr)
    install_mgr._deploy_internal_p2pools(db4e=db4e)

    rows = sql_db.execute_query("SELECT * from p2pool_internal")
    assert len(rows) == 3

    assert rows[0]["chain"] == DField.MAIN_CHAIN
    assert rows[1]["chain"] == DField.MINI_CHAIN
    assert rows[2]["chain"] == DField.NANO_CHAIN

    assert rows[0]["p2p_port"] == 37989
    assert rows[1]["p2p_port"] == 37990
    assert rows[2]["p2p_port"] == 37991

    assert rows[0]["stratum_port"] == 43333
    assert rows[1]["stratum_port"] == 43334
    assert rows[2]["stratum_port"] == 43335

    assert rows[0]["instance"] == DLabel.MAIN_CHAIN
    assert rows[1]["instance"] == DLabel.MINI_CHAIN
    assert rows[2]["instance"] == DLabel.NANO_CHAIN

    assert rows[0]["parent"] == DField.DISABLE
    assert rows[1]["parent"] == DField.DISABLE
    assert rows[2]["parent"] == DField.DISABLE

    assert rows[0]["parent_remote"] == DField.DISABLE
    assert rows[1]["parent_remote"] == DField.DISABLE
    assert rows[2]["parent_remote"] == DField.DISABLE

    assert rows[0]["user_wallet"] == DDef.DONATION_WALLET
    assert rows[1]["user_wallet"] == DDef.DONATION_WALLET
    assert rows[2]["user_wallet"] == DDef.DONATION_WALLET

    vendor_dir = bs_mgr.get_dir(DDir.VENDOR)

    assert rows[0]["log_file"] == os.path.join(
        vendor_dir, DElem.P2POOL, DLabel.MAIN_CHAIN, DDef.LOG_DIR, DFile.P2POOL_LOG
    )
    assert rows[1]["log_file"] == os.path.join(
        vendor_dir, DElem.P2POOL, DLabel.MINI_CHAIN, DDef.LOG_DIR, DFile.P2POOL_LOG
    )
    assert rows[2]["log_file"] == os.path.join(
        vendor_dir, DElem.P2POOL, DLabel.NANO_CHAIN, DDef.LOG_DIR, DFile.P2POOL_LOG
    )

    assert rows[0]["stdin_path"] == os.path.join(
        vendor_dir, DElem.P2POOL, DLabel.MAIN_CHAIN, DDef.RUN_DIR, DFile.P2POOL_STDIN
    )
    assert rows[1]["stdin_path"] == os.path.join(
        vendor_dir, DElem.P2POOL, DLabel.MINI_CHAIN, DDef.RUN_DIR, DFile.P2POOL_STDIN
    )
    assert rows[2]["stdin_path"] == os.path.join(
        vendor_dir, DElem.P2POOL, DLabel.NANO_CHAIN, DDef.RUN_DIR, DFile.P2POOL_STDIN
    )

    assert rows[0]["config_file"] == os.path.join(
        vendor_dir, DElem.P2POOL, DDef.CONF_DIR, DLabel.MAIN_CHAIN + DField.INI_SUFFIX
    )
    assert rows[1]["config_file"] == os.path.join(
        vendor_dir, DElem.P2POOL, DDef.CONF_DIR, DLabel.MINI_CHAIN + DField.INI_SUFFIX
    )
    assert rows[2]["config_file"] == os.path.join(
        vendor_dir, DElem.P2POOL, DDef.CONF_DIR, DLabel.NANO_CHAIN + DField.INI_SUFFIX
    )

    assert rows[0]["stats_mod"] == os.path.join(
        vendor_dir, DElem.P2POOL, DLabel.MAIN_CHAIN, DDef.API_DIR, DFile.STATS_MOD
    )
    assert rows[1]["stats_mod"] == os.path.join(
        vendor_dir, DElem.P2POOL, DLabel.MINI_CHAIN, DDef.API_DIR, DFile.STATS_MOD
    )
    assert rows[2]["stats_mod"] == os.path.join(
        vendor_dir, DElem.P2POOL, DLabel.NANO_CHAIN, DDef.API_DIR, DFile.STATS_MOD
    )
