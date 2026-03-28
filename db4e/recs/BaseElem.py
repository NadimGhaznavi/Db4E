# db4e/elem/BaseElem.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

from db4e.constants.DSQL import DCol


class BaseElem:
    """
    Base record class providing shared ID handling for Db4E elements.
    """

    def __init__(self, rec=None):
        """
        Initialize the record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        self._id = None
        if rec is not None:
            self.from_rec(rec)

    def __repr__(self):
        """
        Return a string representation of the element type.

        :return: Element type name.
        :rtype: str
        """
        return self.elem_type()

    def from_rec(self, rec):
        """
        Populate the object from a database record.

        :param rec: Database record mapping.
        :type rec: dict
        :return: None
        :rtype: None
        """
        self._id = rec[DCol.ID]

    def to_dict(self):
        """
        Return a dictionary representation of the element.

        :return: Dictionary with element fields.
        :rtype: dict
        """
        return {DCol.ID: self._id}

    def elem_type(self):
        """
        Return the element type name.

        :return: Element type name.
        :rtype: str
        """
        return type(self).__name__

    def id(self, id=None):
        """
        Get or set the element ID.

        :param id: Optional ID value to set.
        :type id: int or None
        :return: Current element ID.
        :rtype: int or None
        """
        if id is not None:
            self._id = id
        return self._id
