# db4e/tests/db/test_depl_db.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.XMRigRemote import XMRigRemote
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.XMRig import XMRig
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
from db4e.db.DeplDb import DeplDb
from db4e.constants.DElem import DElem


def test_init(initialized_sql_db):
    depl_db = DeplDb(sql_db=initialized_sql_db)
    assert depl_db._initialized is True


def test_init(uninitialized_sql_db):
    depl_db = DeplDb(sql_db=uninitialized_sql_db)
    assert depl_db._initialized is False


def test_clear_all(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
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
        """
    )
    pool_a = P2PoolRemote()
    pool_a.instance("TestPoolA")
    pool_b = P2PoolRemote()
    pool_b.instance("TestPoolB")
    depl_db = DeplDb(sql_db=initialized_sql_db)
    depl_db.insert_one(pool_a)
    depl_db.insert_one(pool_b)

    rows = sql_db.find_many("p2pool_remote")
    assert len(rows) == 2

    depl_db.clear_all()
    rows = sql_db.find_many("p2pool_remote")
    assert len(rows) == 0


def test_delete_deployment(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
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
        """
    )
    pool_a = P2PoolRemote()
    pool_a.instance("TestPoolA")
    pool_b = P2PoolRemote()
    pool_b.instance("TestPoolB")
    depl_db = DeplDb(sql_db=initialized_sql_db)
    depl_db.insert_one(pool_a)
    depl_db.insert_one(pool_b)

    rows = sql_db.find_many("p2pool_remote")
    assert len(rows) == 2

    depl_db.delete_deployment(pool_a)

    rows = sql_db.find_many("p2pool_remote")
    assert len(rows) == 1
    assert rows[0][1] == "TestPoolB"


def test_get_deployment(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
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
        """
    )
    pool_a = P2PoolRemote()
    pool_a.instance("TestPoolA")
    pool_b = P2PoolRemote()
    pool_b.instance("TestPoolB")
    pool_c = P2PoolRemote()
    pool_c.instance("TestPoolC")
    depl_db = DeplDb(sql_db=initialized_sql_db)
    depl_db.insert_one(pool_a)
    depl_db.insert_one(pool_b)
    depl_db.insert_one(pool_c)
    obj = depl_db.get_deployment(elem_type=DElem.P2POOL_REMOTE, instance="TestPoolB")
    assert type(obj) == P2PoolRemote
    assert obj.instance() == "TestPoolB"


def test_get_deployments(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
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
            logrotate_config TEXT,
            max_log_files INTEGER,
            max_log_size INTEGER,
            log_level INTEGER,
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
            logrotate_config TEXT,
            max_log_files INTEGER,
            max_log_size INTEGER,
            log_level INTEGER,
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
    pool_a = P2PoolRemote()
    pool_a.instance("TestPoolA")
    pool_b = P2PoolRemote()
    pool_b.instance("TestPoolB")
    pool_c = P2PoolRemote()
    pool_c.instance("TestPoolC")
    mon_a = MoneroDRemote()
    mon_a.instance("TestMonA")
    mon_b = MoneroDRemote()
    mon_b.instance("TestMonB")
    mon_c = MoneroDRemote()
    mon_c.instance("TestMonC")
    xmrig_a = XMRigRemote()
    xmrig_a.instance("TestXMRigA")
    xmrig_b = XMRigRemote()
    xmrig_b.instance("TestXMRigB")
    xmrig_c = XMRigRemote()
    xmrig_c.instance("TestXMRigC")
    depl_db = DeplDb(sql_db=initialized_sql_db)
    depl_db.insert_one(pool_a)
    depl_db.insert_one(pool_b)
    depl_db.insert_one(pool_c)
    depl_db.insert_one(mon_a)
    depl_db.insert_one(mon_b)
    depl_db.insert_one(mon_c)
    depl_db.insert_one(xmrig_a)
    depl_db.insert_one(xmrig_b)
    depl_db.insert_one(xmrig_c)
    rows = depl_db.get_deployments()
    assert len(rows) == 9
    all_instance_names = {
        "TestPoolA",
        "TestPoolB",
        "TestPoolC",
        "TestMonA",
        "TestMonB",
        "TestMonC",
        "TestXMRigA",
        "TestXMRigB",
        "TestXMRigC",
    }
    returned_instances = {obj.instance() for obj in rows}
    assert returned_instances == all_instance_names


def test_get_deployment_by_id(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
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
        """
    )
    pool_a = P2PoolRemote()
    pool_a.instance("TestPoolA")
    pool_b = P2PoolRemote()
    pool_b.instance("TestPoolB")
    pool_c = P2PoolRemote()
    pool_c.instance("TestPoolC")
    depl_db = DeplDb(sql_db=initialized_sql_db)
    pool_a = depl_db.insert_one(pool_a)
    pool_b = depl_db.insert_one(pool_b)
    pool_c = depl_db.insert_one(pool_c)
    obj = depl_db.get_deployment_by_id("p2pool_remote", pool_a.id())
    assert obj.instance() == "TestPoolA"
    obj = depl_db.get_deployment_by_id("p2pool_remote", pool_b.id())
    assert obj.instance() == "TestPoolB"
    obj = depl_db.get_deployment_by_id("p2pool_remote", pool_c.id())
    assert obj.instance() == "TestPoolC"


