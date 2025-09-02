"""
db4e/Modules/Monerod.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything Monero Daemon
"""

import os

from db4e.Modules.LocalSoftwareSystem import LocalSoftwareSystem
from db4e.Modules.Components import (
    ConfigFile, DataDir, InPeers, Instance, Local, LogLevel, LogFile, 
    MaxLogFiles, MaxLogSize, OutPeers, P2PBindPort, AnyIP, ZmqPubPort,
    ZmqRpcPort, RpcBindPort, ShowTimeStats, PriorityNode1, PriorityNode2,
    PriorityPort1, PriorityPort2, IpAddr, Version)
from db4e.Constants.Fields import (MONEROD_FIELD, CONFIG_FILE_FIELD, DATA_DIR_FIELD,
    IN_PEERS_FIELD, INSTANCE_FIELD, REMOTE_FIELD, LOG_LEVEL_FIELD, LOG_FILE_FIELD,
    MAX_LOG_FILES_FIELD, MAX_LOG_SIZE_FIELD, OUT_PEERS_FIELD, P2P_BIND_PORT_FIELD,
    ZMQ_PUB_PORT_FIELD, ANY_IP_FIELD, ZMQ_RPC_PORT_FIELD, RPC_BIND_PORT_FIELD,
    SHOW_TIME_STATS_FIELD, PRIORITY_NODE_1_FIELD, PRIORITY_NODE_2_FIELD,
    PRIORITY_PORT_1_FIELD, PRIORITY_PORT_2_FIELD, IP_ADDR_FIELD, VERSION_FIELD)
from db4e.Constants.Labels import (MONEROD_LABEL)
from db4e.Constants.Defaults import (
    MONEROD_VERSION_DEFAULT, CONF_DIR_DEFAULT, LOG_DIR_DEFAULT)


class MoneroD(LocalSoftwareSystem):


    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = MONEROD_FIELD
        self.name = MONEROD_LABEL

        self.add_component(ANY_IP_FIELD, AnyIP())
        self.add_component(CONFIG_FILE_FIELD, ConfigFile())
        self.add_component(DATA_DIR_FIELD, DataDir())
        self.add_component(IN_PEERS_FIELD, InPeers())
        self.add_component(INSTANCE_FIELD, Instance())
        self.add_component(IP_ADDR_FIELD, IpAddr())
        self.add_component(LOG_LEVEL_FIELD, LogLevel())
        self.add_component(LOG_FILE_FIELD, LogFile())
        self.add_component(MAX_LOG_FILES_FIELD, MaxLogFiles())
        self.add_component(MAX_LOG_SIZE_FIELD, MaxLogSize())
        self.add_component(OUT_PEERS_FIELD, OutPeers())
        self.add_component(P2P_BIND_PORT_FIELD, P2PBindPort())
        self.add_component(PRIORITY_NODE_1_FIELD, PriorityNode1())
        self.add_component(PRIORITY_PORT_1_FIELD, PriorityPort1())
        self.add_component(PRIORITY_NODE_2_FIELD, PriorityNode2())
        self.add_component(PRIORITY_PORT_2_FIELD, PriorityPort2())
        self.add_component(REMOTE_FIELD, Local())
        self.add_component(RPC_BIND_PORT_FIELD, RpcBindPort())
        self.add_component(SHOW_TIME_STATS_FIELD, ShowTimeStats())
        self.add_component(VERSION_FIELD, Version())
        self.add_component(ZMQ_PUB_PORT_FIELD, ZmqPubPort())
        self.add_component(ZMQ_RPC_PORT_FIELD, ZmqRpcPort())
        
        self.any_ip = self.components[ANY_IP_FIELD]
        self.config_file = self.components[CONFIG_FILE_FIELD]
        self.data_dir = self.components[DATA_DIR_FIELD]
        self.in_peers = self.components[IN_PEERS_FIELD]
        self.instance = self.components[INSTANCE_FIELD]
        self.ip_addr = self.components[IP_ADDR_FIELD]
        self.log_level = self.components[LOG_LEVEL_FIELD]
        self.log_file = self.components[LOG_FILE_FIELD]
        self.max_log_files = self.components[MAX_LOG_FILES_FIELD]
        self.max_log_size = self.components[MAX_LOG_SIZE_FIELD]
        self.out_peers = self.components[OUT_PEERS_FIELD]
        self.p2p_bind_port = self.components[P2P_BIND_PORT_FIELD]
        self.priority_node_1 = self.components[PRIORITY_NODE_1_FIELD]
        self.priority_port_1 = self.components[PRIORITY_PORT_1_FIELD]
        self.priority_node_2 = self.components[PRIORITY_NODE_2_FIELD]
        self.priority_port_2 = self.components[PRIORITY_PORT_2_FIELD]   
        self.remote = self.components[REMOTE_FIELD]
        self.rpc_bind_port = self.components[RPC_BIND_PORT_FIELD]
        self.show_time_stats = self.components[SHOW_TIME_STATS_FIELD]
        self.zmq_pub_port = self.components[ZMQ_PUB_PORT_FIELD]
        self.zmq_rpc_port = self.components[ZMQ_RPC_PORT_FIELD]
        self.version = self.components[VERSION_FIELD]
        self.version(MONEROD_VERSION_DEFAULT)
        
        if rec:
            self.from_rec(rec)

    def gen_config(self, tmpl_file: str, vendor_dir: str):
        # Generate a Monero Daemon configuration file
        monerod_dir = os.path.join(vendor_dir, MONEROD_FIELD)
        fq_config = os.path.join(monerod_dir,CONF_DIR_DEFAULT, self.instance() + '.ini')
        
        # Monerod log file
        fq_log = os.path.join(
            vendor_dir, MONEROD_FIELD, self.instance(), LOG_DIR_DEFAULT, 'monerod.log')
        print(f"MoneroD:gen_config(): data_dir: {self.data_dir()}")
        # Populate the config templace
        placeholders = {
            'ANY_IP': self.any_ip(),
            'DATA_DIR': self.data_dir(),
            'INSTANCE': self.instance(),
            'IN_PEERS': self.in_peers(),
            'LOG_FILE': fq_log,
            'LOG_LEVEL': self.log_level(),
            'MAX_LOG_FILES': self.max_log_files(),
            'MAX_LOG_SIZE': self.max_log_size(),
            'MONEROD_DIR': monerod_dir,
            'OUT_PEERS': self.out_peers(),
            'P2P_BIND_PORT': self.p2p_bind_port(),
            'PRIORITY_NODE_1': self.priority_node_1(),
            'PRIORITY_PORT_1': self.priority_port_1(),
            'PRIORITY_NODE_2': self.priority_node_2(),
            'PRIORITY_PORT_2': self.priority_port_2(),
            'RPC_BIND_PORT': self.rpc_bind_port(),
            'SHOW_TIME_STATS': self.show_time_stats(),
            'ZMQ_PUB_PORT': self.zmq_pub_port(),
            'ZMQ_RPC_PORT': self.zmq_rpc_port(),
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
