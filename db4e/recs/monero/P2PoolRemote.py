"""
db4e/recs/monero/P2PoolRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0

Everything P2Pool Remote
"""

from db4e.recs.monero.BaseMonero import BaseMonero
from db4e.constants.DSQL import DCol
from db4e.constants.DDef import DDef


class P2PoolRemote(BaseMonero):
    """
    Record for a remote P2Pool endpoint.
    """

    def __init__(self, rec=None):
        """
        Initialize the remote P2Pool record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__()
        self._ip_addr = ""
        self._stratum_port = DDef.STRATUM_PORT
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
        self.ip_addr(rec[DCol.IP_ADDR])
        self.stratum_port(rec[DCol.STRATUM_PORT])

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with remote P2Pool fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.IP_ADDR: self._ip_addr,
                DCol.STRATUM_PORT: self._stratum_port,
            }
        )
        return data

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with remote P2Pool fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.IP_ADDR: self._ip_addr,
                DCol.STRATUM_PORT: self._stratum_port,
            }
        )
        return data

    ## Attribute get/set methods

    def ip_addr(self, ip_addr=None):
        """
        Get or set the endpoint IP address.

        :param ip_addr: Optional IP address to set.
        :type ip_addr: str or None
        :return: Current IP address.
        :rtype: str
        """
        if ip_addr is not None:
            self._ip_addr = ip_addr
        return self._ip_addr

    def stratum_port(self, stratum_port=None):
        """
        Get or set the stratum port.

        :param stratum_port: Optional port to set.
        :type stratum_port: int or None
        :return: Current stratum port.
        :rtype: int
        """
        if stratum_port is not None:
            self._stratum_port = int(stratum_port)
        return self._stratum_port
