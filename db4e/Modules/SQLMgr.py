"""
db4e/Modules/SQLMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import os, sqlite3
from datetime import datetime

from db4e.Modules.Db4E import Db4E
from db4e.Modules.DeplMgr import DeplMgr
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig
from db4e.Modules.XMRigRemote import XMRigRemote

from db4e.Constants.DDir import DDir
from db4e.Constants.DFile import DFile
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem


class SQLMgr:

    def __init__(self, db_type: str):
        """Constructor"""
        depl_mgr = DeplMgr(db=DbMgr())

        self._db_type = db_type
        self._db_dir = None
        self._conn = None
        self._cursor = None
        self._initialized = False

    def db_dir(self, db_dir=None):
        if db_dir:
            self._db_dir = db_dir
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)

            if self._db_type == DField.SERVER:
                self._db_file = os.path.join(db_dir, DFile.SERVER_DB)
            elif self._db_type == DField.CLIENT:
                self._db_file = os.path.join(db_dir, DFile.CLIENT_DB)
            else:
                raise ValueError(f"Unrecognized db_type: {self._db_type}")

            # Connect to SQLite, get a cursor and initialize the DB
            self._conn = sqlite3.connect(self._db_file)
            self._conn.execute("PRAGMA foreign_keys = ON;")
            self._cursor = self._conn.cursor()
            self._init_db()
        return self._db_dir

    def insert_one(self, table_name: str, elem):
        """Generic insert method for any model with a __dict__() returning field:value mapping."""
        data = elem.__dict__()  # Your custom dict with DField constants as keys
        now = datetime.now()

        # Add timestamp fields dynamically (if applicable to that table)
        if table_name != DElem.XMRIG_REMOTE:
            data.update(
                {
                    "updated_y": now.year,
                    "updated_mo": now.month,
                    "updated_d": now.day,
                    "updated_h": now.hour,
                    "updated_mi": now.minute,
                    "updated_s": now.second,
                }
            )

        # Stable key order (deterministic SQL generation)
        columns = sorted(data.keys())
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        values = tuple(data[col] for col in columns)

        # Execute insert
        self._cursor.execute(sql, values)
        self._conn.commit()
        return self._cursor.lastrowid

    def update_one(self, table_name: str, elem, record_id: int):
        """Generic update method for any model with a __dict__() returning field:value mapping."""
        data = elem.__dict__()  # Your model’s dict with DField constants as keys
        now = datetime.now()

        if table_name != DElem.XMRIG_REMOTE:
            # Refresh timestamps
            data.update(
                {
                    "updated_y": now.year,
                    "updated_mo": now.month,
                    "updated_d": now.day,
                    "updated_h": now.hour,
                    "updated_mi": now.minute,
                    "updated_s": now.second,
                }
            )

        # Stable ordering for deterministic SQL generation
        columns = sorted(data.keys())

        # Build the SQL SET clause: column1=?, column2=?, ...
        set_clause = ", ".join([f"{col}=?" for col in columns])

        sql = f"UPDATE {table_name} SET {set_clause} WHERE id=?"
        values = tuple(data[col] for col in columns) + (record_id,)

        # Execute update
        self._cursor.execute(sql, values)
        self._conn.commit()

        return self._cursor.rowcount

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
                instance TEXT,
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
