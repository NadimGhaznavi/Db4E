"""
db4e/Modules/P2Pool.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything P2Pool Remote
"""

from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.Components import (Instance, Remote, IpAddr, StratumPort)
from db4e.Constants.Fields import(
    P2POOL_REMOTE_FIELD, INSTANCE_FIELD, REMOTE_FIELD, IP_ADDR_FIELD,
    STRATUM_PORT_FIELD)
from db4e.Constants.Labels import(P2POOL_REMOTE_LABEL)



class P2PoolRemote(SoftwareSystem):


    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = P2POOL_REMOTE_FIELD
        self.name = P2POOL_REMOTE_LABEL

        self.add_component(INSTANCE_FIELD, Instance())
        self.add_component(IP_ADDR_FIELD, IpAddr())
        self.add_component(REMOTE_FIELD, Remote())
        self.add_component(STRATUM_PORT_FIELD, StratumPort())

        self.instance = self.components[INSTANCE_FIELD]
        self.ip_addr = self.components[IP_ADDR_FIELD]
        self.remote = self.components[REMOTE_FIELD]
        self.stratum_port = self.components[STRATUM_PORT_FIELD]

        if rec:
            self.from_rec(rec)


