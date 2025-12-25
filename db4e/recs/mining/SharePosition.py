"""
db4e/recs/mining/SharePosition.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.mining.BaseMining import BaseMining
from db4e.constants.DSQL import DCol


class SharePosition(BaseMining):
    """
    Record representing the current share position for a pool and chain.
    """

    def __init__(self, chain=None, pool=None, share_position=None, rec=None):
        """
        Initialize the share position record and optionally hydrate from a DB record.

        :param chain: Optional chain identifier.
        :type chain: str or None
        :param pool: Optional pool identifier.
        :type pool: str or None
        :param share_position: Optional share position value.
        :type share_position: int or None
        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__(rec=rec)
        self._chain = chain
        self._pool = pool
        self._share_position = share_position
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
        self._pool = rec[DCol.POOL]
        self._share_position = rec[DCol.SHARE_POSITION]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with share position fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.CHAIN: self._chain,
                DCol.POOL: self._pool,
                DCol.SHARE_POSITION: self._share_position,
            }
        )
        return data

    def constraints(self):
        """
        Return the uniqueness constraint columns for this record.

        :return: Column names defining uniqueness.
        :rtype: list
        """
        return [
            DCol.CHAIN,
            DCol.POOL,
            DCol.SHARE_POSITION,
            DCol.UPDATED_YEAR,
            DCol.UPDATED_MONTH,
            DCol.UPDATED_DAY,
            DCol.UPDATED_HOUR,
            DCol.UPDATED_MINUTE,
            DCol.UPDATED_SECOND,
        ]
