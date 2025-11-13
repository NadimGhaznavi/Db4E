"""
db4e/Modules/MoneroDRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything remote Monero Daemon
"""

from db4e.recs.monero.BaseMonero import BaseMonero

from db4e.constants.DSQL import DCol
from db4e.constants.DDef import DDef


class MoneroDRemote(BaseMonero):

    def __init__(self, rec=None):
        super().__init__()
        self._ip_addr = ""
        self._rpc_bind_port = DDef.RPC_BIND_PORT
        self._zmq_pub_port = DDef.ZMQ_PUB_PORT

        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._ip_addr = rec[DCol.IP_ADDR]
        self._rpc_bind_port = rec[DCol.RPC_BIND_PORT]
        self._zmq_pub_port = rec[DCol.ZMQ_PUB_PORT]

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                DCol.IP_ADDR: self._ip_addr,
                DCol.RPC_BIND_PORT: self._rpc_bind_port,
                DCol.ZMQ_PUB_PORT: self._zmq_pub_port,
            }
        )
        return data

    ## Attribute get/set methods

    def ip_addr(self, ip_addr=None):
        if ip_addr is not None:
            self._ip_addr = ip_addr
        return self._ip_addr

    def rpc_bind_port(self, rpc_bind_port=None):
        if rpc_bind_port is not None:
            self._rpc_bind_port = int(rpc_bind_port)
        return self._rpc_bind_port

    def zmq_pub_port(self, zmq_pub_port=None):
        if zmq_pub_port is not None:
            self._zmq_pub_port = int(zmq_pub_port)
        return self._zmq_pub_port
