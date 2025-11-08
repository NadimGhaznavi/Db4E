"""
db4e/recs/monero/XMRig.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0

Everything XMRig
"""

import os
import subprocess


from db4e.recs.monero.LocalMonero import LocalMonero
from db4e.util.Db4ELogger import Db4ELogger
from db4e.constants.DDef import DDef
from db4e.constants.DField import DField
from db4e.constants.DPlaceholder import DPlaceholder
from db4e.constants.DFile import DFile
from db4e.constants.DModule import DModule
from db4e.constants.DElem import DElem
from db4e.constants.DSQL import DCol


class XMRig(LocalMonero):

    def __init__(self, rec=None, log_file=None):
        super().__init__()
        # XMRig Attributes
        self._config_file = ""
        self._log_file = ""
        self._logrotate_config = ""
        self._max_log_files = DDef.MAX_LOG_FILES
        self._max_log_size = DDef.MAX_LOG_SIZE
        self._num_threads = 1
        self._parent = DField.DISABLE
        self._parent_remote = ""
        self._version = DDef.XMRIG_VERSION
        # Set the version
        self.version(DDef.XMRIG_VERSION)
        # Initialize the parent to being disabled
        self.parent(DField.DISABLE)
        # Used to build the upstream P2Pool radioset
        self._instance_map = {}
        # Historical hashrate data
        self._hashrates = {}
        # Current hashrate
        self._hashrate = None
        # Historical share found data
        self._shares_found = None
        # The upstream P2Pool instance
        self.p2pool = None

        if rec:
            self.from_rec(rec)

        if log_file:
            self.log = Db4ELogger(db4e_module=DModule.XMRIG, log_file=log_file)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._config_file = rec[DCol.CONFIG_FILE]
        self._log_file = rec[DCol.LOG_FILE]
        self._logrotate_config = rec[DCol.LOGROTATE_CONFIG]
        self._max_log_files = rec[DCol.MAX_LOG_FILES]
        self._max_log_size = rec[DCol.MAX_LOG_SIZE]
        self._num_threads = rec[DCol.NUM_THREADS]
        self._parent = rec[DCol.PARENT]
        self._parent_remote = rec[DCol.PARENT_REMOTE]
        self._version = rec[DCol.VERSION]

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                DCol.CONFIG_FILE: self._config_file,
                DCol.LOG_FILE: self._log_file,
                DCol.LOGROTATE_CONFIG: self._logrotate_config,
                DCol.MAX_LOG_FILES: self._max_log_files,
                DCol.MAX_LOG_SIZE: self._max_log_size,
                DCol.NUM_THREADS: self._num_threads,
                DCol.PARENT: self._parent,
                DCol.PARENT_REMOTE: self._parent_remote,
                DCol.VERSION: self._version,
            }
        )
        return data

    ## Attribute get/set methods

    def config_file(self, config_file=None):
        if config_file is not None:
            self._config_file = config_file
        return self._config_file

    def log_file(self, log_file=None):
        if log_file is not None:
            self._log_file = log_file
        return self._log_file

    def logrotate_config(self, logrotate_config=None):
        if logrotate_config is not None:
            self._logrotate_config = logrotate_config
        return self._logrotate_config

    def max_log_files(self, max_log_files=None):
        if max_log_files is not None:
            self._max_log_files = max_log_files
        return self._max_log_files

    def max_log_size(self, max_log_size=None):
        if max_log_size is not None:
            self._max_log_size = max_log_size
        return self._max_log_size

    def num_threads(self, num_threads=None):
        if num_threads is not None:
            self._num_threads = num_threads
        return self._num_threads

    def parent(self, parent=None):
        if parent is not None:
            self._parent = parent
        return self._parent

    def parent_remote(self, parent_remote=None):
        if parent_remote is not None:
            self._parent_remote = parent_remote
        return self._parent_remote

    def version(self, version=None):
        if version is not None:
            self._version = version
        return self._version

    # Generate the XMRig startup config file
    def gen_config(self, tmpl_file: str, vendor_dir: str):
        # XMRig configuration file
        fq_config = os.path.join(
            vendor_dir, DElem.XMRIG, DDef.CONF_DIR, self.instance() + DDef.JSON_SUFFIX
        )

        # XMRig log file
        fq_log = os.path.join(
            vendor_dir, DElem.XMRIG, DDef.LOG_DIR, self.instance() + DDef.LOG_SUFFIX
        )

        # Generate a URL:Port field for the config
        url_entry = self.p2pool.ip_addr() + ":" + self.p2pool.stratum_port()

        # Populate the config templace placeholders
        placeholders = {
            DPlaceholder.MINER_NAME: self.instance(),
            DPlaceholder.NUM_THREADS: ",".join(["-1"] * int(self.num_threads())),
            DPlaceholder.URL: url_entry,
            DPlaceholder.LOG_FILE: fq_log,
        }
        with open(tmpl_file, "r") as f:
            config_contents = f.read()
            final_config = config_contents
            for key, val in placeholders.items():
                final_config = final_config.replace(f"[[{key}]]", str(val))

        # Write the config to file
        with open(fq_config, "w") as f:
            f.write(final_config)
        self.config_file(fq_config)

    # Generate the XMRig logrotate configuration
    def gen_logrotate_config(self, tmpl_file: str, vendor_dir: str, db4e_group: str):
        # Logrotate configuration file
        fq_config = os.path.join(
            vendor_dir,
            DDef.LOGROTATE,
            DElem.XMRIG + "-" + self.instance() + DDef.CONF_SUFFIX,
        )

        # Populate the config template placeholders
        placeholders = {
            DPlaceholder.VENDOR_DIR: vendor_dir,
            DPlaceholder.INSTANCE: self.instance(),
            DPlaceholder.MAX_LOG_FILES: self.max_log_files(),
            DPlaceholder.MAX_LOG_SIZE: self.max_log_size(),
            DPlaceholder.DB4E_GROUP: db4e_group,
        }
        with open(tmpl_file, "r") as f:
            config_contents = f.read()
            final_config = config_contents
            for key, val in placeholders.items():
                final_config = final_config.replace(f"[[{key}]]", str(val))

        # Write the config to file
        with open(fq_config, "w") as f:
            f.write(final_config)
        self.logrotate_config(fq_config)

        # XMRig is run as root, so the log files are owned by root, chown the
        # logrotate file to match the permisions (else logrotate will fail).
        try:
            cmd = [DFile.SUDO, DFile.CHOWN, DDef.ROOT, fq_config]
            proc = subprocess.run(cmd, stderr=subprocess.PIPE, input="")
            stderr = proc.stderr.decode("utf-8")

        except Exception as e:
            self.log.critical(f"gen_logrotate_config(): {e} {stderr}")

    # The current hashrate
    def hashrate(self, hashrate=None):
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate

    # Historical hashrate data
    def hashrates(self, hashrate_data=None):
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates

    # Instance map: Used to construct the upstream P2Pool radioset
    def instance_map(self, map=None):
        if map:
            self._instance_map = map
        return self._instance_map

    # Historical share found data
    def shares_found(self, shares_found_data=None):
        if shares_found_data is not None:
            self._shares_found = shares_found_data
        return self._shares_found
