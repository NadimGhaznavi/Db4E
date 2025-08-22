"""
db4e/Modules/XMRig.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything XMRig
"""

import os
from copy import deepcopy


from db4e.Modules.LocalSoftwareSystem import LocalSoftwareSystem
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Constants.Fields import (XMRIG_FIELD, REMOTE_FIELD, CONFIG_FILE_FIELD, 
    INSTANCE_FIELD, NUM_THREADS_FIELD, VERSION_FIELD, PARENT_FIELD)
from db4e.Constants.Defaults import (CONF_DIR_DEFAULT, XMRIG_VERSION_DEFAULT)
from db4e.Constants.Labels import XMRIG_LABEL
from db4e.Modules.Components import (
    ConfigFile, Instance, Local, NumThreads, Parent, Version)


class XMRig(LocalSoftwareSystem):
    
    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = XMRIG_FIELD
        self.name = XMRIG_LABEL

        self.add_component(CONFIG_FILE_FIELD, ConfigFile())
        self.add_component(INSTANCE_FIELD, Instance())
        self.add_component(REMOTE_FIELD, Local())
        self.add_component(NUM_THREADS_FIELD, NumThreads())
        self.add_component(VERSION_FIELD, Version())
        self.add_component(PARENT_FIELD, Parent())

        self.config_file = self.components[CONFIG_FILE_FIELD]
        self.instance = self.components[INSTANCE_FIELD]
        self.num_threads = self.components[NUM_THREADS_FIELD]
        self.parent = self.components[PARENT_FIELD]
        self.version = self.components[VERSION_FIELD]
        self.version.value = XMRIG_VERSION_DEFAULT
        self._instance_map = {}
        self.p2pool = None

        if rec:
            self.from_rec(rec)
  

    def gen_config(self, tmpl_file: str, vendor_dir: str):
        # Generate a XMRig configuration file

        fq_config = os.path.join(
            vendor_dir, XMRIG_FIELD, CONF_DIR_DEFAULT, self.instance.value + '.json')

        # Generate a URL:Port field for the config
        url_entry = self.p2pool.ip_addr()  + ':' + self.p2pool.stratum_port()

        # Populate the config templace placeholders
        placeholders = {
            'MINER_NAME': self.instance(),
            'NUM_THREADS': ','.join(['-1'] * int(self.num_threads())),
            'URL': url_entry
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