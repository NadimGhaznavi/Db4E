"""
db4e/Modules/XMRigRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything XMRig Remote
"""

from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Modules.Components import (
    Instance,
    Remote,
    IpAddr,
    Hashrate,
    LocalTimestamp,
    Timestamp,
    Uptime,
)
from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel


class XMRigRemote(SoftwareSystem):

    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = DElem.XMRIG_REMOTE
        self.name = DLabel.XMRIG_REMOTE

        self.add_component(DField.INSTANCE, Instance())
        self.add_component(DField.IP_ADDR, IpAddr())
        self.add_component(DField.REMOTE, Remote())
        self.add_component(DField.HASHRATE, Hashrate())
        self.add_component(DField.LOCAL_TIMESTAMP, LocalTimestamp())
        self.add_component(DField.TIMESTAMP, Timestamp())
        self.add_component(DField.UPTIME, Uptime())

        self.instance = self.components[DField.INSTANCE]
        self.ip_addr = self.components[DField.IP_ADDR]
        self.remote = self.components[DField.REMOTE]
        self.hashrate = self.components[DField.HASHRATE]
        self.local_timestamp = self.components[DField.LOCAL_TIMESTAMP]
        self.timestamp = self.components[DField.TIMESTAMP]
        self.uptime = self.components[DField.UPTIME]

        if rec:
            self.from_rec(rec)
            # print(f"XMRigRemote: rec: {rec}, uptime: {self.uptime()}")

    def __dict__(self):
        xmrig_remote_dict = {
            DField.INSTANCE: self.instance(),
            DField.IP_ADDR: self.ip_addr(),
            DField.HASHRATE: self.hashrate(),
            DField.UPDATED_Y: self.local_timestamp().year,
            DField.UPDATED_MO: self.local_timestamp().month,
            DField.UPDATED_D: self.local_timestamp().day,
            DField.UPDATED_H: self.local_timestamp().hour,
            DField.UPDATED_MI: self.local_timestamp().minute,
            DField.UPDATED_S: self.local_timestamp().second,
            DField.UTC_Y: self.timestamp().year,
            DField.UTC_MO: self.timestamp().month,
            DField.UTC_D: self.timestamp().day,
            DField.UTC_H: self.timestamp().hour,
            DField.UTC_MI: self.timestamp().minute,
            DField.UTC_S: self.timestamp().second,
        }
        return xmrig_remote_dict

    def hashrates(self, hashrate_data=None):
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates

    def shares_found(self, shares_found_data=None):
        if shares_found_data is not None:
            self._shares_found = shares_found_data
        return self._shares_found
