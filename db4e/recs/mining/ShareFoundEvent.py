"""
db4e/recs/mining/BaseHourlyMining.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.mining.BaseMining import BaseMining
from db4e.constants.DSQL import DCol


class ShareFoundEvent(BaseMining):
    """
    Record representing a share found event.
    """

    def __init__(self, miner=None, chain=None, pool=None, effort=None, rec=None):
        """
        Initialize the share found event and optionally hydrate from a DB record.

        :param miner: Optional miner identifier.
        :type miner: str or None
        :param chain: Optional chain identifier.
        :type chain: str or None
        :param pool: Optional pool identifier.
        :type pool: str or None
        :param effort: Optional effort value.
        :type effort: int or float or None
        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__(rec=rec)
        self._miner = miner
        self._chain = chain
        self._pool = pool
        self._effort = effort
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
        self._miner = rec[DCol.MINER]
        self._chain = rec[DCol.CHAIN]
        self._pool = rec[DCol.POOL]
        self._effort = rec[DCol.EFFORT]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with share found fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.MINER: self._miner,
                DCol.CHAIN: self._chain,
                DCol.POOL: self._pool,
                DCol.EFFORT: self._effort,
            }
        )
        return data

    def miner(self, miner=None):
        """
        Get or set the miner identifier.

        :param miner: Optional miner identifier to set.
        :type miner: str or None
        :return: Current miner identifier.
        :rtype: str or None
        """
        if miner is not None:
            self._miner = miner
        return self._miner

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

    def pool(self, pool=None):
        """
        Get or set the pool identifier.

        :param pool: Optional pool identifier to set.
        :type pool: str or None
        :return: Current pool identifier.
        :rtype: str or None
        """
        if pool is not None:
            self._pool = pool
        return self._pool

    def effort(self, effort=None):
        """
        Get or set the effort value.

        :param effort: Optional effort value to set.
        :type effort: int or float or None
        :return: Current effort value.
        :rtype: int or float or None
        """
        if effort is not None:
            self._effort = effort
        return self._effort
