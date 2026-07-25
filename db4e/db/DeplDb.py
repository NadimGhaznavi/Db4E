# db4e/db/DeplDb.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

# Base domain DB module
from db4e.db.BaseDb import (
    TABLE_TO_CLASS_MAP,
    CLASS_TO_TABLE_MAP,
    CLASS_STR_TO_TABLE_MAP,
    CLASS_STR_TO_CLASS_MAP,
    DTable,
    BaseDb,
)

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

# Constants
from db4e.constants.DDef import DDef
from db4e.constants.DField import DField

# Db4E logging module
from db4e.util.Db4ELogger import Db4ELogger

# Constants
from db4e.constants.DSQL import DCol, ELEM_TABLE_LIST
from db4e.constants.DElem import DElem


class DeplDb(BaseDb):
    """
    Deployment database access layer.

    Provides CRUD and lookup helpers for deployment records such as
    MoneroD, P2Pool, XMRig, and related remote/internal variants.
    """

    def __init__(self, sql_db: SQLDb, log_file=None):
        """
        Initialize the deployment database manager.

        :param sql_db: Initialized SQL database wrapper.
        :type sql_db: SQLDb
        :param log_file: Optional log file path.
        :type log_file: str or None
        """
        super().__init__(sql_db=sql_db, log_file=log_file)

    def clear_all(self):
        """
        Delete all rows from all deployment tables.
        """
        for table in ELEM_TABLE_LIST:
            self.sql_db.executescript(f"DELETE FROM {table}")

    def delete_deployment(self, elem):
        """
        Delete a deployment record by object instance.

        :param elem: Deployment object to delete.
        :type elem: object
        """
        table = CLASS_TO_TABLE_MAP[type(elem)]
        self.sql_db.execute_query(f"DELETE FROM {table} WHERE id=?", (elem.id(),))

    def disable_deployment(self, elem):
        table = CLASS_TO_TABLE_MAP[type(elem)]
        self.sql_db.execute_query(
            f"UPDATE {table} SET enabled=0 WHERE id=?", [elem.id()]
        )

    def enable_deployment(self, elem):
        table = CLASS_TO_TABLE_MAP[type(elem)]
        self.sql_db.execute_query(
            f"UPDATE {table} SET enabled=1 WHERE id=?", [elem.id()]
        )

    def get_deployment(self, elem_type: str, instance: str):
        """
        Fetch a deployment record by type and instance name.

        :param elem_type: Deployment element type string.
        :type elem_type: str
        :param instance: Instance name.
        :type instance: str
        :return: Deployment object or None.
        :rtype: object or None
        """
        table = CLASS_STR_TO_TABLE_MAP[elem_type]
        rows = self.sql_db.execute_query(
            f"SELECT * FROM {table} WHERE instance=?", (instance,)
        )
        rec = rows[0] if rows else None
        object = None
        if rec:
            object = CLASS_STR_TO_CLASS_MAP[elem_type](rec)

        return object

    def get_deployments(self):
        """
        Return all deployment records across all deployment tables.

        :return: List of deployment objects.
        :rtype: list
        """
        object_list = []
        for table in ELEM_TABLE_LIST:
            for rec in self.sql_db.find_many(table=table):
                new_obj = TABLE_TO_CLASS_MAP[table](rec=rec)
                object_list.append(new_obj)
        return object_list

    def get_deployment_by_id(self, elem_type: str, id: str):
        """
        Fetch a deployment record by type and database ID.

        :param elem_type: Deployment element type string.
        :type elem_type: str
        :param id: Database ID.
        :type id: str
        :return: Deployment object or None.
        :rtype: object or None
        """
        table = CLASS_STR_TO_TABLE_MAP[elem_type]
        rec_list = self.sql_db.execute_query(f"SELECT * FROM {table} WHERE id=?", (id,))
        rec = rec_list[0] if rec_list else None
        object = None
        if rec:
            object = CLASS_STR_TO_CLASS_MAP[elem_type](rec)
            return object
        else:
            return None

    def get_deployments_by_type_str(self, elem_type: str):
        """
        Fetch all deployments for a given element type.

        :param elem_type: Deployment element type string.
        :type elem_type: str
        :return: List of deployment objects.
        :rtype: list
        """
        object_list = []
        table = CLASS_STR_TO_TABLE_MAP[elem_type]

        for rec in self.sql_db.find_many(table=table):
            new_obj = CLASS_STR_TO_CLASS_MAP[elem_type](rec)
            object_list.append(new_obj)

        return object_list

    def get_deployment_ids_and_instances(self, table):
        """
        Build a mapping of instance name to (id, remote_flag) for a table.

        :param table: Table name to query.
        :type table: str
        :return: Mapping of instance name to (id, remote_flag).
        :rtype: dict
        """
        recs = self.sql_db.find_many(table=table)

        # Flag if the upstream element is local or remote
        if table == DTable.MONEROD or table == DTable.P2POOL:
            remote_flag = 0
        elif table == DTable.MONEROD_REMOTE or table == DTable.P2POOL_REMOTE:
            remote_flag = 1

        instance_map = {}
        for rec in recs:
            instance = rec[DCol.INSTANCE]
            instance_map[instance] = (rec[DCol.ID], remote_flag)
        return instance_map

    ## Get deployment types
    def get_monerods(self):
        """
        Return all MoneroD deployments.
        """
        return self.get_deployments_by_type_str(DElem.MONEROD)

    def get_monerod_remotes(self):
        """
        Return all remote MoneroD deployments.
        """
        return self.get_deployments_by_type_str(DElem.MONEROD_REMOTE)

    def get_p2pools(self):
        """
        Return all P2Pool deployments.
        """
        return self.get_deployments_by_type_str(DElem.P2POOL)

    def get_p2pool_remotes(self):
        """
        Return all remote P2Pool deployments.
        """
        return self.get_deployments_by_type_str(DElem.P2POOL_REMOTE)

    def get_p2pool_internals(self):
        """
        Return all internal P2Pool deployments.
        """
        return self.get_deployments_by_type_str(DElem.P2POOL_INTERNAL)

    def get_xmrigs(self):
        """
        Return all XMRig deployments.
        """
        return self.get_deployments_by_type_str(DElem.XMRIG)

    def get_xmrig_remotes(self):
        """
        Return all remote XMRig deployments.
        """
        return self.get_deployments_by_type_str(DElem.XMRIG_REMOTE)

    def get_downstream(self, elem):
        """
        Return downstream deployments for a given element.

        :param elem: Upstream deployment object.
        :type elem: object
        :return: List of downstream deployment objects.
        :rtype: list
        """
        elem_class = type(elem)
        parent_id = elem.id()
        obj_list = []
        # P2Pool is downstream from MoneroD and MoneroDRemote
        if elem_class == MoneroD:
            p2pools = self.get_p2pools()
            for p2pool in p2pools:
                if p2pool.parent() == parent_id and p2pool.parent_remote() == 0:
                    obj_list.append(p2pool)
        elif elem_class == MoneroDRemote:
            p2pools = self.get_p2pool_remotes()
            for p2pool in p2pools:
                if p2pool.parent() == parent_id and p2pool.parent_remote() == 1:
                    obj_list.append(p2pool)
        # XMRig is downstream from P2Pool and P2PoolRemote
        elif elem_class == P2Pool:
            xmrigs = self.get_xmrigs()
            for xmrig in xmrigs:
                if xmrig.parent() == parent_id and xmrig.parent_remote() == 0:
                    obj_list.append(xmrig)
        elif elem_class == P2PoolRemote:
            xmrigs = self.get_xmrig_remotes()
            for xmrig in xmrigs:
                if xmrig.parent() == parent_id and xmrig.parent_remote() == 1:
                    obj_list.append(xmrig)
        else:
            raise ValueError(f"DeplMgr:get_downstream(): No handler for {elem_class}")
        return obj_list

    def get_new(self, elem_type):
        """
        Construct a new deployment object for a given element type.

        :param elem_type: Deployment element type string.
        :type elem_type: str
        :return: Newly constructed deployment object.
        :rtype: object
        """

        if elem_type == DElem.MONEROD:
            return MoneroD()
        elif elem_type == DElem.MONEROD_REMOTE:
            return MoneroDRemote()
        elif elem_type == DElem.P2POOL:
            p2pool = P2Pool()
            db4e = self.get_deployment(DElem.DB4E, DElem.DB4E)
            p2pool.user_wallet(db4e.user_wallet())
            return p2pool
        elif elem_type == DElem.P2POOL_REMOTE:
            return P2PoolRemote()
        elif elem_type == DElem.P2POOL_INTERNAL:
            p2pool = P2PoolInternal()
            p2pool.user_wallet(DDef.DONATION_WALLET)
            return p2pool
        elif elem_type == DElem.XMRIG:
            return XMRig()
        elif elem_type == DElem.XMRIG_REMOTE:
            return XMRigRemote()
        else:
            raise ValueError(f"DeplMgr:get_new(): No handler for {elem_type}")

    def _init_db(self):
        """
        Initialize deployment tables in the SQLite database.
        """
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
                next_http_port INTEGER,
                next_p2p_port INTEGER,
                next_stratum_port INTEGER,
                primary_server INTEGER,
                primary_remote INTEGER,
                user_wallet TEXT,
                vendor_dir TEXT,
                updated_y INTEGER,
                updated_mo INTEGER,
                updated_d INTEGER,
                updated_h INTEGER,
                updated_mi INTEGER,
                updated_s INTEGER 
            );

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
                log_level INTEGER,
                logrotate_config TEXT,
                max_log_files INTEGER,
                max_log_size INTEGER,
                out_peers INTEGER,
                p2p_port INTEGER,
                parent INTEGER,
                parent_remote INTEGER,
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
                log_level INTEGER,
                logrotate_config TEXT,
                max_log_files INTEGER,
                max_log_size INTEGER,
                out_peers INTEGER,
                p2p_port INTEGER,
                parent INTEGER,
                parent_remote INTEGER,
                stats_mod TEXT,
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
                http_port INTEGER,
                instance TEXT,
                log_file TEXT,
                logrotate_config TEXT,
                max_log_files INTEGER,
                max_log_size INTEGER,
                num_threads INTEGER,
                parent INTEGER,
                parent_remote INTEGER,
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
                updated_s INTEGER
            );
            """
        )

        # Add a updated_ts column to the depl tables
        for table in ELEM_TABLE_LIST:
            self.add_updated_ts_column(table)