def test_get_deployments_by_type(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
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
        """
    )
    pool_a = P2PoolRemote()
    pool_a.instance("TestPoolA")
    pool_b = P2PoolRemote()
    pool_b.instance("TestPoolB")
    pool_c = P2PoolRemote()
    pool_c.instance("TestPoolC")
    depl_db = DeplDb(sql_db=initialized_sql_db)
    pool_a = depl_db.insert_one(pool_a)
    pool_b = depl_db.insert_one(pool_b)
    pool_c = depl_db.insert_one(pool_c)

    depl_db = DeplDb(sql_db=initialized_sql_db)
    rows = depl_db.get_deployments_by_type_str("p2pool_remote")
    assert len(rows) == 3
    all_instance_names = {"TestPoolA", "TestPoolB", "TestPoolC"}
    returned_instances = {obj.instance() for obj in rows}
    assert returned_instances == all_instance_names

    rows = depl_db.get_p2pool_remotes()
    assert len(rows) == 3
    all_instance_names = {"TestPoolA", "TestPoolB", "TestPoolC"}
    returned_instances = {obj.instance() for obj in rows}
    assert returned_instances == all_instance_names


def test_get_deployment_ids_and_instances(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
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
        """
    )
    pool_a = P2PoolRemote()
    pool_a.instance("TestPoolA")
    pool_b = P2PoolRemote()
    pool_b.instance("TestPoolB")
    pool_c = P2PoolRemote()
    pool_c.instance("TestPoolC")
    depl_db = DeplDb(sql_db=initialized_sql_db)
    depl_db.insert_one(pool_a)
    depl_db.insert_one(pool_b)
    depl_db.insert_one(pool_c)
    map = depl_db.get_deployment_ids_and_instances("p2pool_remote")
    assert map["TestPoolA"] == (1, 1)
    assert map["TestPoolB"] == (2, 1)
    assert map["TestPoolC"] == (3, 1)

    mon_a = MoneroD()
    mon_a.instance("TestMonA")
    mon_b = MoneroD()
    mon_b.instance("TestMonB")
    mon_c = MoneroD()
    mon_c.instance("TestMonC")
    depl_db.insert_one(mon_a)
    depl_db.insert_one(mon_b)
    depl_db.insert_one(mon_c)
    map = depl_db.get_deployment_ids_and_instances("monerod")
    assert map["TestMonA"] == (1, 0)
    assert map["TestMonB"] == (2, 0)
    assert map["TestMonC"] == (3, 0)


def test_get_downstream(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db = initialized_sql_db
    sql_db.executescript(
        """
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
        """
    )
    mon_a = MoneroD()
    mon_a.instance("TestMonA")
    mon_b = MoneroD()
    mon_b.instance("TestMonB")
    mon_c = MoneroD()
    mon_c.instance("TestMonC")
    p2pool_d = P2Pool()
    p2pool_d.instance("TestPoolD")
    p2pool_e = P2Pool()
    p2pool_e.instance("TestPoolE")
    p2pool_f = P2Pool()
    p2pool_f.instance("TestPoolF")
    depl_db = DeplDb(sql_db=initialized_sql_db)
    mon_a = depl_db.insert_one(mon_a)
    mon_b = depl_db.insert_one(mon_b)
    mon_c = depl_db.insert_one(mon_c)
    p2pool_e.parent(mon_b.id())
    p2pool_e.parent_remote(0)
    depl_db.insert_one(p2pool_d)
    depl_db.insert_one(p2pool_e)
    depl_db.insert_one(p2pool_f)
    rows = depl_db.get_downstream(mon_b)
    assert len(rows) == 1
    assert rows[0].instance() == "TestPoolE"


def test_get_new(initialized_sql_db):
    sql_db = initialized_sql_db
    sql_db.executescript(
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
            primary_remote INTEGER,
            user_wallet TEXT,
            vendor_dir TEXT,
            updated_y INTEGER,
            updated_mo INTEGER,
            updated_d INTEGER,
            updated_h INTEGER,
            updated_mi INTEGER,
            updated_s INTEGER);
        """
    )
    db4e = Db4E()
    depl_db = DeplDb(sql_db=initialized_sql_db)
    depl_db.insert_one(db4e)
    depl_db = DeplDb(sql_db=initialized_sql_db)
    mon_a = depl_db.get_new(DElem.MONEROD)
    assert type(mon_a) == MoneroD
    mon_b = depl_db.get_new(DElem.MONEROD_REMOTE)
    assert type(mon_b) == MoneroDRemote
    p2pool_a = depl_db.get_new(DElem.P2POOL)
    assert type(p2pool_a) == P2Pool
    p2pool_b = depl_db.get_new(DElem.P2POOL_REMOTE)
    assert type(p2pool_b) == P2PoolRemote
    p2pool_c = depl_db.get_new(DElem.P2POOL_INTERNAL)
    assert type(p2pool_c) == P2PoolInternal
    xmrig_a = depl_db.get_new(DElem.XMRIG)
    assert type(xmrig_a) == XMRig
    xmrig_b = depl_db.get_new(DElem.XMRIG_REMOTE)
    assert type(xmrig_b) == XMRigRemote
