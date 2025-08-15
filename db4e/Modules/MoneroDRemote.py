"""
db4e/Modules/MonerodRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything remote Monero Daemon
"""

from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.Components import Instance, Remote, RpcBindPort, IpAddr, ZmqPubPort
from db4e.Constants.Fields import (
    MONEROD_REMOTE_FIELD,INSTANCE_FIELD, REMOTE_FIELD, RPC_BIND_PORT_FIELD, 
    IP_ADDR_FIELD, ZMQ_PUB_PORT_FIELD)
from db4e.Constants.Labels import (MONEROD_REMOTE_LABEL)



class MoneroDRemote(SoftwareSystem):


    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = MONEROD_REMOTE_FIELD
        self.name = MONEROD_REMOTE_LABEL

        self.add_component(INSTANCE_FIELD, Instance())
        self.add_component(REMOTE_FIELD, Remote())
        self.add_component(RPC_BIND_PORT_FIELD, RpcBindPort())
        self.add_component(IP_ADDR_FIELD, IpAddr())
        self.add_component(ZMQ_PUB_PORT_FIELD, ZmqPubPort())

        self.instance = self.components[INSTANCE_FIELD]
        self.remote = self.components[REMOTE_FIELD]
        self.rpc_bind_port = self.components[RPC_BIND_PORT_FIELD]
        self.ip_addr = self.components[IP_ADDR_FIELD]
        self.zmq_pub_port = self.components[ZMQ_PUB_PORT_FIELD]

        if rec:
            self.from_rec(rec)

