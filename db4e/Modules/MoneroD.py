"""
db4e/Modules/Monerod.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything Monero Daemon
"""

from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.Components import (
    ConfigFile, DataDir, InPeers, Instance, Local, LogLevel, LogName, 
    MaxLogFiles, MaxLogSize, OutPeers, P2PBindPort, ObjectId)
from db4e.Constants.Fields import (MONEROD_FIELD, CONFIG_FILE_FIELD, DATA_DIR_FIELD,
    IN_PEERS_FIELD, INSTANCE_FIELD, REMOTE_FIELD, LOG_LEVEL_FIELD, LOG_NAME_FIELD,
    MAX_LOG_FILES_FIELD, MAX_LOG_SIZE_FIELD, OUT_PEERS_FIELD, P2P_BIND_PORT_FIELD,
    OBJECT_ID_FIELD)
from db4e.Constants.Labels import (MONEROD_LABEL)

class MoneroD(SoftwareSystem):


    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = MONEROD_FIELD
        self.name = MONEROD_LABEL

        self.add_component(CONFIG_FILE_FIELD, ConfigFile())
        self.add_component(DATA_DIR_FIELD, DataDir())
        self.add_component(IN_PEERS_FIELD, InPeers())
        self.add_component(INSTANCE_FIELD, Instance())
        self.add_component(LOG_LEVEL_FIELD, LogLevel())
        self.add_component(LOG_NAME_FIELD, LogName())
        self.add_component(MAX_LOG_FILES_FIELD, MaxLogFiles())
        self.add_component(MAX_LOG_SIZE_FIELD, MaxLogSize())
        self.add_component(OUT_PEERS_FIELD, OutPeers())
        self.add_component(P2P_BIND_PORT_FIELD, P2PBindPort())
        self.add_component(REMOTE_FIELD, Local())
        
        self.config_file = self.components[CONFIG_FILE_FIELD]
        self.data_dir = self.components[DATA_DIR_FIELD]
        self.in_peers = self.components[IN_PEERS_FIELD]
        self.instance = self.components[INSTANCE_FIELD]
        self.log_level = self.components[LOG_LEVEL_FIELD]
        self.log_name = self.components[LOG_NAME_FIELD]
        self.max_log_files = self.components[MAX_LOG_FILES_FIELD]
        self.max_log_size = self.components[MAX_LOG_SIZE_FIELD]
        self.out_peers = self.components[OUT_PEERS_FIELD]
        self.p2p_bind_port = self.components[P2P_BIND_PORT_FIELD]
        self.remote = self.components[REMOTE_FIELD]

        if rec:
            self.from_rec(rec)

