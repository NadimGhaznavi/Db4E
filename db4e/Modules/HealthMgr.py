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
from datetime import datetime, timezone

from db4e.Modules.Db4E import Db4E
from db4e.Modules.InternalP2Pool import InternalP2Pool
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig
from db4e.Modules.XMRigRemote import XMRigRemote


from db4e.Constants.DStatus import DStatus
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField

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
        elif type(elem) == InternalP2Pool:
            return self.check_int_p2pool(elem)
        elif type(elem) == XMRig:
            return self.check_xmrig(elem)
        elif type(elem) == XMRigRemote:
            return self.check_xmrig_remote(elem)
        else:
            raise ValueError(f"HealthMgr:check(): No handler for {elem}")

    def check_db4e(self, db4e: Db4E) -> Db4E:
        #print(f"HealthMgr:check_db4e(): rec: {rec}")
        db4e.pop_msgs()
        if db4e.vendor_dir() == "":
            db4e.msg(f"{DLabel.VENDOR_DIR}", DStatus.ERROR, f"Missing {DLabel.VENDOR_DIR}")
        
        elif os.path.isdir(db4e.vendor_dir()):
            db4e.msg(f"{DLabel.VENDOR_DIR}", DStatus.GOOD, f"Found: {db4e.vendor_dir()}")

        else:
            db4e.msg(f"{DLabel.VENDOR_DIR}", DStatus.ERROR, 
                     f"Deployment directory not found: {db4e.vendor_dir()}")

        if db4e.user_wallet():
            db4e.msg(f"{DLabel.USER_WALLET}", DStatus.GOOD, 
                     f"Found: {db4e.user_wallet()[:11]}...")
        else:
            db4e.msg(f"{DLabel.USER_WALLET}", DStatus.ERROR,
                     f"{DLabel.USER_WALLET} missing")

        return db4e


    def check_monerod(self, monerod: MoneroD) -> MoneroD:
        missing_field = False
        if not monerod.instance():
            monerod.msg(DLabel.INSTANCE, DStatus.ERROR, f"{DLabel.INSTANCE} missing")
            missing_field = True

        if not monerod.in_peers():
            monerod.msg(DLabel.IN_PEERS, DStatus.ERROR, f"{DLabel.IN_PEERS} missing")
            missing_field = True

        if not monerod.out_peers():
            monerod.msg(DLabel.OUT_PEERS, DStatus.ERROR, f"{DLabel.OUT_PEERS} missing")
            missing_field = True

        if not monerod.p2p_bind_port():
            monerod.msg(DLabel.P2P_BIND_PORT, DStatus.ERROR, f"{DLabel.P2P_BIND_PORT} missing")
            missing_field = True

        if not monerod.rpc_bind_port():
            monerod.msg(DLabel.RPC_BIND_PORT, DStatus.ERROR, f"{DLabel.RPC_BIND_PORT} missing")
            missing_field = True

        if not monerod.zmq_pub_port():
            monerod.msg(DLabel.ZMQ_PUB_PORT, DStatus.ERROR, f"{DLabel.ZMQ_PUB_PORT} missing")
            missing_field = True

        if not monerod.zmq_rpc_port():
            monerod.msg(DLabel.ZMQ_RPC_PORT, DStatus.ERROR, f"{DLabel.ZMQ_RPC_PORT} missing")
            missing_field = True

        if not monerod.log_level():
            monerod.msg(DLabel.LOG_LEVEL, DStatus.ERROR, f"{DLabel.LOG_LEVEL} missing")
            missing_field = True

        if not monerod.max_log_files():
            monerod.msg(DLabel.MAX_LOG_FILES, DStatus.ERROR, f"{DLabel.MAX_LOG_FILES} missing")
            missing_field = True

        if not monerod.max_log_size():
            monerod.msg(DLabel.MAX_LOG_SIZE, DStatus.ERROR, f"{DLabel.MAX_LOG_SIZE} missing")
            missing_field = True

        if not monerod.priority_node_1():
            monerod.msg(DLabel.PRIORITY_NODE_1, DStatus.ERROR, f"{DLabel.PRIORITY_NODE_1} missing")
            missing_field = True

        if not monerod.priority_port_1():
            monerod.msg(DLabel.PRIORITY_PORT_1, DStatus.ERROR, f"{DLabel.PRIORITY_PORT_1} missing")
            missing_field = True

        if not monerod.priority_node_2():
            monerod.msg(DLabel.PRIORITY_NODE_2, DStatus.ERROR, f"{DLabel.PRIORITY_NODE_2} missing")
            missing_field = True

        if not monerod.priority_port_2():
            monerod.msg(DLabel.PRIORITY_PORT_2, DStatus.ERROR, f"{DLabel.PRIORITY_PORT_2} missing")
            missing_field = True

        if missing_field:
            return monerod

        if monerod.enabled():
            monerod.msg(DLabel.MONEROD, DStatus.GOOD,
                        f"{DLabel.MONEROD} ({monerod.instance()}) is enabled")
        else:
            monerod.msg(DLabel.MONEROD, DStatus.ERROR,
                        f"{DLabel.MONEROD} ({monerod.instance()}) is disabled")

        if self.is_port_open(monerod.ip_addr(), monerod.rpc_bind_port()):
            monerod.msg(DLabel.RPC_BIND_PORT, DStatus.GOOD,
                        f"Connection to {DLabel.RPC_BIND_PORT} successful")
        else:
            monerod.msg(DLabel.RPC_BIND_PORT, DStatus.WARN,
                        f"Connection to {DLabel.RPC_BIND_PORT} failed")

        if self.is_port_open(monerod.ip_addr(), monerod.zmq_pub_port()):
            monerod.msg(DLabel.ZMQ_PUB_PORT, DStatus.GOOD,
                        f"Connection to {DLabel.ZMQ_PUB_PORT} successful")
        else:
            monerod.msg(DLabel.ZMQ_PUB_PORT, DStatus.WARN,
                        f"Connection to {DLabel.ZMQ_PUB_PORT} failed")

        if self.is_port_open(monerod.ip_addr(), monerod.zmq_rpc_port()):
            monerod.msg(DLabel.ZMQ_RPC_PORT, DStatus.GOOD,
                        f"Connection to {DLabel.ZMQ_RPC_PORT} successful")
        else:
            monerod.msg(DLabel.ZMQ_RPC_PORT, DStatus.WARN,
                        f"Connection to {DLabel.ZMQ_RPC_PORT} failed")

        return monerod


    def check_monerod_remote(self, monerod: MoneroDRemote) -> MoneroDRemote:
        #print(f"HealthMgr:check_monerod_remote(): rec: {rec}")

        missing_field = False
        if not monerod.instance():
            monerod.msg(DLabel.INSTANCE, DStatus.ERROR, f"{DLabel.INSTANCE} missing")
            missing_field = True

        if not monerod.rpc_bind_port():
            monerod.msg(DLabel.RPC_BIND_PORT, DStatus.ERROR, f"{DLabel.RPC_BIND_PORT} missing")
            missing_field = True

        if not monerod.ip_addr():
            monerod.msg(DLabel.IP_ADDR, DStatus.ERROR, f"{DLabel.IP_ADDR} missing")
            missing_field = True

        if not monerod.zmq_pub_port():
            monerod.msg(DLabel.ZMQ_PUB_PORT, DStatus.ERROR, f"{DLabel.ZMQ_PUB_PORT} missing")
            missing_field = True

        if missing_field:
            return monerod

        if self.is_port_open(monerod.ip_addr(), monerod.rpc_bind_port()):
            monerod.msg(DLabel.RPC_BIND_PORT, DStatus.GOOD,
                        f"Connection to {DLabel.RPC_BIND_PORT} successful")
        else:
            monerod.msg(DLabel.RPC_BIND_PORT, DStatus.WARN,
                        f"Connection to {DLabel.RPC_BIND_PORT} failed")

        if self.is_port_open(monerod.ip_addr(), monerod.zmq_pub_port()):
            monerod.msg(DLabel.ZMQ_PUB_PORT, DStatus.GOOD,
                        f"Connection to {DLabel.ZMQ_PUB_PORT} successful")
        else:
            monerod.msg(DLabel.ZMQ_PUB_PORT, DStatus.WARN,
                        f"Connection to {DLabel.ZMQ_PUB_PORT} failed")

        return monerod


    def check_p2pool(self, p2pool: P2Pool) -> P2Pool:
        # Check for minssing fields
        missing_field = False
        if not p2pool.instance():
            p2pool.msg(DLabel.P2POOL, DStatus.ERROR, f"{DLabel.INSTANCE} missing")
            missing_field = True

        if not os.path.exists(p2pool.config_file()):
            p2pool.msg(DLabel.P2POOL, DStatus.ERROR, f"{DLabel.CONFIG} missing")
            missing_field = True

        if not p2pool.in_peers():
            p2pool.msg(DLabel.P2POOL, DStatus.ERROR, f"{DLabel.IN_PEERS} missing")
            missing_field = True

        if not p2pool.out_peers():
            p2pool.msg(DLabel.P2POOL, DStatus.ERROR, f"{DLabel.OUT_PEERS} missing")
            missing_field = True

        if not p2pool.p2p_port():
            p2pool.msg(DLabel.P2POOL, DStatus.ERROR, f"{DLabel.P2P_BIND_PORT} missing")
            missing_field = True

        if not p2pool.stratum_port():
            p2pool.msg(DLabel.P2POOL, DStatus.ERROR, f"{DLabel.STRATUM_PORT} missing")
            missing_field = True

        if  not p2pool.log_level():
            p2pool.msg(DLabel.P2POOL, DStatus.ERROR, f"{DLabel.LOG_LEVEL} missing")
            missing_field = True

        if not p2pool.parent():
            p2pool.msg(DLabel.PARENT, DStatus.ERROR, f"Missing upstream Blockchain deployment")
            missing_field = True

        if missing_field:
            return p2pool
        
        # Check enabled/disabled
        if p2pool.enabled():
            p2pool.msg(DLabel.P2POOL, DStatus.GOOD,
                       f"{DLabel.P2POOL} ({p2pool.instance()}) is enabled")
        else:
            p2pool.msg(DLabel.P2POOL, DStatus.ERROR,
                       f"{DLabel.P2POOL} ({p2pool.instance()}) is disabled")
            
        # Check connectivity to stratum port
        if self.is_port_open(p2pool.ip_addr(), p2pool.stratum_port()):
            p2pool.msg(DLabel.P2POOL, DStatus.GOOD,
                       f"Connection to {DLabel.STRATUM_PORT} successful")
        else:
            p2pool.msg(DLabel.P2POOL, DStatus.WARN,
                       f"Connection to {DLabel.STRATUM_PORT} failed")
            
        # Check upstgream monerod
        if type(p2pool.monerod) == MoneroD or type(p2pool.monerod) == MoneroDRemote:
            self.check(p2pool.monerod)
            if p2pool.monerod.status() == DStatus.GOOD:
                p2pool.msg(DLabel.MONEROD, DStatus.GOOD,
                        f"Upstream MoneroD ({p2pool.monerod.instance()}) is healthy")
            else:
                p2pool.msg(DLabel.MONEROD, DStatus.WARN,
                        f"Upstream MoneroD ({p2pool.monerod.instance()}) has issues:")
                p2pool.push_msgs(p2pool.monerod.pop_msgs())
        else:
            p2pool.msg(DLabel.MONEROD, DStatus.WARN,
                      f"Missing upstream Monero deployment")            

        #print(f"HealthMgr:check_p2pool(): msgs: {p2pool.pop_msgs()}")
        return p2pool


    def check_p2pool_remote(self, p2pool: P2PoolRemote) -> P2PoolRemote:
        #print(f"HealthMgr:check_p2pool_remote(): rec: {rec}")
        if self.is_port_open(p2pool.ip_addr(), p2pool.stratum_port()):
            p2pool.msg(DLabel.P2POOL, DStatus.GOOD,
                       f"Connection to {DLabel.STRATUM_PORT} successful")
        else:
            p2pool.msg(DLabel.P2POOL, DStatus.WARN,
                       f"Connection to {DLabel.STRATUM_PORT} failed")
        return p2pool        


    def check_int_p2pool(self, p2pool: InternalP2Pool) -> InternalP2Pool:
        # Check enabled/disabled
        if p2pool.enabled():
            p2pool.msg(DLabel.P2POOL, DStatus.GOOD,
                       f"{DLabel.P2POOL} ({p2pool.instance()}) is enabled")
        else:
            p2pool.msg(DLabel.P2POOL, DStatus.ERROR,
                       f"{DLabel.P2POOL} ({p2pool.instance()}) is disabled")
            
        # Check connectivity to stratum port
        if self.is_port_open(p2pool.ip_addr(), p2pool.stratum_port()):
            p2pool.msg(DLabel.P2POOL, DStatus.GOOD,
                       f"Connection to {DLabel.STRATUM_PORT} successful")
        else:
            p2pool.msg(DLabel.P2POOL, DStatus.WARN,
                       f"Connection to {DLabel.STRATUM_PORT} failed")
            
        # Check upstgream monerod
        if p2pool.parent() == DField.DISABLE:
            p2pool.msg(DLabel.MONEROD, DStatus.WARN,
                      f"Missing upstream Monero deployment")       
        return p2pool     


    def check_xmrig(self, xmrig: XMRig) -> XMRig:
        #print(f"HealthMgr:check_xmrig(): p2pool_rec: {p2pool_rec}")

        # Check that the XMRig configuration file exists
        if os.path.exists(xmrig.config_file()):
            xmrig.msg(DLabel.CONFIG_FILE, DStatus.GOOD, f"Found: {xmrig.config_file()}")
        elif not xmrig.config_file:
            xmrig.msg(DLabel.CONFIG_FILE, DStatus.WARN, f"Missing")
        else:
            xmrig.msg(DLabel.CONFIG_FILE, DStatus.WARN, f"Not found: {xmrig.config_file()}")
        
        # Check if the instance is enabled
        if xmrig.enabled():
            xmrig.msg(DLabel.XMRIG, DStatus.GOOD,
                      f"{DLabel.XMRIG} ({xmrig.instance()}) is enabled")
        else:
            xmrig.msg(DLabel.XMRIG, DStatus.ERROR,
                      f"{DLabel.XMRIG} ({xmrig.instance()}) is disabled")


        # Check the upstream P2Pool
        if xmrig.parent() == DField.DISABLE:
            xmrig.msg(DLabel.P2POOL, DStatus.WARN,
                      f"Missing upstream P2pool deployment")

        return xmrig

    def check_xmrig_remote(self, xmrig: XMRigRemote) -> XMRigRemote:
        now = datetime.now().replace(microsecond=0)
        timestamp = xmrig.local_timestamp()
        delta = now - timestamp
        up_since_min = delta.total_seconds() / 60
        print(f"{xmrig}: {up_since_min}")
        if up_since_min < 3:
            xmrig.msg(DLabel.XMRIG, DStatus.GOOD,
                      f"{DLabel.XMRIG} ({xmrig.instance()}) is mining")
        elif up_since_min >= 3 and up_since_min < 5:
            xmrig.msg(DLabel.XMRIG, DStatus.WARN,
                f"{DLabel.XMRIG_REMOTE_SHORT} ({xmrig.instance()}) is not mining")
        elif up_since_min >= 5 and up_since_min < 10:
            xmrig.msg(DLabel.XMRIG, DStatus.ERROR,
                f"{DLabel.XMRIG_REMOTE_SHORT} ({xmrig.instance()}) is not mining")
        else:
            xmrig.msg(DLabel.XMRIG_REMOTE, DStatus.UNKNOWN,
                f"{DLabel.XMRIG_REMOTE_SHORT} ({xmrig.instance()}) is inactive")
        return xmrig


    def is_port_open(self, host, port):
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


