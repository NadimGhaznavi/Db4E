"""
db4e/Modules/MoneroD.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything Monero Daemon
"""

import os

from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.Components import (
    BlockchainDir, ConfigFile, InPeers, Instance, Local, LogLevel, LogFile, 
    MaxLogFiles, MaxLogSize, OutPeers, P2PBindPort, AnyIP, ZmqPubPort,
    ZmqRpcPort, RpcBindPort, ShowTimeStats, PriorityNode1, PriorityNode2,
    PriorityPort1, PriorityPort2, IpAddr, Version, StdinPath, Enabled)

from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DDef import DDef
from db4e.Constants.DElem import DElem
from db4e.Constants.DPlaceholder import DPlaceholder


class MoneroD(SoftwareSystem):


    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = DElem.MONEROD
        self.name = DLabel.MONEROD

        self.add_component(DField.ANY_IP, AnyIP())
        self.add_component(DField.BLOCKCHAIN_DIR, BlockchainDir())
        self.add_component(DField.CONFIG_FILE, ConfigFile())
        self.add_component(DField.ENABLED, Enabled())
        self.add_component(DField.IN_PEERS, InPeers())
        self.add_component(DField.INSTANCE, Instance())
        self.add_component(DField.IP_ADDR, IpAddr())
        self.add_component(DField.LOG_LEVEL, LogLevel())
        self.add_component(DField.LOG_FILE, LogFile())
        self.add_component(DField.MAX_LOG_FILES, MaxLogFiles())
        self.add_component(DField.MAX_LOG_SIZE, MaxLogSize())
        self.add_component(DField.OUT_PEERS, OutPeers())
        self.add_component(DField.P2P_BIND_PORT, P2PBindPort())
        self.add_component(DField.PRIORITY_NODE_1, PriorityNode1())
        self.add_component(DField.PRIORITY_PORT_1, PriorityPort1())
        self.add_component(DField.PRIORITY_NODE_2, PriorityNode2())
        self.add_component(DField.PRIORITY_PORT_2, PriorityPort2())
        self.add_component(DField.REMOTE, Local())
        self.add_component(DField.RPC_BIND_PORT, RpcBindPort())
        self.add_component(DField.SHOW_TIME_STATS, ShowTimeStats())
        self.add_component(DField.STDIN_PATH, StdinPath())
        self.add_component(DField.VERSION, Version())
        self.add_component(DField.ZMQ_PUB_PORT, ZmqPubPort())
        self.add_component(DField.ZMQ_RPC_PORT, ZmqRpcPort())
        
        self.any_ip = self.components[DField.ANY_IP]
        self.blockchain_dir = self.components[DField.BLOCKCHAIN_DIR]
        self.config_file = self.components[DField.CONFIG_FILE]
        self.enabled = self.components[DField.ENABLED]
        self.in_peers = self.components[DField.IN_PEERS]
        self.instance = self.components[DField.INSTANCE]
        self.ip_addr = self.components[DField.IP_ADDR]
        self.log_level = self.components[DField.LOG_LEVEL]
        self.log_file = self.components[DField.LOG_FILE]
        self.max_log_files = self.components[DField.MAX_LOG_FILES]
        self.max_log_size = self.components[DField.MAX_LOG_SIZE]
        self.out_peers = self.components[DField.OUT_PEERS]
        self.p2p_bind_port = self.components[DField.P2P_BIND_PORT]
        self.priority_node_1 = self.components[DField.PRIORITY_NODE_1]
        self.priority_port_1 = self.components[DField.PRIORITY_PORT_1]
        self.priority_node_2 = self.components[DField.PRIORITY_NODE_2]
        self.priority_port_2 = self.components[DField.PRIORITY_PORT_2]   
        self.remote = self.components[DField.REMOTE]
        self.rpc_bind_port = self.components[DField.RPC_BIND_PORT]
        self.show_time_stats = self.components[DField.SHOW_TIME_STATS]
        self.stdin_path = self.components[DField.STDIN_PATH]
        self.zmq_pub_port = self.components[DField.ZMQ_PUB_PORT]
        self.zmq_rpc_port = self.components[DField.ZMQ_RPC_PORT]
        self.version = self.components[DField.VERSION]
        self.version(DDef.MONEROD_VERSION)
        
        if rec:
            self.from_rec(rec)

    def gen_config(self, tmpl_file: str, vendor_dir: str):
        # Generate a Monero Daemon configuration file
        monerod_dir = os.path.join(vendor_dir, DElem.MONEROD)
        fq_config = os.path.join(
            monerod_dir, DDef.CONF_DIR, self.instance() + DDef.INI_SUFFIX)
        
        # Monerod log file
        fq_log = os.path.join(
            vendor_dir, DElem.MONEROD, self.instance(), DDef.LOG_DIR, 
            DDef.MONEROD_LOG_FILE)

        # Populate the config templace
        placeholders = {
            DPlaceholder.ANY_IP : self.any_ip(),
            DPlaceholder.BLOCKCHAIN_DIR : self.blockchain_dir(),
            DPlaceholder.INSTANCE : self.instance(),
            DPlaceholder.IN_PEERS : self.in_peers(),
            DPlaceholder.LOG_FILE : fq_log,
            DPlaceholder.LOG_LEVEL : self.log_level(),
            DPlaceholder.MAX_LOG_FILES : self.max_log_files(),
            DPlaceholder.MAX_LOG_SIZE : self.max_log_size(),
            DPlaceholder.MONEROD_DIR : monerod_dir,
            DPlaceholder.OUT_PEERS : self.out_peers(),
            DPlaceholder.P2P_BIND_PORT : self.p2p_bind_port(),
            DPlaceholder.PRIORITY_NODE_1 : self.priority_node_1(),
            DPlaceholder.PRIORITY_PORT_1 : self.priority_port_1(),
            DPlaceholder.PRIORITY_NODE_2 : self.priority_node_2(),
            DPlaceholder.PRIORITY_PORT_2 : self.priority_port_2(),
            DPlaceholder.RPC_BIND_PORT : self.rpc_bind_port(),
            DPlaceholder.SHOW_TIME_STATS : self.show_time_stats(),
            DPlaceholder.STDIN_PATH : self.stdin_path(),
            DPlaceholder.ZMQ_PUB_PORT : self.zmq_pub_port(),
            DPlaceholder.ZMQ_RPC_PORT : self.zmq_rpc_port(),
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
