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
import errno

from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.Components import(
    AnyIP, Chain, ConfigFile, InPeers, Instance, Local, LogLevel, OutPeers, Enabled,
    P2PPort, StratumPort, UserWallet, Version, IpAddr, Parent, LogFile, StdinPath)
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DDef import DDef
from db4e.Constants.DPlaceholder import DPlaceholder



class P2Pool(SoftwareSystem):
    
    
    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = DElem.P2POOL
        self.name = DLabel.P2POOL

        self.add_component(DField.ANY_IP, AnyIP())
        self.add_component(DField.CHAIN, Chain())
        self.add_component(DField.CONFIG_FILE, ConfigFile())
        self.add_component(DField.ENABLED, Enabled())
        self.add_component(DField.IN_PEERS, InPeers())
        self.add_component(DField.INSTANCE, Instance())
        self.add_component(DField.IP_ADDR, IpAddr())
        self.add_component(DField.LOG_FILE, LogFile())
        self.add_component(DField.REMOTE, Local())
        self.add_component(DField.LOG_LEVEL, LogLevel())
        self.add_component(DField.OUT_PEERS, OutPeers())
        self.add_component(DField.P2P_PORT, P2PPort())
        self.add_component(DField.PARENT, Parent())
        self.add_component(DField.STDIN_PATH, StdinPath())
        self.add_component(DField.STRATUM_PORT, StratumPort())
        self.add_component(DField.USER_WALLET, UserWallet())
        self.add_component(DField.VERSION, Version())

        self.any_ip = self.components[DField.ANY_IP]
        self.chain = self.components[DField.CHAIN]
        self.config_file = self.components[DField.CONFIG_FILE]
        self.enabled = self.components[DField.ENABLED]
        self.in_peers = self.components[DField.IN_PEERS]
        self.instance = self.components[DField.INSTANCE]
        self.ip_addr = self.components[DField.IP_ADDR]
        self.log_file = self.components[DField.LOG_FILE]
        self.remote = self.components[DField.REMOTE]
        self.log_level = self.components[DField.LOG_LEVEL]
        self.out_peers = self.components[DField.OUT_PEERS]
        self.p2p_port = self.components[DField.P2P_PORT]
        self.parent = self.components[DField.PARENT]
        self.stratum_port = self.components[DField.STRATUM_PORT]
        self.stdin_path = self.components[DField.STDIN_PATH]
        self.user_wallet = self.components[DField.USER_WALLET]
        self.version = self.components[DField.VERSION]
        self.version(DDef.P2POOL_VERSION)
        self._instance_map = {}

        self.monerod = None
        self.parent(DField.DISABLE)
        self._hashrates = None
        self._hashrate = None
        
        if rec:
            self.from_rec(rec)

    def gen_config(self, tmpl_file: str, vendor_dir: str):
        # Generate a XMRig configuration file

        p2pool_dir = os.path.join(vendor_dir, DElem.P2POOL)
        api_dir = os.path.join(p2pool_dir, self.instance(), DDef.API_DIR)
        run_dir = os.path.join(p2pool_dir, self.instance(), DDef.RUN_DIR)
        log_dir = os.path.join(p2pool_dir, self.instance(), DDef.LOG_DIR)

        fq_config = os.path.join(
            p2pool_dir, DDef.CONF_DIR, self.instance() + DDef.INI_SUFFIX)

        # Monero settings
        monerod_ip = self.monerod.ip_addr()
        monerod_zmq_port = self.monerod.zmq_pub_port()
        monerod_rpc_port = self.monerod.rpc_bind_port()

        # Populate the config templace placeholders
        placeholders = {
            DPlaceholder.WALLET : self.user_wallet(),
            DPlaceholder.P2P_DIR : p2pool_dir,
            DPlaceholder.MONEROD_IP : monerod_ip,
            DPlaceholder.ZMQ_PUB_PORT : monerod_zmq_port,
            DPlaceholder.RPC_BIND_PORT : monerod_rpc_port,
            DPlaceholder.LOG_LEVEL : self.log_level(),
            DPlaceholder.P2P_PORT : self.p2p_port(),
            DPlaceholder.STRATUM_PORT : self.stratum_port(),
            DPlaceholder.IN_PEERS : self.in_peers(),
            DPlaceholder.OUT_PEERS : self.out_peers(),
            DPlaceholder.CHAIN : self.chain(),
            DPlaceholder.ANY_IP : self.any_ip(),
            DPlaceholder.API_DIR : api_dir,
            DPlaceholder.RUN_DIR : run_dir,
            DPlaceholder.LOG_DIR : log_dir,
        }
        with open(tmpl_file, 'r') as f:
            config_contents = f.read()
            final_config = config_contents
            for key, val in placeholders.items():
                final_config = final_config.replace(f'[[{key}]]', str(val))

        # Write the config to file
        with open(fq_config, 'w') as f:
            f.write(final_config)
        self.config_file(fq_config)


    def hashrate(self, hashrate=None):
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate
    

    def hashrates(self, hashrate_data=None):
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates
    
        
    def instance_map(self, map=None):
        if map is not None:
            self._instance_map = map
        return self._instance_map
    




