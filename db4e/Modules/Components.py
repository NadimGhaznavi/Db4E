"""
db4e/Constants/Components.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Constants.Fields import DDir, DFile, DField
from db4e.Constants.Labels import DLabel
from db4e.Constants.Defaults import (
    ANY_IP_DEFAULT, CHAIN_DEFAULT, DONATION_WALLET_DEFAULT, IN_PEERS_DEFAULT,
    LOG_LEVEL_DEFAULT, MAX_LOG_FILES_DEFAULT, MAX_LOG_SIZE_DEFAULT,
    NUM_THREADS_DEFAULT, OUT_PEERS_DEFAULT,
    P2P_BIND_PORT_DEFAULT, PRIORITY_NODE_1_DEFAULT, PRIORITY_NODE_2_DEFAULT,
    RPC_BIND_PORT_DEFAULT, SHOW_TIME_STATS_DEFAULT, STRATUM_PORT_DEFAULT,
    ZMQ_PUB_PORT_DEFAULT, ZMQ_RPC_PORT_DEFAULT
)


class Component:
    def __init__(self, field, label, default_value=""):
        self.field = field
        self.label = label
        self.value = default_value
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.field}={self.value!r}>"
    
    def __eq__(self, other):
        if isinstance(other, Component):
            return (
                self.field == other.field and
                self.label == other.label and
                self.value == other.value
            )
        raise ValueError(f"Cannot compare {self.__class__.__name__} with {type(other).__name__}")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __call__(self, *args):
        if not args:
            return self.value
        elif len(args) == 1:
            self.value = args[0]
            return self  # return self so you can chain calls if you want
        else:
            raise TypeError(
                f"{self.__class__.__name__}.__call__ takes at most 1 argument ({len(args)} given)"
            )

class AnyIP(Component):
    def __init__(self):
        super().__init__(DField.ANY_IP, DLabel.ANY_IP, ANY_IP_DEFAULT)


class Chain(Component):
    def __init__(self):
        super().__init__(DField.CHAIN, DLabel.CHAIN, CHAIN_DEFAULT)


class ConfigFile(Component):
    def __init__(self):
        super().__init__(DField.CONFIG_FILE, DLabel.CONFIG_FILE)


class DataDir(Component):
    def __init__(self):
        super().__init__(DField.DATA, DLabel.DATA_DIR)


class Db4eGroup(Component):
    def __init__(self):
        super().__init__(DField.GROUP, DLabel.GROUP)


class Db4eUser(Component):
    def __init__(self):
        super().__init__(DField.USER, DLabel.USER)


class DonationWallet(Component):
    def __init__(self):
        super().__init__(
            DField.DONATION_WALLET, DLabel.DONATIONS_WALLET, DONATION_WALLET_DEFAULT)


class InPeers(Component):
    def __init__(self):
        super().__init(DField.IN_PEERS, DLabel.IN_PEERS, IN_PEERS_DEFAULT)


class InstallDir(Component):
    def __init__(self):
        super().__init__(DDir.INSTALL, DLabel.INSTALL_DIR)


class Instance(Component):
    def __init__(self):
        super().__init(DField.INSTANCE, DLabel.INSTANCE)


class IpAddr(Component):
    def __init__(self):
        super().__init(DField.IP_ADDR, DLabel.IP_ADDR)


class Local(Component):
    def __init__(self):
        super().__init(DField.REMOTE, DLabel.REMOTE, False)


class LogLevel(Component):
    def __init__(self):
        super().__init(DField.LOG_LEVEL, DLabel.LOG_LEVEL, LOG_LEVEL_DEFAULT)


class LogFile(Component):
    def __init__(self):
        super().__init(DField.LOG_FILE, DLabel.LOG_FILE)


class MaxLogFiles(Component):
    def __init__(self):
        super().__init(DField.MAX_LOG_FILES, DLabel.MAX_LOG_FILES, MAX_LOG_FILES_DEFAULT)


class MaxLogSize(Component):
    def __init__(self):
        super().__init(DField.MAX_LOG_SIZE, DLabel.MAX_LOG_SIZE, MAX_LOG_SIZE_DEFAULT)


class NumThreads(Component):
    def __init__(self):
        super().__init(DField.NUM_THREADS, DLabel.NUM_THREADS, NUM_THREADS_DEFAULT)


class OutPeers(Component):
    def __init__(self):
        super().__init(DField.OUT_PEERS, DLabel.OUT_PEERS, OUT_PEERS_DEFAULT)


class P2PBindPort(Component):
    def __init__(self):
        super().__init(DField.P2P_BIND_PORT, DLabel.P2P_BIND_PORT, P2P_BIND_PORT_DEFAULT)


class Parent(Component):
    def __init__(self):
        super().__init(DField.PARENT, DLabel.PARENT)
        
        
class PrimaryServer(Component):
    def __init__(self):
        super().__init__(DField.PRIMARY_SERVER, DLabel.PRIMARY_SERVER, False)


class PriorityNode1(Component):
    def __init__(self):
        super().__init__(
            DField.PRIORITY_NODE_1, DLabel.PRIORITY_NODE_1, PRIORITY_NODE_1_DEFAULT)


class PriorityNode2(Component):
    def __init__(self):
        super().__init__(
            DField.PRIORITY_NODE_2, DLabel.PRIORITY_NODE_2, PRIORITY_NODE_2_DEFAULT)


class PriorityPort1(Component):
    def __init__(self):
        super().__init__(
            DField.PRIORITY_PORT_1, DLabel.PRIORITY_PORT_1, P2P_BIND_PORT_DEFAULT)


class PriorityPort2(Component):
    def __init__(self):
        super().__init__(
            DField.PRIORITY_PORT_2, DLabel.PRIORITY_PORT_2, P2P_BIND_PORT_DEFAULT)


class Remote(Component):
    def __init__(self):
        super().__init(DField.REMOTE, DLabel.REMOTE, True)


class RpcBindPort(Component):
    def __init__(self):
        super().__init(DField.RPC_BIND_PORT, DLabel.RPC_BIND_PORT, RPC_BIND_PORT_DEFAULT)


class ShowTimeStats(Component):
    def __init__(self):
        super().__init__(
            DField.SHOW_TIME_STATS, DLabel.SHOW_TIME_STATS, SHOW_TIME_STATS_DEFAULT)


class Stdin(Component):
    def __init__(self):
        super().__init__(DField.STDIN, DLabel.STDIN)


class StratumPort(Component):
    def __init__(self):
        super().__init__(DField.STRATUM_PORT, DLabel.STRATUM_PORT, STRATUM_PORT_DEFAULT)


class Version(Component):
    def __init__(self):
        super().__init__(DField.VERSION, DLabel.VERSION)


class UserWallet(Component):
    def __init__(self):
        super().__init__(DField.USER_WALLET, DLabel.USER_WALLET)


class VendorDir(Component):
    def __init__(self):
        super().__init__(DDir.VENDOR, DLabel.VENDOR_DIR)


class ZmqPubPort(Component):
    def __init__(self):
        super().__init__(DField.ZMQ_PUB_PORT, DLabel.ZMQ_PUB_PORT, ZMQ_PUB_PORT_DEFAULT)


class ZmqRpcPort(Component):
    def __init__(self):
        super().__init__(DField.ZMQ_RPC_PORT, DLabel.ZMQ_RPC_PORT, ZMQ_RPC_PORT_DEFAULT)

