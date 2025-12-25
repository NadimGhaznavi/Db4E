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

from db4e.recs.monero.LocalMonero import LocalMonero
from db4e.constants.DSQL import DCol
from db4e.constants.DDef import DDef
from db4e.constants.DElem import DElem
from db4e.constants.DPlaceholder import DPlaceholder


class MoneroD(LocalMonero):
    """
    Record for a locally managed Monero daemon and its configuration.
    """

    def __init__(self, rec=None):
        """
        Initialize the MoneroD record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__()
        self._any_ip = DDef.ANY_IP
        self._blockchain_dir = ""
        self._config_file = ""
        self._in_peers = DDef.IN_PEERS
        self._ip_addr = ""
        self._log_file = ""
        self._log_level = DDef.LOG_LEVEL
        self._max_log_files = DDef.MAX_LOG_FILES
        self._max_log_size = DDef.MAX_LOG_SIZE
        self._out_peers = DDef.OUT_PEERS
        self._p2p_bind_port = DDef.P2P_BIND_PORT
        self._priority_node_1 = DDef.PRIORITY_NODE_1
        self._priority_node_2 = DDef.PRIORITY_NODE_2
        self._priority_port_1 = DDef.P2P_BIND_PORT
        self._priority_port_2 = DDef.P2P_BIND_PORT
        self._rpc_bind_port = DDef.RPC_BIND_PORT
        self._show_time_stats = DDef.SHOW_TIME_STATS
        self._stdin_path = ""
        self._version = DDef.MONEROD_VERSION
        self._zmq_pub_port = DDef.ZMQ_PUB_PORT
        self._zmq_rpc_port = DDef.ZMQ_RPC_PORT
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
        self._blockchain_dir = rec[DCol.BLOCKCHAIN_DIR]
        self._config_file = rec[DCol.CONFIG_FILE]
        self._in_peers = rec[DCol.IN_PEERS]
        self._ip_addr = rec[DCol.IP_ADDR]
        self._log_level = rec[DCol.LOG_LEVEL]
        self._log_file = rec[DCol.LOG_FILE]
        self._max_log_files = rec[DCol.MAX_LOG_FILES]
        self._max_log_size = rec[DCol.MAX_LOG_SIZE]
        self._out_peers = rec[DCol.OUT_PEERS]
        self._p2p_bind_port = rec[DCol.P2P_BIND_PORT]
        self._priority_node_1 = rec[DCol.PRIORITY_NODE_1]
        self._priority_port_1 = rec[DCol.PRIORITY_PORT_1]
        self._priority_node_2 = rec[DCol.PRIORITY_NODE_2]
        self._priority_port_2 = rec[DCol.PRIORITY_PORT_2]
        self._rpc_bind_port = rec[DCol.RPC_BIND_PORT]
        self._show_time_stats = rec[DCol.SHOW_TIME_STATS]
        self._stdin_path = rec[DCol.STDIN_PATH]
        self._version = rec[DCol.VERSION]
        self._zmq_pub_port = rec[DCol.ZMQ_PUB_PORT]
        self._zmq_rpc_port = rec[DCol.ZMQ_RPC_PORT]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with Monero daemon fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.ANY_IP: self._any_ip,
                DCol.BLOCKCHAIN_DIR: self._blockchain_dir,
                DCol.CONFIG_FILE: self._config_file,
                DCol.IN_PEERS: self._in_peers,
                DCol.IP_ADDR: self._ip_addr,
                DCol.LOG_LEVEL: self._log_level,
                DCol.LOG_FILE: self._log_file,
                DCol.MAX_LOG_FILES: self._max_log_files,
                DCol.MAX_LOG_SIZE: self._max_log_size,
                DCol.OUT_PEERS: self._out_peers,
                DCol.P2P_BIND_PORT: self._p2p_bind_port,
                DCol.PRIORITY_NODE_1: self._priority_node_1,
                DCol.PRIORITY_PORT_1: self._priority_port_1,
                DCol.PRIORITY_NODE_2: self._priority_node_2,
                DCol.PRIORITY_PORT_2: self._priority_port_2,
                DCol.RPC_BIND_PORT: self._rpc_bind_port,
                DCol.SHOW_TIME_STATS: self._show_time_stats,
                DCol.STDIN_PATH: self._stdin_path,
                DCol.VERSION: self._version,
                DCol.ZMQ_PUB_PORT: self._zmq_pub_port,
                DCol.ZMQ_RPC_PORT: self._zmq_rpc_port,
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

    def blockchain_dir(self, blockchain_dir=None):
        """
        Get or set the blockchain directory.

        :param blockchain_dir: Optional directory path to set.
        :type blockchain_dir: str or None
        :return: Current blockchain directory.
        :rtype: str
        """
        if blockchain_dir is not None:
            self._blockchain_dir = blockchain_dir
        return self._blockchain_dir

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

    def p2p_bind_port(self, p2p_bind_port=None):
        """
        Get or set the P2P bind port.

        :param p2p_bind_port: Optional port to set.
        :type p2p_bind_port: int or None
        :return: Current P2P bind port.
        :rtype: int
        """
        if p2p_bind_port is not None:
            self._p2p_bind_port = int(p2p_bind_port)
        return self._p2p_bind_port

    def priority_node_1(self, priority_node_1=None):
        """
        Get or set the first priority node host.

        :param priority_node_1: Optional node host to set.
        :type priority_node_1: str or None
        :return: Current first priority node host.
        :rtype: str
        """
        if priority_node_1 is not None:
            self._priority_node_1 = priority_node_1
        return self._priority_node_1

    def priority_port_1(self, priority_port_1=None):
        """
        Get or set the first priority node port.

        :param priority_port_1: Optional port to set.
        :type priority_port_1: int or None
        :return: Current first priority node port.
        :rtype: int
        """
        if priority_port_1 is not None:
            self._priority_port_1 = int(priority_port_1)
        return self._priority_port_1

    def priority_node_2(self, priority_node_2=None):
        """
        Get or set the second priority node host.

        :param priority_node_2: Optional node host to set.
        :type priority_node_2: str or None
        :return: Current second priority node host.
        :rtype: str
        """
        if priority_node_2 is not None:
            self._priority_node_2 = priority_node_2
        return self._priority_node_2

    def priority_port_2(self, priority_port_2=None):
        """
        Get or set the second priority node port.

        :param priority_port_2: Optional port to set.
        :type priority_port_2: int or None
        :return: Current second priority node port.
        :rtype: int
        """
        if priority_port_2 is not None:
            self._priority_port_2 = int(priority_port_2)
        return self._priority_port_2

    def rpc_bind_port(self, rpc_bind_port=None):
        """
        Get or set the RPC bind port.

        :param rpc_bind_port: Optional port to set.
        :type rpc_bind_port: int or None
        :return: Current RPC bind port.
        :rtype: int
        """
        if rpc_bind_port is not None:
            self._rpc_bind_port = int(rpc_bind_port)
        return self._rpc_bind_port

    def show_time_stats(self, show_time_stats=None):
        """
        Get or set the show-time-stats flag.

        :param show_time_stats: Optional flag value to set.
        :type show_time_stats: int or None
        :return: Current show-time-stats flag.
        :rtype: int
        """
        if show_time_stats is not None:
            self._show_time_stats = int(show_time_stats)
        return self._show_time_stats

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

    def version(self, version=None):
        """
        Get or set the Monero daemon version string.

        :param version: Optional version string to set.
        :type version: str or None
        :return: Current version string.
        :rtype: str
        """
        if version is not None:
            self._version = str(version)
        return self._version

    def zmq_pub_port(self, zmq_pub_port=None):
        """
        Get or set the ZMQ publish port.

        :param zmq_pub_port: Optional port to set.
        :type zmq_pub_port: int or None
        :return: Current ZMQ publish port.
        :rtype: int
        """
        if zmq_pub_port is not None:
            self._zmq_pub_port = int(zmq_pub_port)
        return self._zmq_pub_port

    def zmq_rpc_port(self, zmq_rpc_port=None):
        """
        Get or set the ZMQ RPC port.

        :param zmq_rpc_port: Optional port to set.
        :type zmq_rpc_port: int or None
        :return: Current ZMQ RPC port.
        :rtype: int
        """
        if zmq_rpc_port is not None:
            self._zmq_rpc_port = int(zmq_rpc_port)
        return self._zmq_rpc_port

    # Generate the startup config file
    def gen_config(self, tmpl_file: str, vendor_dir: str):
        """
        Generate a Monero daemon config file from a template.

        :param tmpl_file: Template file path.
        :type tmpl_file: str
        :param vendor_dir: Vendor directory root.
        :type vendor_dir: str
        :return: None
        :rtype: None
        """
        # Generate a Monero Daemon configuration file
        monerod_dir = os.path.join(vendor_dir, DElem.MONEROD)
        fq_config = os.path.join(
            monerod_dir, DDef.CONF_DIR, self.instance() + DDef.INI_SUFFIX
        )

        # Monerod log file
        fq_log = os.path.join(
            vendor_dir,
            DElem.MONEROD,
            self.instance(),
            DDef.LOG_DIR,
            DDef.MONEROD_LOG_FILE,
        )

        # Populate the config templace
        placeholders = {
            DPlaceholder.ANY_IP: self.any_ip(),
            DPlaceholder.BLOCKCHAIN_DIR: self.blockchain_dir(),
            DPlaceholder.INSTANCE: self.instance(),
            DPlaceholder.IN_PEERS: self.in_peers(),
            DPlaceholder.LOG_FILE: fq_log,
            DPlaceholder.LOG_LEVEL: self.log_level(),
            DPlaceholder.MAX_LOG_FILES: self.max_log_files(),
            DPlaceholder.MAX_LOG_SIZE: self.max_log_size(),
            DPlaceholder.MONEROD_DIR: monerod_dir,
            DPlaceholder.OUT_PEERS: self.out_peers(),
            DPlaceholder.P2P_BIND_PORT: self.p2p_bind_port(),
            DPlaceholder.PRIORITY_NODE_1: self.priority_node_1(),
            DPlaceholder.PRIORITY_PORT_1: self.priority_port_1(),
            DPlaceholder.PRIORITY_NODE_2: self.priority_node_2(),
            DPlaceholder.PRIORITY_PORT_2: self.priority_port_2(),
            DPlaceholder.RPC_BIND_PORT: self.rpc_bind_port(),
            DPlaceholder.SHOW_TIME_STATS: self.show_time_stats(),
            DPlaceholder.STDIN_PATH: self.stdin_path(),
            DPlaceholder.ZMQ_PUB_PORT: self.zmq_pub_port(),
            DPlaceholder.ZMQ_RPC_PORT: self.zmq_rpc_port(),
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
