"""
db4e/recs/monero/XMRigRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0

Everything XMRig Remote
"""

from db4e.recs.monero.BaseMonero import BaseMonero
from db4e.constants.DSQL import DCol


class XMRigRemote(BaseMonero):

    def __init__(self, rec=None):
        super().__init__()
        self._ip_addr = None
        # Current hashrate
        self._hashrate = None
        # Historical hashrate data
        self._hashrates = None
        # Historical share found data
        self._shares_found = None
        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._ip_addr = rec[DCol.IP_ADDR]

    def to_dict(self):
        data = super().to_dict()
        data.update({DCol.IP_ADDR: self._ip_addr})
        return data

    def ip_addr(self, ip_addr=None):
        if ip_addr is not None:
            self._ip_addr = ip_addr
        return self._ip_addr

    def hashrate(self, hashrate=None):
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate

    def hashrates(self, hashrate_data=None):
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates

    def shares_found(self, shares_found_data=None):
        if shares_found_data is not None:
            self._shares_found = shares_found_data
        return self._shares_found
