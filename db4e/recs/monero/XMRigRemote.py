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
    """
    Record for a remote XMRig miner endpoint.
    """

    def __init__(self, rec=None):
        """
        Initialize the remote XMRig record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
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
        """
        Populate the object from a database record.

        :param rec: Database record mapping.
        :type rec: dict
        :return: None
        :rtype: None
        """
        super().from_rec(rec)
        self._ip_addr = rec[DCol.IP_ADDR]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with remote XMRig fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update({DCol.IP_ADDR: self._ip_addr})
        return data

    def ip_addr(self, ip_addr=None):
        """
        Get or set the endpoint IP address.

        :param ip_addr: Optional IP address to set.
        :type ip_addr: str or None
        :return: Current IP address.
        :rtype: str or None
        """
        if ip_addr is not None:
            self._ip_addr = ip_addr
        return self._ip_addr

    def hashrate(self, hashrate=None):
        """
        Get or set the current miner hashrate.

        :param hashrate: Optional hashrate value to set.
        :type hashrate: int or None
        :return: Current hashrate value.
        :rtype: int or None
        """
        if hashrate is not None:
            self._hashrate = int(hashrate)
        return self._hashrate

    def hashrates(self, hashrate_data=None):
        """
        Get or set historical miner hashrate data.

        :param hashrate_data: Optional historical data to set.
        :type hashrate_data: list or dict or None
        :return: Historical hashrate data.
        :rtype: list or dict or None
        """
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates

    def shares_found(self, shares_found_data=None):
        """
        Get or set historical share found data.

        :param shares_found_data: Optional historical data to set.
        :type shares_found_data: list or dict or None
        :return: Historical share found data.
        :rtype: list or dict or None
        """
        if shares_found_data is not None:
            self._shares_found = shares_found_data
        return self._shares_found
