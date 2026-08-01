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
    """
    Record for a locally managed XMRig miner and its configuration.
    """

    def __init__(self, rec=None, log_file=None):
        """
        Initialize the XMRig record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :param log_file: Optional log file path for logger initialization.
        :type log_file: str or None
        :return: None
        :rtype: None
        """
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
        # HTTP port
        self._http_port = None
        # Historical share found data
        self._shares_found = None
        # The upstream P2Pool instance
        self.p2pool = None

        if rec:
            self.from_rec(rec)

        if log_file:
            self.log = Db4ELogger(db4e_module=DModule.XMRIG, log_file=log_file)

    def from_rec(self, rec):
        """
        Populate the object from a database record.

        :param rec: Database record mapping.
        :type rec: dict
        :return: None
        :rtype: None
        """
        super().from_rec(rec)
        self._config_file = rec[DCol.CONFIG_FILE]
        self._http_port = rec[DCol.HTTP_PORT]
        self._log_file = rec[DCol.LOG_FILE]
        self._logrotate_config = rec[DCol.LOGROTATE_CONFIG]
        self._max_log_files = rec[DCol.MAX_LOG_FILES]
        self._max_log_size = rec[DCol.MAX_LOG_SIZE]
        self._num_threads = rec[DCol.NUM_THREADS]
        self._parent = rec[DCol.PARENT]
        self._parent_remote = rec[DCol.PARENT_REMOTE]
        self._version = rec[DCol.VERSION]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with XMRig fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.CONFIG_FILE: self._config_file,
                DCol.HTTP_PORT: self._http_port,
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
        """
        Get or set the config file path.

        :param config_file: Optional config file path to set.
        :type config_file: str or None
        :return: Current config file path.
        :rtype: str
        """
        if config_file is not None:
            self._config_file = config_file
        return self._config_file

    def http_port(self, port=None):
        if port is not None:
            self._http_port = port
        return self._http_port

    def log_file(self, log_file=None):
        """
        Get or set the log file path.

        :param log_file: Optional log file path to set.
        :type log_file: str or None
        :return: Current log file path.
        :rtype: str
        """
        if log_file is not None:
            self._log_file = log_file
        return self._log_file

    def logrotate_config(self, logrotate_config=None):
        """
        Get or set the logrotate config file path.

        :param logrotate_config: Optional config file path to set.
        :type logrotate_config: str or None
        :return: Current logrotate config path.
        :rtype: str
        """
        if logrotate_config is not None:
            self._logrotate_config = logrotate_config
        return self._logrotate_config

    def max_log_files(self, max_log_files=None):
        """
        Get or set the maximum number of log files to retain.

        :param max_log_files: Optional max log file count to set.
        :type max_log_files: int or None
        :return: Current max log file count.
        :rtype: int
        """
        if max_log_files is not None:
            self._max_log_files = int(max_log_files)
        return self._max_log_files

    def max_log_size(self, max_log_size=None):
        """
        Get or set the maximum log file size.

        :param max_log_size: Optional max log size to set.
        :type max_log_size: int or None
        :return: Current max log size.
        :rtype: int
        """
        if max_log_size is not None:
            self._max_log_size = int(max_log_size)
        return self._max_log_size

    def num_threads(self, num_threads=None):
        """
        Get or set the number of mining threads.

        :param num_threads: Optional thread count to set.
        :type num_threads: int or None
        :return: Current thread count.
        :rtype: int
        """
        if num_threads is not None:
            self._num_threads = int(num_threads)
        return self._num_threads

    def parent(self, parent=None):
        """
        Get or set the upstream P2Pool ID.

        :param parent: Optional parent ID to set.
        :type parent: int or None
        :return: Current parent ID.
        :rtype: int
        """
        if parent is not None:
            self._parent = int(parent)
        return self._parent

    def parent_remote(self, parent_remote=None):
        """
        Get or set the remote parent flag or ID.

        :param parent_remote: Optional remote parent value to set.
        :type parent_remote: int or None
        :return: Current remote parent value.
        :rtype: int
        """
        if parent_remote is not None:
            self._parent_remote = int(parent_remote)
        return self._parent_remote

    def version(self, version=None):
        """
        Get or set the XMRig version string.

        :param version: Optional version string to set.
        :type version: str or None
        :return: Current version string.
        :rtype: str
        """
        if version is not None:
            self._version = str(version)
        return self._version

    # Generate the XMRig startup config file
    def gen_config(self, tmpl_file: str):
        """
        Generate an XMRig config file from a template.

        :param tmpl_file: Template file path.
        :type tmpl_file: str
        :return: None
        :rtype: None
        """
        # XMRig configuration file
        fq_config = os.path.join(
            DDef.DB4E_INSTALL_DIR,
            DElem.XMRIG,
            DDef.CONF_DIR,
            self.instance() + DDef.JSON_SUFFIX,
        )

        # XMRig log file
        fq_log = os.path.join(
            DDef.DB4E_INSTALL_DIR,
            DElem.XMRIG,
            DDef.LOG_DIR,
            self.instance() + DDef.LOG_SUFFIX,
        )

        # Generate a URL:Port field for the config
        url_entry = self.p2pool.ip_addr() + ":" + str(self.p2pool.stratum_port())

        # Populate the config templace placeholders
        placeholders = {
            DPlaceholder.HTTP_PORT: self.http_port(),
            DPlaceholder.MINER_NAME: self.instance(),
            DPlaceholder.NUM_THREADS: ",".join(["-1"] * int(self.num_threads())),
            DPlaceholder.URL: url_entry,
            DPlaceholder.LOG_FILE: fq_log,
        }
        DIV = DDef.XMRIG_DIV
        with open(tmpl_file, "r") as f:
            config_contents = f.read()
            final_config = config_contents
            for key, val in placeholders.items():
                final_config = final_config.replace(f"{DIV}{key}{DIV}", str(val))

        # Write the config to file
        with open(fq_config, "w") as f:
            f.write(final_config)
        self.config_file(fq_config)

    # Generate the XMRig logrotate configuration
    def gen_logrotate_config(self, tmpl_file: str):
        """
        Generate an XMRig logrotate configuration file.

        :param tmpl_file: Template file path.
        :type tmpl_file: str
        :param db4e_group: Db4E group name for permissions.
        :type db4e_group: str
        :return: None
        :rtype: None
        """
        # Logrotate configuration file
        fq_config = os.path.join(
            DDef.DB4E_INSTALL_DIR,
            DDef.LOGROTATE,
            DElem.XMRIG + "-" + self.instance() + DDef.CONF_SUFFIX,
        )

        # Populate the config template placeholders
        placeholders = {
            DPlaceholder.VENDOR_DIR: DDef.DB4E_INSTALL_DIR,
            DPlaceholder.INSTANCE: self.instance(),
            DPlaceholder.MAX_LOG_FILES: self.max_log_files(),
            DPlaceholder.MAX_LOG_SIZE: self.max_log_size(),
            DPlaceholder.DB4E_GROUP: DDef.DB4E_GROUP,
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
        """
        Get or set the current miner hashrate.

        :param hashrate: Optional hashrate value to set.
        :type hashrate: int or None
        :return: Current hashrate value.
        :rtype: int or None
        """
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate

    # Historical hashrate data
    def hashrates(self, hashrate_data=None):
        """
        Get or set historical miner hashrate data.

        :param hashrate_data: Optional historical data to set.
        :type hashrate_data: list or dict or None
        :return: Historical hashrate data.
        :rtype: list or dict or None
        """
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates

    # Instance map: Used to construct the upstream P2Pool radioset
    def instance_map(self, map=None):
        """
        Get or set the instance map for radioset construction.

        :param map: Optional instance map to set.
        :type map: dict or None
        :return: Current instance map.
        :rtype: dict
        """
        if map:
            self._instance_map = map
        return self._instance_map

    # Historical share found data
    def shares_found(self, shares_found_data=None):
        """
        Get or set historical share found data.

        :param shares_found_data: Optional historical data to set.
        :type shares_found_data: list or dict or None
        :return: Historical share found data.
        :rtype: list or dict or None
        """
        if shares_found_data is not None:
            self._shares_found = shares_found_data
        return self._shares_found
