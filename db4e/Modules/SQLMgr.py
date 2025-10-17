"""
db4e/Modules/SQLMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import os, sqlite3

from db4e.Modules.DeplMgr import DeplMgr
from db4e.Modules.DbMgr import DbMgr

from db4e.Constants.DDir import DDir
from db4e.Constants.DFile import DFile


class SQLMgr:

    def __init__(self):
        """Constructor"""
        depl_mgr = DeplMgr(db=DbMgr())

        db_dir = depl_mgr.get_dir(DDir.DB)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        self._db_file = os.path.join(db_dir, DFile.SERVER_DB)

        # Connect to SQLite, get a cursor and initialize the DB
        self._conn = sqlite3.connect(self._db_file)
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._cursor = self._conn.cursor()
        self._init_db()

    def _init_db(self):
        """Initialize the DB"""

        # Create the tables if they don't already exist.
        self._cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS db4e (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db4e_group TEXT,
                db4e_user TEXT,
                donation_wallet TEXT,
                install_dir TEXT,
                instance TEXT,
                primary_server INTEGER,
                user_wallet TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER );

            CREATE TABLE IF NOT EXISTS monerod (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blockchain_dir TEXT,
                config_file TEXT,
                enabled INTEGER,
                in_peers INTEGER,
                instance TEXT,
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
                rpc_bind_port INTEGER,
                ip_addr TEXT,
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
                log_rotate_config TEXT,
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
                enabled INTEGER,
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
                log_rotate_config TEXT,
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
                ip_addr TEXT,
                hashrate REAL,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER,
                uptime TEXT,
                utc_y INTEGER,
                utc_mo INTEGER,
                utc_d INTEGER,
                utc_h INTEGER,
                utc_mi INTEGER,
                utc_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS start_stop (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                element TEXT,
                instance TEXT,
                event TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS current_uptime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                element TEXT,
                instance TEXT,
                start_time INTEGER,
                stop_time INTEGER,
                current_secs INTEGER,
                current INTEGER
            );

            CREATE TABLE IF NOT EXISTS block_found_event (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS chain_hashrate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain TEXT,
                hashrate REAL,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS chain_miners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain TEXT,
                miners INTEGER,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS miner_hashrate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner TEXT,
                chain TEXT,
                pool TEXT,
                hashrate REAL,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS pool_hashrate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain TEXT,
                pool TEXT,
                hashrate REAL,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS share_found_event (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner TEXT,
                chain TEXT,
                pool TEXT,
                ip_addr TEXT,
                effort REAL,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS share_position (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner TEXT,
                chain TEXT,
                pool TEXT,
                share_position INTEGER,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );

            CREATE TABLE IF NOT EXISTS share_position (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                miner TEXT,
                chain TEXT,
                pool TEXT,
                share_position INTEGER,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER
            );
            """
        )
        self._conn.commit()
