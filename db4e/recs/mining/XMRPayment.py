"""
db4e/recs/mining/XMRPayment.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.mining.BaseMining import BaseMining
from db4e.util.Helper import xmr_to_piconero
from db4e.constants.DSQL import DCol

PICONEROS_PER_XMR = 1_000_000_000_000


class XMRPayment(BaseMining):
    """
    Record representing an XMR payment value.
    """

    def __init__(self, chain=None, pool=None, payment=None, rec=None):
        """
        Initialize the payment record and optionally hydrate from a DB record.

        :param chain: Optional chain identifier.
        :type chain: str or None
        :param pool: Optional pool identifier.
        :type pool: str or None
        :param payment: Optional payment amount in XMR.
        :type payment: int or float or None
        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__(rec=rec)
        self._chain = chain
        self._pool = pool
        if payment is not None:
            self._piconero = xmr_to_piconero(payment)
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
        self._piconero = rec[DCol.PICONERO]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with payment fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.CHAIN: self._chain,
                DCol.POOL: self._pool,
                DCol.PICONERO: self._piconero,
            }
        )
        return data
