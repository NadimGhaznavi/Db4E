"""
db4e/Modules/P2Pool.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything P2Pool
"""

import os

from db4e.Modules.LocalSoftwareSystem import LocalSoftwareSystem
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.Components import(
    AnyIP, Chain, ConfigFile, InPeers, Instance, Local, LogLevel, OutPeers,
    P2PBindPort, StratumPort, UserWallet, Version, IpAddr, Parent)
from db4e.Constants.Fields import(
    P2POOL_FIELD, ANY_IP_FIELD, CHAIN_FIELD, CONFIG_FILE_FIELD, IN_PEERS_FIELD,
    INSTANCE_FIELD, REMOTE_FIELD, LOG_LEVEL_FIELD, OUT_PEERS_FIELD, P2P_BIND_PORT_FIELD,
    STRATUM_PORT_FIELD, USER_WALLET_FIELD, VERSION_FIELD, IP_ADDR_FIELD, PARENT_FIELD)
from db4e.Constants.Labels import(P2POOL_LABEL)
from db4e.Constants.Defaults import(
    P2POOL_VERSION_DEFAULT, CONF_DIR_DEFAULT, API_DIR_DEFAULT, RUN_DIR_DEFAULT,
    LOG_DIR_DEFAULT)


class P2Pool(LocalSoftwareSystem):
    
    
    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = P2POOL_FIELD
        self.name = P2POOL_LABEL

        self.add_component(ANY_IP_FIELD, AnyIP())
        self.add_component(CHAIN_FIELD, Chain())
        self.add_component(CONFIG_FILE_FIELD, ConfigFile())
        self.add_component(IN_PEERS_FIELD, InPeers())
        self.add_component(INSTANCE_FIELD, Instance())
        self.add_component(IP_ADDR_FIELD, IpAddr())
        self.add_component(REMOTE_FIELD, Local())
        self.add_component(LOG_LEVEL_FIELD, LogLevel())
        self.add_component(OUT_PEERS_FIELD, OutPeers())
        self.add_component(P2P_BIND_PORT_FIELD, P2PBindPort())
        self.add_component(PARENT_FIELD, Parent())
        self.add_component(STRATUM_PORT_FIELD, StratumPort())
        self.add_component(USER_WALLET_FIELD, UserWallet())
        self.add_component(VERSION_FIELD, Version())

        self.any_ip = self.components[ANY_IP_FIELD]
        self.chain = self.components[CHAIN_FIELD]
        self.config_file = self.components[CONFIG_FILE_FIELD]
        self.in_peers = self.components[IN_PEERS_FIELD]
        self.instance = self.components[INSTANCE_FIELD]
        self.ip_addr = self.components[IP_ADDR_FIELD]
        self.remote = self.components[REMOTE_FIELD]
        self.log_level = self.components[LOG_LEVEL_FIELD]
        self.out_peers = self.components[OUT_PEERS_FIELD]
        self.p2p_bind_port = self.components[P2P_BIND_PORT_FIELD]
        self.parent = self.components[PARENT_FIELD]
        self.stratum_port = self.components[STRATUM_PORT_FIELD]
        self.user_wallet = self.components[USER_WALLET_FIELD]
        self.version = self.components[VERSION_FIELD]
        self.version.value = P2POOL_VERSION_DEFAULT
        self._instance_map = {}
        self.monerod = None

        self.monerod = None
        if rec:
            self.from_rec(rec)

    def gen_config(self, tmpl_file: str, vendor_dir: str):
        # Generate a XMRig configuration file

        p2pool_dir = os.path.join(vendor_dir, P2POOL_FIELD)
        api_dir = os.path.join(p2pool_dir, self.instance(), API_DIR_DEFAULT)
        run_dir = os.path.join(p2pool_dir, self.instance(), RUN_DIR_DEFAULT)
        log_dir = os.path.join(p2pool_dir, self.instance(), LOG_DIR_DEFAULT)

        fq_config = os.path.join(
            p2pool_dir, CONF_DIR_DEFAULT, self.instance.value + '.ini')

        # Monero settings
        monerod_ip = self.monerod.ip_addr()
        monerod_zmq_port = self.monerod.zmq_pub_port()
        monerod_rpc_port = self.monerod.rpc_bind_port()

        # Populate the config templace placeholders
        placeholders = {
            'WALLET': self.user_wallet(),
            'P2P_DIR': p2pool_dir,
            'MONEROD_IP': monerod_ip,
            'ZMQ_PORT': monerod_zmq_port,
            'RPC_PORT': monerod_rpc_port,
            'LOG_LEVEL': self.log_level(),
            'P2P_BIND_PORT': self.p2p_bind_port(),
            'STRATUM_PORT': self.stratum_port(),
            'IN_PEERS': self.in_peers(),
            'OUT_PEERS': self.out_peers(),
            'CHAIN': self.chain(),
            'ANY_IP': self.any_ip(),
            'API_DIR': api_dir,
            'RUN_DIR': run_dir,
            'LOG_DIR': log_dir,
        }
        with open(tmpl_file, 'r') as f:
            config_contents = f.read()
            final_config = config_contents
            for key, val in placeholders.items():
                final_config = final_config.replace(f'[[{key}]]', str(val))

        # Write the config to file
        with open(fq_config, 'w') as f:
            f.write(final_config)
        self.config_file.value = fq_config
        
        
    def instance_map(self, map=None):
        if map:
            self._instance_map = map
        return self._instance_map        