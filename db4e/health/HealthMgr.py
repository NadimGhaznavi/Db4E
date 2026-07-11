# db4e/mgr/HealthMgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

import os
import socket

# Logging DB
from db4e.util.Db4ELogger import Db4ELogger

# SystemD access
from db4e.util.Db4ESystemD import Db4ESystemD

# Ops DB - Service status
from db4e.db.OpsDb import OpsDb

# Health DB
from db4e.db.HealthDb import HealthDb
from db4e.db.DeplDb import DeplDb
from db4e.util.Helper import HealthMsg, is_port_open, get_upstream

# Deployment elements
from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig
from db4e.recs.monero.XMRigRemote import XMRigRemote

# Constants
from db4e.constants.DModule import DModule as MODULE
from db4e.constants.DElem import DElem as ELEM
from db4e.constants.DStatus import DStatus as STATUS
from db4e.constants.DHealth import DCategory as CATEGORY
from db4e.constants.DField import DField as FIELD
from db4e.constants.DLabel import DLabel as LABEL
from db4e.constants.DSystemD import DSystemD as SYSTEMD


class HealthMgr:
    """
    Health manager that periodically checks the health of deployed components.
    """

    def __init__(
        self, health_db: HealthDb, depl_db: DeplDb, ops_db: OpsDb, log_file=None
    ):
        self.health_db = health_db
        self.depl_db = depl_db
        self.ops_db = ops_db
        self.systemd = Db4ESystemD(ops_db=ops_db)
        self.log = Db4ELogger(db4e_module=MODULE.HEALTH_MGR, log_file=log_file)

    def check(self, elem):
        """
        Perform health checks on deployed elements.
        """
        if type(elem) == Db4E:
            self.check_db4e(elem)
        elif type(elem) == MoneroD:
            self.check_monerod(elem)
        elif type(elem) == MoneroDRemote:
            self.check_monerod_remote(elem)
        elif type(elem) == P2Pool:
            self.check_p2pool(elem)
        elif type(elem) == P2PoolRemote:
            self.check_p2pool_remote(elem)
        elif type(elem) == P2PoolInternal:
            self.check_p2pool_internal(elem)
        elif type(elem) == XMRig:
            self.check_xmrig(elem)

    def check_db4e(self, db4e: Db4E):
        # Check that the deployment directory exists
        if os.path.isdir(db4e.vendor_dir()):
            health_msg = HealthMsg(
                instance=LABEL.DB4E,
                elem_type=ELEM.DB4E,
                category=CATEGORY.VENDOR_DIR,
                status=STATUS.GOOD,
                message=f"Found directory {db4e.vendor_dir()}",
            )
        else:
            health_msg = HealthMsg(
                instance=ELEM.DB4E,
                elem_type=ELEM.DB4E,
                category=CATEGORY.VENDOR_DIR,
                status=STATUS.ERROR,
                message=f"Directory {db4e.vendor_dir()} not found",
            )
        self.health_db.upsert_one(health_msg)

        # Check if a primary server has been set
        if db4e.primary_server() == FIELD.DISABLE:
            health_msg = HealthMsg(
                instance=LABEL.DB4E,
                elem_type=ELEM.DB4E,
                category=CATEGORY.PRIMARY_SERVER,
                status=STATUS.WARN,
                message="Primary server is unset",
            )
        else:
            monerod = get_upstream(
                depl_db=self.depl_db,
                upstream_type=ELEM.MONEROD,
                remote=db4e.primary_remote(),
                id=db4e.primary_server(),
            )
            health_msg = HealthMsg(
                instance=LABEL.DB4E,
                elem_type=ELEM.DB4E,
                category=CATEGORY.PRIMARY_SERVER,
                status=STATUS.GOOD,
                message=f"Primary server set: {monerod.instance()}",
            )
        self.health_db.upsert_one(health_msg)

    def check_monerod(self, monerod: MoneroD):
        ip_addr = monerod.ip_addr()

        # Is the RPC Port open
        port = monerod.rpc_bind_port()
        if is_port_open(ip_addr, port):
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=ELEM.MONEROD,
                category=CATEGORY.RPC_BIND_PORT,
                status=STATUS.GOOD,
                message=f"Connected to [b]{ip_addr}:{port}[/]",
            )
        else:
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=ELEM.MONEROD,
                category=CATEGORY.RPC_BIND_PORT,
                status=STATUS.ERROR,
                message=f"Failed to connect to [b]{ip_addr}:{port}[/]",
            )
        self.health_db.upsert_one(health_msg)

        # Is ZMQ PUB port open
        port = monerod.zmq_pub_port()
        if is_port_open(ip_addr, port):
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=ELEM.MONEROD,
                category=CATEGORY.ZMQ_PUB_PORT,
                status=STATUS.GOOD,
                message=f"Connected to [b]{ip_addr}:{port}[/]",
            )
        else:
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=ELEM.MONEROD,
                category=CATEGORY.ZMQ_PUB_PORT,
                status=STATUS.ERROR,
                message=f"Failed to connect to [b]{ip_addr}:{port}[/]",
            )
        self.health_db.upsert_one(health_msg)

        # Check that the blockchain directory is there
        blockchain_dir = monerod.blockchain_dir()
        if os.path.exists(blockchain_dir):
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=ELEM.MONEROD,
                category=CATEGORY.BLOCKCHAIN_DIR,
                status=STATUS.GOOD,
                message=f"Found Directory: {monerod.blockchain_dir()}",
            )
        else:
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=ELEM.MONEROD,
                category=CATEGORY.BLOCKCHAIN_DIR,
                status=STATUS.ERROR,
                message=f"Directory Missing: {monerod.blockchain_dir()}",
            )
        self.health_db.upsert_one(health_msg)

    def check_p2pool(self, p2pool: P2Pool):
        ip_addr = p2pool.ip_addr()
        port = p2pool.stratum_port()

        # Is the instance enabled
        if p2pool.enabled():
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL,
                category=CATEGORY.ENABLED,
                status=STATUS.GOOD,
                message=f"Instance is enabled",
            )
        else:
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL,
                category=CATEGORY.ENABLED,
                status=STATUS.ERROR,
                message=f"Instance is disabled",
            )
        self.health_db.upsert_one(health_msg)

        # Is stratum port open
        if is_port_open(ip_addr, port):
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL,
                category=CATEGORY.STRATUM_PORT,
                status=STATUS.GOOD,
                message=f"Connected to [b]{ip_addr}:{port}[/]",
            )
        else:
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL,
                category=CATEGORY.STRATUM_PORT,
                status=STATUS.ERROR,
                message=f"Failed to connect to [b]{ip_addr}:{port}[/]",
            )
        self.health_db.upsert_one(health_msg)        

        # Check that there the upstream monerod is defined
        if p2pool.parent() == FIELD.DISABLE:
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL,
                category=CATEGORY.UPSTREAM,
                status=STATUS.ERROR,
                message=f"Upstream Monero is undefined",
            )
        else:
            monerod = get_upstream(
                depl_db=self.depl_db,
                upstream_type=ELEM.MONEROD,
                remote=p2pool.parent_remote(),
                id=p2pool.parent(),
            )
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL,
                category=CATEGORY.UPSTREAM,
                status=STATUS.GOOD,
                message=f"Upstream Monero is defined: {monerod.instance()}",
            )
        self.health_db.upsert_one(health_msg)

        # Check if p2pool is running
        sd = self.systemd
        instance = p2pool.instance()
        sd.service_name(
            service_name="p2pool@" + instance,
            service_type=SYSTEMD.SERVICE_SUFFIX
        )
        if sd.running():
            health_msg = HealthMsg(
                instance=instance,
                elem_type=ELEM.P2POOL,
                category=CATEGORY.RUNNING,
                status=STATUS.GOOD,
                message="Instance is running"
            )
        else:
            health_msg = HealthMsg(
                instance=instance,
                elem_type=ELEM.P2POOL,
                category=CATEGORY.RUNNING,
                status=STATUS.ERROR,
                message="Instance is stopped"
            )
        self.health_db.upsert_one(health_msg)

    def check_monerod_remote(self, monerod: MoneroDRemote):
        ip_addr = monerod.ip_addr()

        # Is RPC BIND port open
        port = monerod.rpc_bind_port()
        if is_port_open(ip_addr, port):
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=ELEM.MONEROD_REMOTE,
                category=CATEGORY.RPC_BIND_PORT,
                status=STATUS.GOOD,
                message=f"Connected to [b]{ip_addr}:{port}[/]",
            )
        else:
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=ELEM.MONEROD_REMOTE,
                category=CATEGORY.RPC_BIND_PORT,
                status=STATUS.ERROR,
                message=f"Failed to connect to [b]{ip_addr}:{port}[/]",
            )
        self.health_db.upsert_one(health_msg)

        # Is ZMQ PUB port open
        port = monerod.zmq_pub_port()
        if is_port_open(ip_addr, port):
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=ELEM.MONEROD_REMOTE,
                category=CATEGORY.ZMQ_PUB_PORT,
                status=STATUS.GOOD,
                message=f"Connected to [b]{ip_addr}:{port}[/]",
            )
        else:
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=ELEM.MONEROD_REMOTE,
                category=CATEGORY.ZMQ_PUB_PORT,
                status=STATUS.ERROR,
                message=f"Failed to connect to [b]{ip_addr}:{port}[/]",
            )
        self.health_db.upsert_one(health_msg)

    def check_p2pool_internal(self, p2pool: P2PoolInternal):
        ip_addr = p2pool.ip_addr()
        port = p2pool.stratum_port()

        # Is the instance enabled
        if p2pool.enabled():
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL_INTERNAL,
                category=CATEGORY.ENABLED,
                status=STATUS.GOOD,
                message=f"Instance is enabled",
            )
        else:
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL_INTERNAL,
                category=CATEGORY.ENABLED,
                status=STATUS.ERROR,
                message=f"Instance is disabled",
            )
        self.health_db.upsert_one(health_msg)

        # Is stratum port open
        if is_port_open(ip_addr, port):
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL_INTERNAL,
                category=CATEGORY.STRATUM_PORT,
                status=STATUS.GOOD,
                message=f"Connected to [b]{ip_addr}:{port}[/]",
            )
        else:
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL_INTERNAL,
                category=CATEGORY.STRATUM_PORT,
                status=STATUS.ERROR,
                message=f"Failed to connect to [b]{ip_addr}:{port}[/]",
            )
        self.health_db.upsert_one(health_msg)

        # Check that there the upstream monerod is defined
        if p2pool.parent() == FIELD.DISABLE:
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL_INTERNAL,
                category=CATEGORY.UPSTREAM,
                status=STATUS.ERROR,
                message=f"Upstream Monero is undefined",
            )
        else:
            monerod = get_upstream(
                depl_db=self.depl_db,
                upstream_type=ELEM.MONEROD,
                remote=p2pool.parent_remote(),
                id=p2pool.parent(),
            )
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL_INTERNAL,
                category=CATEGORY.UPSTREAM,
                status=STATUS.GOOD,
                message=f"Upstream Monero is defined: {monerod.instance()}",
            )
        self.health_db.upsert_one(health_msg)

        # Check if p2pool is running
        sd = self.systemd
        instance = p2pool.instance()
        sd.service_name(
            service_name="p2pool@" + instance,
            service_type=SYSTEMD.SERVICE_SUFFIX
        )
        if sd.running():
            health_msg = HealthMsg(
                instance=instance,
                elem_type=ELEM.P2POOL_INTERNAL,
                category=CATEGORY.RUNNING,
                status=STATUS.GOOD,
                message="Instance is running"
            )
        else:
            health_msg = HealthMsg(
                instance=instance,
                elem_type=ELEM.P2POOL_INTERNAL,
                category=CATEGORY.RUNNING,
                status=STATUS.ERROR,
                message="Instance is stopped"
            )
        self.health_db.upsert_one(health_msg)



    def check_p2pool_remote(self, p2pool: P2PoolRemote):
        ip_addr = p2pool.ip_addr()
        port = p2pool.stratum_port()

        # Is stratum port open
        if is_port_open(ip_addr, port):
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL_REMOTE,
                category=CATEGORY.STRATUM_PORT,
                status=STATUS.GOOD,
                message=f"Connected to [b]{ip_addr}:{port}[/]",
            )
        else:
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=ELEM.P2POOL_REMOTE,
                category=CATEGORY.STRATUM_PORT,
                status=STATUS.ERROR,
                message=f"Failed to connect to [b]{ip_addr}:{port}[/]",
            )
        self.health_db.upsert_one(health_msg)

    def check_xmrig(self, xmrig: XMRig):
        pass
