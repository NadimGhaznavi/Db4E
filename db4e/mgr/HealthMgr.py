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

# Health DB
from db4e.db.HealthDb import HealthDb
from db4e.util.Helper import HealthMsg

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
from db4e.constants.DModule import DModule
from db4e.constants.DElem import DElem
from db4e.constants.DStatus import DStatus
from db4e.constants.DHealth import DCategory
from db4e.constants.DLabel import DLabel


def is_port_open(host, port):
    try:
        infos = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for family, socktype, proto, canonname, sockaddr in infos:
            try:
                with socket.socket(family, socktype, proto) as sock:
                    sock.settimeout(5)
                    sock.connect(sockaddr)  # will raise if connection fails
                    return True
            except (ConnectionRefusedError, TimeoutError, OSError):
                continue
        return False
    except socket.gaierror:
        return False


class HealthMgr:
    """
    Health manager that periodically checks the health of deployed components.
    """

    def __init__(self, health_db: HealthDb, log_file=None):
        self.health_db = health_db
        self.log = Db4ELogger(db4e_module=DModule.HEALTH_MGR, log_file=log_file)

    def check(self, elem):
        """
        Perform health checks on deployed elements.
        """
        if type(elem) == Db4E:
            self.check_db4e(elem)
        elif type(elem) == MoneroDRemote:
            self.check_monerod_remote(elem)
        elif type(elem) == P2PoolRemote:
            self.check_p2pool_remote(elem)

    def check_db4e(self, db4e: Db4E):
        # Check that the deployment directory exists
        if os.path.isdir(db4e.vendor_dir()):
            health_msg = HealthMsg(
                instance=DElem.DB4E,
                elem_type=DElem.DB4E,
                category=DCategory.VENDOR_DIR,
                status=DStatus.GOOD,
                message=f"Found directory {db4e.vendor_dir()}",
            )
        else:
            health_msg = HealthMsg(
                instance=DElem.DB4E,
                elem_type=DElem.DB4E,
                category=DCategory.VENDOR_DIR,
                status=DStatus.ERROR,
                message=f"Directory {db4e.vendor_dir()} not found",
            )
        self.health_db.upsert_one(health_msg)

    def check_monerod_remote(self, monerod: MoneroDRemote):
        ip_addr = monerod.ip_addr()

        # Is RPC BIND port open
        port = monerod.rpc_bind_port()
        if is_port_open(ip_addr, port):
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=DElem.MONEROD_REMOTE,
                category=DCategory.RPC_BIND_PORT,
                status=DStatus.GOOD,
                message=f"Connected to [b]{ip_addr}:{port}[/]",
            )
        else:
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=DElem.MONEROD_REMOTE,
                category=DCategory.RPC_BIND_PORT,
                status=DStatus.ERROR,
                message=f"Failed to connect to [b]{ip_addr}:{port}[/]",
            )
        self.health_db.upsert_one(health_msg)

        # Is ZMQ PUB port open
        port = monerod.zmq_pub_port()
        if is_port_open(ip_addr, port):
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=DElem.MONEROD_REMOTE,
                category=DCategory.ZMQ_PUB_PORT,
                status=DStatus.GOOD,
                message=f"Connected to [b]{ip_addr}:{port}[/]",
            )
        else:
            health_msg = HealthMsg(
                instance=monerod.instance(),
                elem_type=DElem.MONEROD_REMOTE,
                category=DCategory.ZMQ_PUB_PORT,
                status=DStatus.ERROR,
                message=f"Failed to connect to [b]{ip_addr}:{port}[/]",
            )
        self.health_db.upsert_one(health_msg)

    def check_p2pool_remote(self, p2pool: P2PoolRemote):
        ip_addr = p2pool.ip_addr()
        port = p2pool.stratum_port()

        # Is stratum port open
        if is_port_open(ip_addr, port):
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=DElem.P2POOL_REMOTE,
                category=DCategory.STRATUM_PORT,
                status=DStatus.GOOD,
                message=f"Connected to [b]{ip_addr}:{port}[/]",
            )
        else:
            health_msg = HealthMsg(
                instance=p2pool.instance(),
                elem_type=DElem.P2POOL_REMOTE,
                category=DCategory.STRATUM_PORT,
                status=DStatus.ERROR,
                message=f"Failed to connect to [b]{ip_addr}:{port}[/]",
            )
        self.health_db.upsert_one(health_msg)
