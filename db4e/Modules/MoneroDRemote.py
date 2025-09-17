"""
db4e/Modules/MoneroDRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything remote Monero Daemon
"""

from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.Components import (
    Instance, Remote, RpcBindPort, IpAddr, ZmqPubPort, PrimaryServer)
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem



class MoneroDRemote(SoftwareSystem):


    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = DElem.MONEROD_REMOTE
        self.name = DLabel.MONEROD_REMOTE

        self.add_component(DField.INSTANCE, Instance())
        self.add_component(DField.REMOTE, Remote())
        self.add_component(DField.RPC_BIND_PORT, RpcBindPort())
        self.add_component(DField.IP_ADDR, IpAddr())
        self.add_component(DField.ZMQ_PUB_PORT, ZmqPubPort())

        self.instance = self.components[DField.INSTANCE]
        self.remote = self.components[DField.REMOTE]
        self.rpc_bind_port = self.components[DField.RPC_BIND_PORT]
        self.ip_addr = self.components[DField.IP_ADDR]
        self.zmq_pub_port = self.components[DField.ZMQ_PUB_PORT]

        if rec:
            self.from_rec(rec)

