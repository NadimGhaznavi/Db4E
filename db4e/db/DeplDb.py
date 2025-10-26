"""
db4e/db/DeplDb.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

# Supporting modules
from datetime import datetime

# Base deomain database module
from db4e.db.BaseDb import BaseDb


# Deployment elements
from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig
from db4e.recs.monero.XMRigRemote import XMRigRemote

# The module that interfaces with SQLite3
from db4e.db.SQLDb import SQLDb

# Db4E logging module
from db4e.util.Db4ELogger import Db4ELogger

# Constants
from db4e.constants.DSQL import DCol, ELEM_TABLE_LIST, ELEM_TABLE_MAP
from db4e.constants.DElem import DElem
from db4e.constants.DModule import DModule


class DeplDb(BaseDb):

    def __init__(self, sql_db: SQLDb, log_file=None):
        self.sql_db = sql_db
        if log_file:
            self.log = Db4ELogger(db4e_module=DModule.DEPLOYMENT_DB, log_file=log_file)
        self._init_db()

    def factory(self, elem_type, rec):
        if elem_type == DElem.DB4E:
            return Db4E(rec=rec)
        elif elem_type == DElem.MONEROD:
            return MoneroD(rec=rec)
        elif elem_type == DElem.MONEROD_REMOTE:
            return MoneroDRemote(rec=rec)
        elif elem_type == DElem.P2POOL:
            return P2Pool(rec=rec)
        elif elem_type == DElem.P2POOL_REMOTE:
            return P2PoolRemote(rec=rec)
        elif elem_type == DElem.INT_P2POOL:
            return P2PoolInternal(rec=rec)
        elif elem_type == DElem.XMRIG:
            return XMRig(rec=rec)
        elif elem_type == DElem.XMRIG_REMOTE:
            return XMRigRemote(rec=rec)
        else:
            raise ValueError(f"DeplMgr:factory(): No handler for {elem_type}")

    def get_deployments(self):
        object_list = []
        for table in ELEM_TABLE_LIST:
            for rec in self.sql_db.find_many(table=table):
                object_list.append(self.factory(rec))
        return object_list

    def get_deployment_by_id(self, elem_type: str, instance: str):
        table = ELEM_TABLE_MAP[elem_type]
        rec = self.sql_db.execute_query(
            f"SELECT * FROM {table} WHERE instance=?", (instance,)
        )[0]
        return self.factory(rec)

    def _init_db(self):
        self.sql_db.executescript(
            """
            CREATE TABLE IF NOT EXISTS db4e (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                donation_wallet TEXT,
                db4e_group TEXT,
                db4e_user TEXT,
                enabled INTEGER,
                install_dir TEXT,
                instance TEXT,
                primary_server INTEGER,
                user_wallet TEXT,
                vendor_dir TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER );

            CREATE TABLE IF NOT EXISTS monerod (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                any_ip TEXT,
                blockchain_dir TEXT,
                config_file TEXT,
                enabled INTEGER,
                in_peers INTEGER,
                instance TEXT,
                ip_addr TEXT,
                log_file TEXT,
                log_level INTEGER,
                max_log_files INTEGER,
                max_log_size INTEGER,
                out_peers INTEGER,
                p2p_bind_port INTEGER,
                priority_node_1 TEXT,
                priority_node_2 TEXT,
                priority_port_1 INTEGER,
                priority_port_2 INTEGER,
                rpc_bind_port INTEGER,
                show_time_stats INTEGER,
                stdin_path TEXT,
                version TEXT,
                zmq_pub_port INTEGER,
                zmq_rpc_port INTEGER,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS monerod_remote (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instance TEXT,
                ip_addr TEXT,
                rpc_bind_port INTEGER,
                zmq_pub_port INTEGER,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS p2pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                any_ip TEXT,
                chain TEXT,
                config_file TEXT,
                enabled INTEGER,
                in_peers INTEGER,
                instance TEXT,
                ip_addr TEXT,
                log_file TEXT,
                logrotate_config TEXT,
                max_log_files INTEGER,
                max_log_size INTEGER,
                log_level INTEGER,
                out_peers INTEGER,
                p2p_port INTEGER,
                parent INTEGER,
                stdin_path TEXT,
                stratum_port INTEGER,
                user_wallet TEXT,
                version TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS p2pool_internal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                any_ip TEXT,
                chain TEXT,
                config_file TEXT,
                enabled INTEGER,
                in_peers INTEGER,
                instance TEXT,
                ip_addr TEXT,
                log_file TEXT,
                logrotate_config TEXT,
                max_log_files INTEGER,
                max_log_size INTEGER,
                log_level INTEGER,
                out_peers INTEGER,
                p2p_port INTEGER,
                parent INTEGER,
                stdin_path TEXT,
                stratum_port INTEGER,
                user_wallet TEXT,
                version TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS p2pool_remote (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instance TEXT,
                ip_addr TEXT,
                stratum_port INTEGER,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS xmrig (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_file TEXT,
                enabled INTEGER,
                instance TEXT,
                log_file TEXT,
                logrotate_config TEXT,
                max_log_files INTEGER,
                max_log_size INTEGER,
                num_threads INTEGER,
                parent INTEGER,
                version TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS xmrig_remote (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instance TEXT,
                ip_addr TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER,
            );
            """
        )
