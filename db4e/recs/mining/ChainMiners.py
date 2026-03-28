"""
db4e/recs/mining/ChainMiners.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.mining.BaseHourlyMining import BaseHourlyMining
from db4e.constants.DSQL import DCol


class ChainMiners(BaseHourlyMining):
    """
    Record representing the number of miners on a chain per hour.
    """

    def __init__(self, chain=None, num_miners=None, rec=None):
        """
        Initialize the chain miners record and optionally hydrate from a DB record.

        :param chain: Optional chain identifier.
        :type chain: str or None
        :param num_miners: Optional miner count.
        :type num_miners: int or None
        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__(rec=rec)
        self._chain = chain
        self._miners = num_miners
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
        self._chain = rec[DCol.CHAIN]
        self._miners = rec[DCol.MINERS]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with chain miners fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update({DCol.CHAIN: self._chain, DCol.MINERS: self._miners})
        return data

    def constraints(self):
        """
        Return the uniqueness constraint columns for this record.

        :return: Column names defining uniqueness.
        :rtype: list
        """
        return [
            DCol.CHAIN,
            DCol.UPDATED_YEAR,
            DCol.UPDATED_MONTH,
            DCol.UPDATED_DAY,
            DCol.UPDATED_HOUR,
        ]
