"""
db4e/Modules/P2PoolRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything P2Pool Remote
"""

from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.Components import Instance, Remote, IpAddr, StratumPort
from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel


class P2PoolRemote(SoftwareSystem):

    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = DElem.P2POOL_REMOTE
        self.name = DLabel.P2POOL_REMOTE

        self.add_component(DField.INSTANCE, Instance())
        self.add_component(DField.IP_ADDR, IpAddr())
        self.add_component(DField.REMOTE, Remote())
        self.add_component(DField.STRATUM_PORT, StratumPort())

        self.instance = self.components[DField.INSTANCE]
        self.ip_addr = self.components[DField.IP_ADDR]
        self.remote = self.components[DField.REMOTE]
        self.stratum_port = self.components[DField.STRATUM_PORT]

        if rec:
            self.from_rec(rec)

    def __dict__(self):
        p2pool_remote_dict = {
            DField.INSTANCE: self.instance(),
            DField.IP_ADDR: self.ip_addr(),
            DField.STRATUM_PORT: self.stratum_port(),
        }
        return p2pool_remote_dict
