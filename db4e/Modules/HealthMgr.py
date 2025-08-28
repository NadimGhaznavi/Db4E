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
from copy import deepcopy


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
    INSTANCE_LABEL, IP_ADDR_LABEL, MONEROD_LABEL, IN_PEERS_LABEL, OUT_PEERS_LABEL,
    P2P_BIND_PORT_LABEL, STRATUM_PORT_LABEL, LOG_LEVEL_LABEL, PARENT_LABEL)

class HealthMgr:

    def check(self, elem):
        elem.pop_msgs()
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
        if db4e.vendor_dir() == "":
            db4e.msg(f"{VENDOR_DIR_LABEL}", ERROR_FIELD, f"Missing {VENDOR_DIR_LABEL}")
        
        elif os.path.isdir(db4e.vendor_dir()):
            db4e.msg(f"{VENDOR_DIR_LABEL}", GOOD_FIELD, f"Found: {db4e.vendor_dir()}")

        else:
            db4e.msg(f"{VENDOR_DIR_LABEL}", ERROR_FIELD, 
                     f"Deployment directory not found: {db4e.vendor_dir()}")

        if db4e.user_wallet():
            db4e.msg(f"{USER_WALLET_LABEL}", GOOD_FIELD, 
                     f"Found: {db4e.user_wallet()[:11]}...")
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
        missing_field = False
        if not p2pool.instance():
            p2pool.msg(P2POOL_LABEL, ERROR_FIELD, f"{INSTANCE_LABEL} missing")
            missing_field = True

        if not os.path.exists(p2pool.config_file()):
            p2pool.msg(P2POOL_LABEL, ERROR_FIELD, f"{CONFIG_LABEL} missing")
            missing_field = True

        if not p2pool.in_peers():
            p2pool.msg(P2POOL_LABEL, ERROR_FIELD, f"{IN_PEERS_LABEL} missing")
            missing_field = True

        if not p2pool.out_peers():
            p2pool.msg(P2POOL_LABEL, ERROR_FIELD, f"{OUT_PEERS_LABEL} missing")
            missing_field = True

        if not p2pool.p2p_bind_port():
            p2pool.msg(P2POOL_LABEL, ERROR_FIELD, f"{P2P_BIND_PORT_LABEL} missing")
            missing_field = True

        if not p2pool.stratum_port():
            p2pool.msg(P2POOL_LABEL, ERROR_FIELD, f"{STRATUM_PORT_LABEL} missing")
            missing_field = True

        if not p2pool.log_level():
            p2pool.msg(P2POOL_LABEL, ERROR_FIELD, f"{LOG_LEVEL_LABEL} missing")
            missing_field = True

        if not p2pool.parent():
            p2pool.msg(PARENT_LABEL, ERROR_FIELD, f"Missing upstream Blockchain deployment")
            missing_field = True

        if missing_field:
            return p2pool
        
        if self.is_port_open(p2pool.ip_addr(), p2pool.p2p_bind_port()):
            p2pool.msg(P2POOL_LABEL, GOOD_FIELD,
                       f"Connection to {P2P_BIND_PORT_LABEL} successful")
        else:
            p2pool.msg(P2POOL_LABEL, WARN_FIELD,
                       f"Connection to {P2P_BIND_PORT_LABEL} failed")
            
        if self.is_port_open(p2pool.ip_addr(), p2pool.stratum_port()):
            p2pool.msg(P2POOL_LABEL, GOOD_FIELD,
                       f"Connection to {STRATUM_PORT_LABEL} successful")
        
        if p2pool.enabled():
            p2pool.msg(P2POOL_LABEL, GOOD_FIELD,
                       f"{P2POOL_LABEL} ({p2pool.instance.value}) is enabled")
        else:
            p2pool.msg(P2POOL_LABEL, WARN_FIELD,
                       f"{P2POOL_LABEL} ({p2pool.instance.value}) is disabled")

        # Check upstream MoneroD
        #print(f"HealthMgr:check_p2pool(): type(p2pool.monerod): {type(p2pool.monerod)}")
        if type(p2pool.monerod) == MoneroD or type(p2pool.monerod) == MoneroDRemote:
            self.check(p2pool.monerod)
            if p2pool.monerod.status() == GOOD_FIELD:
                p2pool.msg(MONEROD_LABEL, GOOD_FIELD,
                        f"Upstream MoneroD ({p2pool.monerod.instance.value}) is healthy")
            else:
                p2pool.msg(MONEROD_LABEL, WARN_FIELD,
                        f"Upstream MoneroD ({p2pool.monerod.instance.value}) has issues:")
                p2pool.push_msgs(p2pool.monerod.pop_msgs())
        else:
            p2pool.msg(MONEROD_LABEL, WARN_FIELD,
                      f"Missing upstream Blockchain deployment")            

        #print(f"HealthMgr:check_p2pool(): msgs: {p2pool.pop_msgs()}")
        return p2pool


    def check_p2pool_remote(self, p2pool: P2PoolRemote) -> P2PoolRemote:
        #print(f"HealthMgr:check_p2pool_remote(): rec: {rec}")
        if self.is_port_open(p2pool.ip_addr.value, p2pool.stratum_port.value):
            p2pool.msg(P2POOL_LABEL, GOOD_FIELD,
                       f"Connection to {STRATUM_PORT_LABEL} successful")
        else:
            p2pool.msg(P2POOL_LABEL, WARN_FIELD,
                       f"Connection to {STRATUM_PORT_LABEL} failed")
            
        return p2pool        

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
        if xmrig.enabled():
            xmrig.msg(XMRIG_LABEL, GOOD_FIELD,
                      f"{XMRIG_LABEL} ({xmrig.instance.value}) is enabled")
        else:
            xmrig.msg(XMRIG_LABEL, WARN_FIELD,
                      f"{XMRIG_LABEL} ({xmrig.instance.value}) is disabled")


        # Check the upstream P2Pool
        if type(xmrig.p2pool) == P2Pool or type(xmrig.p2pool) == P2PoolRemote:
            self.check(xmrig.p2pool)
            if xmrig.p2pool.status() == GOOD_FIELD:
                xmrig.msg(P2POOL_LABEL, GOOD_FIELD,
                        f"Upstream P2pool ({xmrig.p2pool.instance()}) is healthy")
            else:
                xmrig.msg(P2POOL_LABEL, WARN_FIELD,
                        f"Upstream P2pool ({xmrig.p2pool.instance()}) has issues:")
                xmrig.push_msgs(xmrig.p2pool.pop_msgs())
        else:
            xmrig.msg(P2POOL_LABEL, WARN_FIELD,
                      f"Missing upstream P2pool deployment")
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