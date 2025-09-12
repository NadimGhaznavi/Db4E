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
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DDef import DDef
from db4e.Constants.DPlaceholder import DPlaceholder

from db4e.Modules.Components import (
    ConfigFile, Instance, Local, LogFile, NumThreads, Parent, Version)


class XMRig(LocalSoftwareSystem):
    
    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = DElem.XMRIG
        self.name = DLabel.XMRIG

        self.add_component(DField.CONFIG_FILE, ConfigFile())
        self.add_component(DField.INSTANCE, Instance())
        self.add_component(DField.LOG_FILE, LogFile())
        self.add_component(DField.REMOTE, Local())
        self.add_component(DField.NUM_THREADS, NumThreads())
        self.add_component(DField.VERSION, Version())
        self.add_component(DField.PARENT, Parent())

        self.config_file = self.components[DField.CONFIG_FILE]
        self.instance = self.components[DField.INSTANCE]
        self.log_file = self.components[DField.LOG_FILE]
        self.num_threads = self.components[DField.NUM_THREADS]
        self.parent = self.components[DField.PARENT]
        self.version = self.components[DField.VERSION]
        self.version(DDef.XMRIG_VERSION)
        self._instance_map = {}
        self.p2pool = None

        if rec:
            self.from_rec(rec)
  

    def gen_config(self, tmpl_file: str, vendor_dir: str):
        # XMRig configuration file
        fq_config = os.path.join(
            vendor_dir, DElem.XMRIG, DDef.CONF_DIR, self.instance() + DDef.JSON_SUFFIX)
        
        # XMRig log file
        fq_log = os.path.join(
            vendor_dir, DElem.XMRIG, DDef.LOG_DIR, self.instance() + DDef.LOG_SUFFIX)

        # Generate a URL:Port field for the config
        url_entry = self.p2pool.ip_addr()  + ':' + self.p2pool.stratum_port()

        # Populate the config templace placeholders
        placeholders = {
            DPlaceholder.MINER_NAME: self.instance(),
            DPlaceholder.NUM_THREADS: ','.join(['-1'] * int(self.num_threads())),
            DPlaceholder.URL: url_entry,
            DPlaceholder.LOG_FILE: fq_log,
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
    

    def instance_map(self, map=None):
        if map:
            self._instance_map = map
        return self._instance_map