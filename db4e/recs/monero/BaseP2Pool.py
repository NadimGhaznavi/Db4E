"""
db4e/recs/monero/BaseP2Pool.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Virtual base class for P2Pool and P2PoolInternal.
"""

import os

from db4e.recs.monero.LocalMonero import LocalMonero
from db4e.constants.DSQL import DCol
from db4e.constants.DDef import DDef
from db4e.constants.DElem import DElem
from db4e.constants.DField import DField
from db4e.constants.DPlaceholder import DPlaceholder
from db4e.constants.DLabel import DLabel


CHAIN_TO_CHAIN_LABEL_MAP = {
    DField.MAIN_CHAIN: DLabel.MAIN_CHAIN_LONG,
    DField.MINI_CHAIN: DLabel.MINI_CHAIN_LONG,
    DField.NANO_CHAIN: DLabel.NANO_CHAIN_LONG,
}


class BaseP2Pool(LocalMonero):
    """
    Base record for P2Pool configurations and runtime metadata.
    """

    def __init__(self, rec=None):
        """
        Initialize the P2Pool base record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__()
        # P2Pool attributes
        self._any_ip = ""
        self._chain = ""
        self._config_file = ""
        self._in_peers = DDef.IN_PEERS
        self._ip_addr = ""
        self._log_file = ""
        self._log_level = ""
        self._logrotate_config = ""
        self._max_log_files = DDef.MAX_LOG_FILES
        self._max_log_size = DDef.MAX_LOG_SIZE
        self._log_level = DDef.LOG_LEVEL
        self._out_peers = DDef.OUT_PEERS
        self._p2p_port = DDef.P2P_PORT
        self._parent = DField.DISABLE
        self._parent_remote = DField.DISABLE
        self._stdin_path = ""
        self._stratum_port = DDef.STRATUM_PORT
        self._user_wallet = ""
        self._version = DDef.P2POOL_VERSION
        # Set the version
        self.version(DDef.P2POOL_VERSION)
        # Used to construct the Monero radioset
        self._instance_map = {}
        # An instance of the upstream Monero daemon
        self.monerod = None
        # A foreign key to the upstream Monero daemon
        self.parent(DField.DISABLE)
        # Historical pool hashrate data
        self._hashrates = None
        # Current pool hashrate
        self._hashrate = None

        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        """
        Populate the object from a database record.

        :param rec: Database record mapping.
        :type rec: dict
        :return: None
        :rtype: None
        """
        super().from_rec(rec)
        self._any_ip = rec[DCol.ANY_IP]
        self._chain = rec[DCol.CHAIN]
        self._config_file = rec[DCol.CONFIG_FILE]
        self._in_peers = rec[DCol.IN_PEERS]
        self._ip_addr = rec[DCol.IP_ADDR]
        self._log_file = rec[DCol.LOG_FILE]
        self._log_level = rec[DCol.LOG_LEVEL]
        self._logrotate_config = rec[DCol.LOGROTATE_CONFIG]
        self._max_log_files = rec[DCol.MAX_LOG_FILES]
        self._max_log_size = rec[DCol.MAX_LOG_SIZE]
        self._out_peers = rec[DCol.OUT_PEERS]
        self._p2p_port = rec[DCol.P2P_PORT]
        self._parent = rec[DCol.PARENT]
        self._parent_remote = rec[DCol.PARENT_REMOTE]
        self._stdin_path = rec[DCol.STDIN_PATH]
        self._stratum_port = rec[DCol.STRATUM_PORT]
        self._user_wallet = rec[DCol.USER_WALLET]
        self._version = rec[DCol.VERSION]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with P2Pool fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.ANY_IP: self._any_ip,
                DCol.CHAIN: self._chain,
                DCol.CONFIG_FILE: self._config_file,
                DCol.IN_PEERS: self._in_peers,
                DCol.IP_ADDR: self._ip_addr,
                DCol.LOG_FILE: self._log_file,
                DCol.LOG_LEVEL: self._log_level,
                DCol.LOGROTATE_CONFIG: self._logrotate_config,
                DCol.MAX_LOG_FILES: self._max_log_files,
                DCol.MAX_LOG_SIZE: self._max_log_size,
                DCol.OUT_PEERS: self._out_peers,
                DCol.P2P_PORT: self._p2p_port,
                DCol.PARENT: self._parent,
                DCol.PARENT_REMOTE: self._parent_remote,
                DCol.STDIN_PATH: self._stdin_path,
                DCol.STRATUM_PORT: self._stratum_port,
                DCol.USER_WALLET: self._user_wallet,
                DCol.VERSION: self._version,
            }
        )
        return data

    ## Attribute get/set methods

    def any_ip(self, any_ip=None):
        """
        Get or set the bind address.

        :param any_ip: Optional IP address to set.
        :type any_ip: str or None
        :return: Current bind address.
        :rtype: str
        """
        if any_ip is not None:
            self._any_ip = any_ip
        return self._any_ip

    def chain(self, chain=None):
        """
        Get or set the chain identifier.

        :param chain: Optional chain value to set.
        :type chain: str or None
        :return: Current chain identifier.
        :rtype: str
        """
        if chain is not None:
            self._chain = chain
        return self._chain

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

    def in_peers(self, in_peers=None):
        """
        Get or set the inbound peer limit.

        :param in_peers: Optional inbound peer count to set.
        :type in_peers: int or None
        :return: Current inbound peer count.
        :rtype: int
        """
        if in_peers is not None:
            self._in_peers = int(in_peers)
        return self._in_peers

    def ip_addr(self, ip_addr=None):
        """
        Get or set the listening IP address.

        :param ip_addr: Optional IP address to set.
        :type ip_addr: str or None
        :return: Current listening IP address.
        :rtype: str
        """
        if ip_addr is not None:
            self._ip_addr = ip_addr
        return self._ip_addr

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

    def log_level(self, log_level=None):
        """
        Get or set the log verbosity level.

        :param log_level: Optional log level to set.
        :type log_level: int or None
        :return: Current log level.
        :rtype: int
        """
        if log_level is not None:
            self._log_level = int(log_level)
        return self._log_level

    def out_peers(self, out_peers=None):
        """
        Get or set the outbound peer limit.

        :param out_peers: Optional outbound peer count to set.
        :type out_peers: int or None
        :return: Current outbound peer count.
        :rtype: int
        """
        if out_peers is not None:
            self._out_peers = int(out_peers)
        return self._out_peers

    def p2p_port(self, p2p_port=None):
        """
        Get or set the P2P port.

        :param p2p_port: Optional port to set.
        :type p2p_port: int or None
        :return: Current P2P port.
        :rtype: int
        """
        if p2p_port is not None:
            self._p2p_port = int(p2p_port)
        return self._p2p_port

    def parent(self, parent=None):
        """
        Get or set the upstream Monero daemon ID.

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

    def stdin_path(self, stdin_path=None):
        """
        Get or set the stdin pipe path.

        :param stdin_path: Optional stdin path to set.
        :type stdin_path: str or None
        :return: Current stdin path.
        :rtype: str
        """
        if stdin_path is not None:
            self._stdin_path = stdin_path
        return self._stdin_path

    def stratum_port(self, stratum_port=None):
        """
        Get or set the stratum port.

        :param stratum_port: Optional port to set.
        :type stratum_port: int or None
        :return: Current stratum port.
        :rtype: int
        """
        if stratum_port is not None:
            self._stratum_port = int(stratum_port)
        return self._stratum_port

    def user_wallet(self, user_wallet=None):
        """
        Get or set the user wallet address.

        :param user_wallet: Optional wallet address to set.
        :type user_wallet: str or None
        :return: Current wallet address.
        :rtype: str
        """
        if user_wallet is not None:
            self._user_wallet = user_wallet
        return self._user_wallet

    def version(self, version=None):
        """
        Get or set the P2Pool version string.

        :param version: Optional version string to set.
        :type version: str or None
        :return: Current version string.
        :rtype: str
        """
        if version is not None:
            self._version = str(version)
        return self._version

    # Generate the P2Pool startup config file
    def gen_config(self, tmpl_file: str, vendor_dir: str):
        """
        Generate a P2Pool config file from a template.

        :param tmpl_file: Template file path.
        :type tmpl_file: str
        :param vendor_dir: Vendor directory root.
        :type vendor_dir: str
        :return: None
        :rtype: None
        """

        p2pool_dir = os.path.join(vendor_dir, DElem.P2POOL)
        api_dir = os.path.join(p2pool_dir, self.instance(), DDef.API_DIR)
        run_dir = os.path.join(p2pool_dir, self.instance(), DDef.RUN_DIR)
        log_dir = os.path.join(p2pool_dir, self.instance(), DDef.LOG_DIR)

        fq_config = os.path.join(
            p2pool_dir, DDef.CONF_DIR, self.instance() + DDef.INI_SUFFIX
        )

        # Monero settings
        monerod_ip = self.monerod.ip_addr()
        monerod_zmq_port = self.monerod.zmq_pub_port()
        monerod_rpc_port = self.monerod.rpc_bind_port()

        # Populate the config templace placeholders
        placeholders = {
            DPlaceholder.WALLET: self.user_wallet(),
            DPlaceholder.P2P_DIR: p2pool_dir,
            DPlaceholder.MONEROD_IP: monerod_ip,
            DPlaceholder.ZMQ_PUB_PORT: monerod_zmq_port,
            DPlaceholder.RPC_BIND_PORT: monerod_rpc_port,
            DPlaceholder.LOG_LEVEL: self.log_level(),
            DPlaceholder.P2P_PORT: self.p2p_port(),
            DPlaceholder.STRATUM_PORT: self.stratum_port(),
            DPlaceholder.IN_PEERS: self.in_peers(),
            DPlaceholder.OUT_PEERS: self.out_peers(),
            DPlaceholder.CHAIN: self.chain(),
            DPlaceholder.ANY_IP: self.any_ip(),
            DPlaceholder.API_DIR: api_dir,
            DPlaceholder.RUN_DIR: run_dir,
            DPlaceholder.LOG_DIR: log_dir,
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

    # Generate the P2Pool logrotate configuration
    def gen_logrotate_config(self, tmpl_file: str, vendor_dir: str, db4e_group: str):
        """
        Generate a P2Pool logrotate configuration file.

        :param tmpl_file: Template file path.
        :type tmpl_file: str
        :param vendor_dir: Vendor directory root.
        :type vendor_dir: str
        :param db4e_group: Db4E group name for permissions.
        :type db4e_group: str
        :return: None
        :rtype: None
        """
        # Logrotate configuration file
        fq_config = os.path.join(
            vendor_dir,
            DDef.LOGROTATE,
            DElem.P2POOL + "-" + self.instance() + DDef.CONF_SUFFIX,
        )

        # Populate the config template
        placeholders = {
            DPlaceholder.VENDOR_DIR: vendor_dir,
            DPlaceholder.INSTANCE: self.instance(),
            DPlaceholder.MAX_LOG_FILES: self.max_log_files(),
            DPlaceholder.MAX_LOG_SIZE: self.max_log_size(),
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

    # The current pool hashrate
    def hashrate(self, hashrate=None):
        """
        Get or set the current pool hashrate.

        :param hashrate: Optional hashrate value to set.
        :type hashrate: int or None
        :return: Current hashrate value.
        :rtype: int or None
        """
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate

    # Historical pool hashrate data
    def hashrates(self, hashrate_data=None):
        """
        Get or set historical pool hashrate data.

        :param hashrate_data: Optional historical data to set.
        :type hashrate_data: list or dict or None
        :return: Historical hashrate data.
        :rtype: list or dict or None
        """
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates

    # Instance map: Used to construct the upstream Monero daemon radioset
    def instance_map(self, map=None):
        """
        Get or set the instance map for radioset construction.

        :param map: Optional instance map to set.
        :type map: dict or None
        :return: Current instance map.
        :rtype: dict
        """
        if map is not None:
            self._instance_map = map
        return self._instance_map

    # Historical share found data
    def shares_found(self, shares_found=None):
        """
        Get or set historical share found data.

        :param shares_found: Optional historical data to set.
        :type shares_found: list or dict or None
        :return: Historical share found data.
        :rtype: list or dict or None
        """
        if shares_found is not None:
            self._shares_found = shares_found
        return self._shares_found
