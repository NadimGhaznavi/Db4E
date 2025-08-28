"""
db4e/Modules/LocalSoftwareSystem.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

This is a virtual class.
"""


from db4e.Modules.SoftwareSystem import SoftwareSystem
from db4e.Constants.Labels import LOCAL_SOFTWARE_SYSTEM_LABEL
from db4e.Constants.Fields import LOCAL_SOFTWARE_SYSTEM_FIELD, ENABLED_FIELD




class LocalSoftwareSystem(SoftwareSystem):


    def __init__(self):
        super().__init__()
        self._elem_type = LOCAL_SOFTWARE_SYSTEM_FIELD
        self.name = LOCAL_SOFTWARE_SYSTEM_LABEL
        self._enabled = False


    def disable(self):
        self._enabled = False


    def enable(self):
        self._enabled = True


    def enabled(self):
        return self._enabled


    def from_rec(self, rec: dict):
        super().from_rec(rec)
        try:
            if rec[ENABLED_FIELD]:
                self.enable()
            else:
                self.disable()
        except KeyError:
            raise ValueError(
                f"LocalSoftwareSystem:from_rec(): Missing '{ENABLED_FIELD}' field")


    def to_rec(self):
        rec = super().to_rec()
        rec[ENABLED_FIELD] = bool(self.enabled())
        return rec
