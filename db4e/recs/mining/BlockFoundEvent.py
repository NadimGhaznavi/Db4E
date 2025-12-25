"""
db4e/recs/mining/BlockFoundEvent.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.mining.BaseMining import BaseMining
from db4e.constants.DSQL import DCol


class BlockFoundEvent(BaseMining):
    """
    Record representing a block found event for a chain.
    """

    def __init__(self, chain=None, rec=None):
        """
        Initialize the block found event and optionally hydrate from a DB record.

        :param chain: Optional chain identifier.
        :type chain: str or None
        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__(rec=rec)
        self._chain = chain
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

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with block found fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update({DCol.CHAIN: self._chain})
        return data

    def chain(self, chain=None):
        """
        Get or set the chain identifier.

        :param chain: Optional chain identifier to set.
        :type chain: str or None
        :return: Current chain identifier.
        :rtype: str or None
        """
        if chain is not None:
            self._chain = chain
        return self._chain
