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
from db4e.constants.DStatus import DStatus


class BaseP2Pool(LocalMonero):

    def __init__(self, rec=None):
        super().__init__()
        # P2Pool attributes
        self._any_ip = None
        self._chain = None
        self._config_file = None
        self._in_peers = None
        self._ip_addr = None
        self._log_file = None
        self._logrotate_config = None
        self._max_log_files = None
        self._max_log_size = None
        self._log_level = None
        self._out_peers = None
        self._p2p_port = None
        self._parent = None
        self._stdin_path = None
        self._stratum_port = None
        self._user_wallet = None
        self._version = None
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
        # The health of the deployed instance
        self._status = DStatus.UNKNOWN

        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._any_ip = rec[DCol.ANY_IP]
        self._chain = rec[DCol.CHAIN]
        self._config_file = rec[DCol.CONFIG_FILE]
        self._in_peers = rec[DCol.IN_PEERS]
        self._ip_addr = rec[DCol.IP_ADDR]
        self._log_file = rec[DCol.LOG_FILE]
        self._logrotate_config = rec[DCol.LOGROTATE_CONFIG]
        self._max_log_files = rec[DCol.MAX_LOG_FILES]
        self._max_log_size = rec[DCol.MAX_LOG_SIZE]
        self._log_level = rec[DCol.LOG_LEVEL]
        self._out_peers = rec[DCol.OUT_PEERS]
        self._p2p_port = rec[DCol.P2P_PORT]
        self._parent = rec[DCol.PARENT]
        self._stdin_path = rec[DCol.STDIN_PATH]
        self._stratum_port = rec[DCol.STRATUM_PORT]
        self._user_wallet = rec[DCol.USER_WALLET]
        self._version = rec[DCol.VERSION]

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                DCol.ANY_IP: self._any_ip,
                DCol.CHAIN: self._chain,
                DCol.CONFIG_FILE: self._config_file,
                DCol.IN_PEERS: self._in_peers,
                DCol.IP_ADDR: self._ip_addr,
                DCol.LOG_FILE: self._log_file,
                DCol.LOGROTATE_CONFIG: self._logrotate_config,
                DCol.MAX_LOG_FILES: self._max_log_files,
                DCol.MAX_LOG_SIZE: self._max_log_size,
                DCol.LOG_LEVEL: self._log_level,
                DCol.OUT_PEERS: self._out_peers,
                DCol.P2P_PORT: self._p2p_port,
                DCol.PARENT: self._parent,
                DCol.STDIN_PATH: self._stdin_path,
                DCol.STRATUM_PORT: self._stratum_port,
                DCol.USER_WALLET: self._user_wallet,
                DCol.VERSION: self._version,
            }
        )
        return data

    ## Attribute get/set methods

    def any_ip(self, any_ip=None):
        if any_ip is not None:
            self._any_ip = any_ip
        return self._any_ip

    def chain(self, chain=None):
        if chain is not None:
            self._chain = chain
        return self._chain

    def config_file(self, config_file=None):
        if config_file is not None:
            self._config_file = config_file
        return self._config_file

    def in_peers(self, in_peers=None):
        if in_peers is not None:
            self._in_peers = in_peers
        return self._in_peers

    def ip_addr(self, ip_addr=None):
        if ip_addr is not None:
            self._ip_addr = ip_addr
        return self._ip_addr

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

    def log_level(self, log_level=None):
        if log_level is not None:
            self._log_level = log_level
        return self._log_level

    def out_peers(self, out_peers=None):
        if out_peers is not None:
            self._out_peers = out_peers
        return self._out_peers

    def p2p_port(self, p2p_port=None):
        if p2p_port is not None:
            self._p2p_port = p2p_port
        return self._p2p_port

    def parent(self, parent=None):
        if parent is not None:
            self._parent = parent
        return self._parent

    def stdin_path(self, stdin_path=None):
        if stdin_path is not None:
            self._stdin_path = stdin_path
        return self._stdin_path

    def stratum_port(self, stratum_port=None):
        if stratum_port is not None:
            self._stratum_port = stratum_port
        return self._stratum_port

    def user_wallet(self, user_wallet=None):
        if user_wallet is not None:
            self._user_wallet = user_wallet
        return self._user_wallet

    def version(self, version=None):
        if version is not None:
            self._version = version
        return self._version

    # Generate the P2Pool startup config file
    def gen_config(self, tmpl_file: str, vendor_dir: str):

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
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate

    # Historical pool hashrate data
    def hashrates(self, hashrate_data=None):
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates

    # Instance map: Used to construct the upstream Monero daemon radioset
    def instance_map(self, map=None):
        if map is not None:
            self._instance_map = map
        return self._instance_map

    # Historical share found data
    def shares_found(self, shares_found=None):
        if shares_found is not None:
            self._shares_found = shares_found
        return self._shares_found

    # The health of the deployed instance
    def status(self, status=None):
        if status is not None:
            self._status = status
        return self._status
