"""
db4e/Modules/P2Pool.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything P2Pool
"""

from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.Components import(
    AnyIP, Chain, ConfigFile, InPeers, Instance, Local, LogLevel, OutPeers,
    P2PBindPort, StratumPort, UserWallet, Version)
from db4e.Constants.Fields import(
    P2POOL_FIELD, ANY_IP_FIELD, CHAIN_FIELD, CONFIG_FILE_FIELD, IN_PEERS_FIELD,
    INSTANCE_FIELD, REMOTE_FIELD, LOG_LEVEL_FIELD, OUT_PEERS_FIELD, P2P_BIND_PORT_FIELD,
    STRATUM_PORT_FIELD, USER_WALLET_FIELD, VERSION_FIELD, COMPONENTS_FIELD, VALUE_FIELD)
from db4e.Constants.Labels import(P2POOL_LABEL)
from db4e.Constants.Defaults import(P2POOL_VERSION_DEFAULT)


class P2Pool(SoftwareSystem):
    
    
    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = P2POOL_FIELD
        self.name = P2POOL_LABEL

        self.add_component(ANY_IP_FIELD, AnyIP())
        self.add_component(CHAIN_FIELD, Chain())
        self.add_component(CONFIG_FILE_FIELD, ConfigFile())
        self.add_component(IN_PEERS_FIELD, InPeers())
        self.add_component(INSTANCE_FIELD, Instance())
        self.add_component(REMOTE_FIELD, Local())
        self.add_component(LOG_LEVEL_FIELD, LogLevel())
        self.add_component(OUT_PEERS_FIELD, OutPeers())
        self.add_component(P2P_BIND_PORT_FIELD, P2PBindPort())
        self.add_component(STRATUM_PORT_FIELD, StratumPort())
        self.add_component(USER_WALLET_FIELD, UserWallet())
        self.add_component(VERSION_FIELD, Version())

        self.any_ip = self.components[ANY_IP_FIELD]
        self.chain = self.components[CHAIN_FIELD]
        self.config_file = self.components[CONFIG_FILE_FIELD]
        self.in_peers = self.components[IN_PEERS_FIELD]
        self.instance = self.components[INSTANCE_FIELD]
        self.remote = self.components[REMOTE_FIELD]
        self.log_level = self.components[LOG_LEVEL_FIELD]
        self.out_peers = self.components[OUT_PEERS_FIELD]
        self.p2p_bind_port = self.components[P2P_BIND_PORT_FIELD]
        self.stratum_port = self.components[STRATUM_PORT_FIELD]
        self.user_wallet = self.components[USER_WALLET_FIELD]
        self.version = self.components[VERSION_FIELD]
        self.version.value = P2POOL_VERSION_DEFAULT

        self.monerod = None
        if rec:
            self.from_rec(rec)
        