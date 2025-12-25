# db4e/elem/monero/LocalMonero.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

from db4e.recs.monero.BaseMonero import BaseMonero
from db4e.constants.DSQL import DCol


class LocalMonero(BaseMonero):
    """
    Base record for locally managed Monero components.
    """

    def __init__(self, rec=None):
        """
        Initialize the local Monero record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__()
        self._enabled = False
        if rec is not None:
            self.from_rec(rec)

    def __repr__(self):
        """
        Return a string representation including the instance name.

        :return: Class and instance name string.
        :rtype: str
        """
        return f"{self.elem_type()}({self.instance()})"

    def from_rec(self, rec):
        """
        Populate the object from a database record.

        :param rec: Database record mapping.
        :type rec: dict
        :return: None
        :rtype: None
        """
        super().from_rec(rec)
        self._enabled = rec[DCol.ENABLED]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with local Monero fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update({DCol.ENABLED: self._enabled})
        return data

    def enabled(self, enabled=None):
        """
        Get or set whether the component is enabled.

        :param enabled: Optional enabled flag to set.
        :type enabled: bool or None
        :return: Current enabled flag.
        :rtype: bool
        """
        if enabled is not None:
            self._enabled = enabled
        return self._enabled
