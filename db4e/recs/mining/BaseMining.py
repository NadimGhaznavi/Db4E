"""
db4e/recs/mining/BaseMining.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.mining.BaseHourlyMining import BaseHourlyMining
from db4e.constants.DSQL import DCol


class BaseMining(BaseHourlyMining):
    """
    Base record for mining metrics tracked below hourly granularity.
    """

    def __init__(self, rec=None):
        """
        Initialize the mining record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__(rec=rec)
        self._updated_mi = None
        self._updated_s = None
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
        self._updated_mi = rec[DCol.UPDATED_MINUTE]
        self._updated_s = rec[DCol.UPDATED_SECOND]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with mining fields.
        :rtype: dict
        """
        data = super().to_dict()
        return data
