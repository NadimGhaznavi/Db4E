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
import subprocess


from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.Db4ELogger import Db4ELogger

from db4e.Modules.Components import (
    ConfigFile, Enabled, Instance, Local, LogFile, NumThreads, Parent, Version,
    MaxLogFiles, MaxLogSize, LogRotateConfig)

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DDef import DDef
from db4e.Constants.DPlaceholder import DPlaceholder
from db4e.Constants.DFile import DFile
from db4e.Constants.DModule import DModule





class XMRig(SoftwareSystem):
    
    def __init__(self, rec=None, log_file=None):
        super().__init__()
        self._elem_type = DElem.XMRIG
        self.name = DLabel.XMRIG

        self.add_component(DField.CONFIG_FILE, ConfigFile())
        self.add_component(DField.ENABLED, Enabled())
        self.add_component(DField.INSTANCE, Instance())
        self.add_component(DField.LOG_FILE, LogFile())
        self.add_component(DField.LOG_ROTATE_CONFIG, LogRotateConfig())
        self.add_component(DField.MAX_LOG_FILES, MaxLogFiles())
        self.add_component(DField.MAX_LOG_SIZE, MaxLogSize())
        self.add_component(DField.REMOTE, Local())
        self.add_component(DField.NUM_THREADS, NumThreads())
        self.add_component(DField.VERSION, Version())
        self.add_component(DField.PARENT, Parent())

        self.config_file = self.components[DField.CONFIG_FILE]
        self.enabled = self.components[DField.ENABLED]
        self.instance = self.components[DField.INSTANCE]
        self.log_file = self.components[DField.LOG_FILE]
        self.logrotate_config = self.components[DField.LOG_ROTATE_CONFIG]
        self.max_log_files = self.components[DField.MAX_LOG_FILES]
        self.max_log_size = self.components[DField.MAX_LOG_SIZE]
        self.num_threads = self.components[DField.NUM_THREADS]
        self.parent = self.components[DField.PARENT]
        self.version = self.components[DField.VERSION]
        self.version(DDef.XMRIG_VERSION)
        self.parent(DField.DISABLE)
        self._instance_map = {}
        self._hashrates = {}
        self._hashrate = None
        self._uptime = None
        self.p2pool = None

        if rec:
            self.from_rec(rec)

        if log_file:
            self.log = Db4ELogger(db4e_module=DModule.XMRIG, log_file=log_file)
  

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


    def gen_logrotate_config(self, tmpl_file: str, vendor_dir: str, db4e_group:str):
        # Logrotate configuration file
        fq_config = os.path.join(
            vendor_dir, DElem.DB4E, DDef.LOG_ROTATE, DElem.XMRIG + "-" + \
                self.instance() + DDef.CONF_SUFFIX)
        
        # Populate the config template placeholders
        placeholders = {
            DPlaceholder.VENDOR_DIR: vendor_dir,
            DPlaceholder.INSTANCE: self.instance(),
            DPlaceholder.MAX_LOG_FILES: self.max_log_files(),
            DPlaceholder.MAX_LOG_SIZE: self.max_log_size(),
            DPlaceholder.DB4E_GROUP: db4e_group,
        }
        with open(tmpl_file, 'r') as f:
            config_contents = f.read()
            final_config = config_contents
            for key, val in placeholders.items():
                final_config = final_config.replace(f'[[{key}]]', str(val))

        # Write the config to file
        with open(fq_config, 'w') as f:
            f.write(final_config)
        self.logrotate_config(fq_config)

        # XMRig is run as root, so the log files are owned by root, chown the 
        # logrotate file to match the permisions (else logrotate will fail).
        try:
            cmd = [DFile.SUDO, DFile.CHOWN, DDef.ROOT, fq_config]
            proc = subprocess.run(
                cmd, 
                stderr=subprocess.PIPE, 
                input='')
            stderr = proc.stderr.decode('utf-8')
            
        except Exception as e:
            self.log.critical(f"gen_logrotate_config(): {e} {stderr}")


    def hashrate(self, hashrate=None):
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate
    

    def hashrates(self, hashrate_data=None):
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates
    

    def instance_map(self, map=None):
        if map:
            self._instance_map = map
        return self._instance_map
    

    def uptime(self, uptime=None):
        if uptime is not None:
            self._uptime = uptime
        return self._uptime