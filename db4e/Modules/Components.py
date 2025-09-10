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

from db4e.Constants.Defaults import DDef

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
        super().__init__(DField.ANY_IP, DLabel.ANY_IP, DDef.ANY_IP)


class Chain(Component):
    def __init__(self):
        super().__init__(DField.CHAIN, DLabel.CHAIN, DDef.CHAIN)


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
            DField.DONATION_WALLET, DLabel.DONATIONS_WALLET, 
            DefDB4E.DONATION_WALLET)


class InPeers(Component):
    def __init__(self):
        super().__init(DField.IN_PEERS, DLabel.IN_PEERS, DDef.IN_PEERS)


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
        super().__init(DField.LOG_LEVEL, DLabel.LOG_LEVEL, DDef.LOG_LEVEL)


class LogFile(Component):
    def __init__(self):
        super().__init(DField.LOG_FILE, DLabel.LOG_FILE)


class MaxLogFiles(Component):
    def __init__(self):
        super().__init(
            DField.MAX_LOG_FILES, DLabel.MAX_LOG_FILES, DDef.MAX_LOG_FILES)


class MaxLogSize(Component):
    def __init__(self):
        super().__init(
            DField.MAX_LOG_SIZE, DLabel.MAX_LOG_SIZE, DDef.MAX_LOG_SIZE)


class NumThreads(Component):
    def __init__(self):
        super().__init(
            DField.NUM_THREADS, DLabel.NUM_THREADS, DDef.NUM_THREADS)


class OutPeers(Component):
    def __init__(self):
        super().__init(DField.OUT_PEERS, DLabel.OUT_PEERS, DDef.OUT_PEERS)


class P2PBindPort(Component):
    def __init__(self):
        super().__init(
            DField.P2P_BIND_PORT, DLabel.P2P_BIND_PORT, DDef.P2P_BIND_PORT)


class Parent(Component):
    def __init__(self):
        super().__init(DField.PARENT, DLabel.PARENT)
        
        
class PrimaryServer(Component):
    def __init__(self):
        super().__init__(DField.PRIMARY_SERVER, DLabel.PRIMARY_SERVER, False)


class PriorityNode1(Component):
    def __init__(self):
        super().__init__(
            DField.PRIORITY_NODE_1, DLabel.PRIORITY_NODE_1,
            DDef.PRIORITY_NODE_1)


class PriorityNode2(Component):
    def __init__(self):
        super().__init__(
            DField.PRIORITY_NODE_2, DLabel.PRIORITY_NODE_2, 
            DDef.PRIORITY_NODE_2)


class PriorityPort1(Component):
    def __init__(self):
        super().__init__(
            DField.PRIORITY_PORT_1, DLabel.PRIORITY_PORT_1, 
            DDef.P2P_BIND_PORT)


class PriorityPort2(Component):
    def __init__(self):
        super().__init__(
            DField.PRIORITY_PORT_2, DLabel.PRIORITY_PORT_2, 
            DDef.P2P_BIND_PORT)


class Remote(Component):
    def __init__(self):
        super().__init(DField.REMOTE, DLabel.REMOTE, True)


class RpcBindPort(Component):
    def __init__(self):
        super().__init(
            DField.RPC_BIND_PORT, DLabel.RPC_BIND_PORT, 
            DDef.RPC_BIND_PORT)


class ShowTimeStats(Component):
    def __init__(self):
        super().__init__(
            DField.SHOW_TIME_STATS, DLabel.SHOW_TIME_STATS, 
            DDef.SHOW_TIME_STATS)


class Stdin(Component):
    def __init__(self):
        super().__init__(DField.STDIN, DLabel.STDIN)


class StratumPort(Component):
    def __init__(self):
        super().__init__(DField.STRATUM_PORT, DLabel.STRATUM_PORT, 
                         DDef.STRATUM_PORT)


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
        super().__init__(
            DField.ZMQ_PUB_PORT, DLabel.ZMQ_PUB_PORT, DDef.ZMQ_PUB_PORT)


class ZmqRpcPort(Component):
    def __init__(self):
        super().__init__(
            DField.ZMQ_RPC_PORT, DLabel.ZMQ_RPC_PORT, DDef.ZMQ_RPC_PORT)

