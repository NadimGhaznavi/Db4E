"""
db4e/Constants/Components.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Constants.Fields import (
    ANY_IP_FIELD, CHAIN_FIELD, CONFIG_FIELD, DATA_DIR_FIELD,
    DONATION_WALLET_FIELD, FIELD_FIELD, GROUP_FIELD, HEALTH_MSGS_FIELD, 
    IN_PEERS_FIELD,
    INSTALL_DIR_FIELD, INSTANCE_FIELD, IP_ADDR_FIELD, LABEL_FIELD,
    LOG_LEVEL_FIELD, LOG_NAME_FIELD, MAX_LOG_FILES_FIELD,
    MAX_LOG_SIZE_FIELD, NUM_THREADS_FIELD, OUT_PEERS_FIELD,
    P2P_BIND_PORT_FIELD, OBJECT_ID_FIELD, PRIORITY_NODE_1_FIELD,
    PRIORITY_NODE_2_FIELD, PRIORITY_PORT_1_FIELD, PRIORITY_PORT_2_FIELD,
    REMOTE_FIELD, RPC_BIND_PORT_FIELD, SHOW_TIME_STATS_FIELD,
    STRATUM_PORT_FIELD, USER_FIELD, USER_WALLET_FIELD, VALUE_FIELD,
    VENDOR_DIR_FIELD, VERSION_FIELD, ZMQ_PUB_PORT_FIELD, ZMQ_RPC_PORT_FIELD,
    CONFIG_FILE_FIELD, PARENT_FIELD
)
from db4e.Constants.Labels import (
    ANY_IP_LABEL, CHAIN_LABEL, DATA_DIR_LABEL, DONATIONS_WALLET_LABEL,
    GROUP_LABEL, PARENT_LABEL, IN_PEERS_LABEL, INSTALL_DIR_LABEL, INSTANCE_LABEL, IP_ADDR_LABEL,
    LOG_LEVEL_LABEL, LOG_NAME_LABEL, MAX_LOG_FILES_LABEL, MAX_LOG_SIZE_LABEL,
    NUM_THREADS_LABEL, OUT_PEERS_LABEL, P2P_BIND_PORT_LABEL,
    PRIORITY_NODE_1_LABEL, PRIORITY_NODE_2_LABEL, PRIORITY_PORT_1_LABEL,
    PRIORITY_PORT_2_LABEL, REMOTE_LABEL, RPC_BIND_PORT_LABEL, SHOW_TIME_STATS_LABEL,
    STRATUM_PORT_LABEL, USER_LABEL, USER_WALLET_LABEL, VENDOR_DIR_LABEL, VERSION_LABEL,
    ZMQ_PUB_PORT_LABEL, ZMQ_RPC_PORT_LABEL, CONFIG_FILE_LABLE, OBJECT_ID_LABEL
)
from db4e.Constants.Defaults import (
    ANY_IP_DEFAULT, CHAIN_DEFAULT, DONATION_WALLET_DEFAULT, IN_PEERS_DEFAULT,
    LOG_LEVEL_DEFAULT, MAX_LOG_FILES_DEFAULT, MAX_LOG_SIZE_DEFAULT,
    NUM_THREADS_DEFAULT, OUT_PEERS_DEFAULT,
    P2P_BIND_PORT_DEFAULT, PRIORITY_NODE_1_DEFAULT, PRIORITY_NODE_2_DEFAULT,
    RPC_BIND_PORT_DEFAULT, SHOW_TIME_STATS_FIELD_DEFAULT, STRATUM_PORT_DEFAULT,
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
        super().__init__(ANY_IP_FIELD, ANY_IP_LABEL, ANY_IP_DEFAULT)


class Chain(Component):
    def __init__(self):
        super().__init__(CHAIN_FIELD, CHAIN_LABEL, CHAIN_DEFAULT)


class ConfigFile(Component):
    def __init__(self):
        super().__init__(CONFIG_FILE_FIELD, CONFIG_FILE_LABLE)


class DataDir(Component):
    def __init__(self):
        super().__init__(DATA_DIR_FIELD, DATA_DIR_LABEL)


class Db4eGroup(Component):
    def __init__(self):
        super().__init__(GROUP_FIELD, GROUP_LABEL)


class Db4eUser(Component):
    def __init__(self):
        super().__init__(USER_FIELD, USER_LABEL)


class DonationWallet(Component):
    def __init__(self):
        super().__init__(
            DONATION_WALLET_FIELD, DONATIONS_WALLET_LABEL, DONATION_WALLET_DEFAULT)


class InPeers(Component):
    def __init__(self):
        super().__init__(IN_PEERS_FIELD, IN_PEERS_LABEL, IN_PEERS_DEFAULT)


class InstallDir(Component):
    def __init__(self):
        super().__init__(INSTALL_DIR_FIELD, INSTALL_DIR_LABEL)


class Instance(Component):
    def __init__(self):
        super().__init__(INSTANCE_FIELD, INSTANCE_LABEL)


class IpAddr(Component):
    def __init__(self):
        super().__init__(IP_ADDR_FIELD, IP_ADDR_LABEL)


class Local(Component):
    def __init__(self):
        super().__init__(REMOTE_FIELD, REMOTE_LABEL, False)


class LogLevel(Component):
    def __init__(self):
        super().__init__(LOG_LEVEL_FIELD, LOG_LEVEL_LABEL, LOG_LEVEL_DEFAULT)


class LogName(Component):
    def __init__(self):
        super().__init__(LOG_NAME_FIELD, LOG_NAME_LABEL)


class MaxLogFiles(Component):
    def __init__(self):
        super().__init__(MAX_LOG_FILES_FIELD, MAX_LOG_FILES_LABEL, MAX_LOG_FILES_DEFAULT)


class MaxLogSize(Component):
    def __init__(self):
        super().__init__(MAX_LOG_SIZE_FIELD, MAX_LOG_SIZE_LABEL, MAX_LOG_SIZE_DEFAULT)


class NumThreads(Component):
    def __init__(self):
        super().__init__(NUM_THREADS_FIELD, NUM_THREADS_LABEL, NUM_THREADS_DEFAULT)


class ObjectId(Component):
    def __init__(self):
        super().__init__(OBJECT_ID_FIELD, OBJECT_ID_LABEL)


class OutPeers(Component):
    def __init__(self):
        super().__init__(OUT_PEERS_FIELD, OUT_PEERS_LABEL, OUT_PEERS_DEFAULT)


class P2PBindPort(Component):
    def __init__(self):
        super().__init__(P2P_BIND_PORT_FIELD, P2P_BIND_PORT_LABEL, P2P_BIND_PORT_DEFAULT)


class Parent(Component):
    def __init__(self):
        super().__init__(PARENT_FIELD, PARENT_LABEL)
        
        
class PriorityNode1(Component):
    def __init__(self):
        super().__init__(
            PRIORITY_NODE_1_FIELD, PRIORITY_NODE_1_LABEL, PRIORITY_NODE_1_DEFAULT)


class PriorityNode2(Component):
    def __init__(self):
        super().__init__(
            PRIORITY_NODE_2_FIELD, PRIORITY_NODE_2_LABEL, PRIORITY_NODE_2_DEFAULT)


class PriorityPort1(Component):
    def __init__(self):
        super().__init__(
            PRIORITY_PORT_1_FIELD, PRIORITY_PORT_1_LABEL, P2P_BIND_PORT_DEFAULT)


class PriorityPort2(Component):
    def __init__(self):
        super().__init__(
            PRIORITY_PORT_2_FIELD, PRIORITY_PORT_2_LABEL, P2P_BIND_PORT_DEFAULT)


class Remote(Component):
    def __init__(self):
        super().__init__(REMOTE_FIELD, REMOTE_LABEL, True)


class RpcBindPort(Component):
    def __init__(self):
        super().__init__(RPC_BIND_PORT_FIELD, RPC_BIND_PORT_LABEL, RPC_BIND_PORT_DEFAULT)


class ShowTimeStats(Component):
    def __init__(self):
        super().__init__(
            SHOW_TIME_STATS_FIELD, SHOW_TIME_STATS_LABEL, SHOW_TIME_STATS_FIELD_DEFAULT)


class StratumPort(Component):
    def __init__(self):
        super().__init__(STRATUM_PORT_FIELD, STRATUM_PORT_LABEL, STRATUM_PORT_DEFAULT)


class Version(Component):
    def __init__(self):
        super().__init__(VERSION_FIELD, VERSION_LABEL)


class UserWallet(Component):
    def __init__(self):
        super().__init__(USER_WALLET_FIELD, USER_WALLET_LABEL)


class VendorDir(Component):
    def __init__(self):
        super().__init__(VENDOR_DIR_FIELD, VENDOR_DIR_LABEL)


class ZmqPubPort(Component):
    def __init__(self):
        super().__init__(ZMQ_PUB_PORT_FIELD, ZMQ_PUB_PORT_LABEL, ZMQ_PUB_PORT_DEFAULT)


class ZmqRpcPort(Component):
    def __init__(self):
        super().__init__(ZMQ_RPC_PORT_FIELD, ZMQ_RPC_PORT_LABEL, ZMQ_RPC_PORT_DEFAULT)

