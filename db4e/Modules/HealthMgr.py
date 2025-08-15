"""
db4e/Modules/HealthMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import os
import socket

from db4e.Modules.Db4E import Db4E
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig

from db4e.Constants.Fields import(ERROR_FIELD, GOOD_FIELD, WARN_FIELD)
from db4e.Constants.Labels import(
    CONFIG_LABEL, P2POOL_LABEL, RPC_BIND_PORT_LABEL, STRATUM_PORT_LABEL, 
    ZMQ_PUB_PORT_LABEL, VENDOR_DIR_LABEL, USER_WALLET_LABEL, XMRIG_LABEL,
    INSTANCE_LABEL, IP_ADDR_LABEL)

class HealthMgr:

    def check(self, elem):

        if type(elem) == Db4E:
            return self.check_db4e(elem)
        elif type(elem) == MoneroD:
            return self.check_monerod(elem)
        elif type(elem) == MoneroDRemote:
            return self.check_monerod_remote(elem)
        elif type(elem) == P2Pool:
            return self.check_p2pool(elem)
        elif type(elem) == P2PoolRemote:
            return self.check_p2pool_remote(elem)
        elif type(elem) == XMRig:
            return self.check_xmrig(elem)
        else:
            raise ValueError(f"HealthMgr:check(): No handler for {elem}")

    def check_db4e(self, db4e: Db4E) -> Db4E:
        #print(f"HealthMgr:check_db4e(): rec: {rec}")
        db4e.pop_msgs()
        if db4e.vendor_dir.value == "":
            db4e.msg(f"{VENDOR_DIR_LABEL}", ERROR_FIELD, f"Missing {VENDOR_DIR_LABEL}")
        
        elif os.path.isdir(db4e.vendor_dir.value):
            db4e.msg(f"{VENDOR_DIR_LABEL}", GOOD_FIELD, f"Found: {db4e.vendor_dir.value}")

        else:
            db4e.msg(f"{VENDOR_DIR_LABEL}", ERROR_FIELD, 
                     f"Deployment directory not found: {db4e.vendor_dir.value}")

        if db4e.user_wallet.value:
            db4e.msg(f"{USER_WALLET_LABEL}", GOOD_FIELD, 
                     f"Found: {db4e.user_wallet.value[:11]}...")
        else:
            db4e.msg(f"{USER_WALLET_LABEL}", ERROR_FIELD,
                     f"{USER_WALLET_LABEL} missing")

        return db4e


    def check_monerod(self, monerod: MoneroD) -> MoneroD:
        # TODO
        return monerod

    def check_monerod_remote(self, monerod: MoneroDRemote) -> MoneroDRemote:
        #print(f"HealthMgr:check_monerod_remote(): rec: {rec}")

        missing_field = False
        if not monerod.instance():
            monerod.msg(INSTANCE_LABEL, ERROR_FIELD, f"{INSTANCE_LABEL} missing")
            missing_field = True

        if not monerod.rpc_bind_port():
            monerod.msg(RPC_BIND_PORT_LABEL, ERROR_FIELD, f"{RPC_BIND_PORT_LABEL} missing")
            missing_field = True

        if not monerod.ip_addr():
            monerod.msg(IP_ADDR_LABEL, ERROR_FIELD, f"{IP_ADDR_LABEL} missing")
            missing_field = True

        if not monerod.zmq_pub_port():
            monerod.msg(ZMQ_PUB_PORT_LABEL, ERROR_FIELD, f"{ZMQ_PUB_PORT_LABEL} missing")
            missing_field = True

        if missing_field:
            return monerod

        if self.is_port_open(monerod.ip_addr(), monerod.rpc_bind_port()):
            monerod.msg(RPC_BIND_PORT_LABEL, GOOD_FIELD,
                        f"Connection to {RPC_BIND_PORT_LABEL} successful")
        else:
            monerod.msg(RPC_BIND_PORT_LABEL, WARN_FIELD,
                        f"Connection to {RPC_BIND_PORT_LABEL} failed")

        if self.is_port_open(monerod.ip_addr(), monerod.zmq_pub_port()):
            monerod.msg(ZMQ_PUB_PORT_LABEL, GOOD_FIELD,
                        f"Connection to {ZMQ_PUB_PORT_LABEL} successful")
        else:
            monerod.msg(ZMQ_PUB_PORT_LABEL, WARN_FIELD,
                        f"Connection to {ZMQ_PUB_PORT_LABEL} failed")

        return monerod


    def check_p2pool(self, p2pool: P2Pool) -> P2Pool:
        #print(f"HealthMgr:check_p2pool(): rec: {rec}")
        # TODO
        return p2pool

    def check_p2pool_remote(self, p2pool: P2PoolRemote) -> P2PoolRemote:
        #print(f"HealthMgr:check_p2pool_remote(): rec: {rec}")
        if self.is_port_open(p2pool.ip_addr.value, p2pool.stratum_port.value):
            p2pool.msg(P2POOL_LABEL, GOOD_FIELD,
                       f"Connection to {STRATUM_PORT_LABEL} successful")
        else:
            p2pool.msg(P2POOL_LABEL, WARN_FIELD,
                       f"Connection to {STRATUM_PORT_LABEL} failed")
        return P2PoolRemote        

    def check_xmrig(self, xmrig: XMRig) -> XMRig:
        #print(f"HealthMgr:check_xmrig(): p2pool_rec: {p2pool_rec}")

        # Check that the XMRig configuration file exists
        if os.path.exists(xmrig.config_file.value):
            xmrig.msg(CONFIG_LABEL, GOOD_FIELD, f"Found: {xmrig.config_file.value}")
        elif not xmrig.config_file.value:
            xmrig.msg(CONFIG_LABEL, WARN_FIELD, f"Missing")
        else:
            xmrig.msg(CONFIG_LABEL, WARN_FIELD, f"Not found: {xmrig.config_file.value}")
        
        # Check if the instance is enabled
        if xmrig.enable():
            xmrig.msg(XMRIG_LABEL, GOOD_FIELD,
                      f"{XMRIG_LABEL} ({xmrig.instance.value}) is enabled")
        else:
            xmrig.msg(XMRIG_LABEL, WARN_FIELD,
                      f"{XMRIG_LABEL} ({xmrig.instance.value}) is disabled")


        # Check the upstream P2Pool
        self.check(xmrig.p2pool)
        if xmrig.p2pool.status() == GOOD_FIELD:
            xmrig.msg(P2POOL_LABEL, GOOD_FIELD,
                      f"Upstream P2pool ({xmrig.p2pool.instance.value}) is healthy")
        else:
            xmrig.msg(P2POOL_LABEL, WARN_FIELD,
                      f"Upstream P2pool ({xmrig.p2pool.instance.value}) has issues:")
            xmrig.push_msgs(xmrig.p2pool.pop_msgs())
        
        return xmrig


    def is_port_open(self, ip_addr, port_num):
        #print(f"Helper:is_port_open(): {ip_addr}/{port_num}")
        if not self.is_valid_ip_or_hostname(ip_addr):
            return False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)  # Set aLine timeout for the connection attempt
                result = sock.connect_ex((ip_addr, int(port_num)))
                return result == 0
        except socket.gaierror:
            return False  # Handle cases like invalid hostname


    def is_valid_ip_or_hostname(self, host: str) -> str:
        try:
            socket.getaddrinfo(host, None)  # works for IPv4/IPv6
            return True
        except socket.gaierror:
            return False