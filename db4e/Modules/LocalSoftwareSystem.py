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
from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel



class LocalSoftwareSystem(SoftwareSystem):


    def __init__(self):
        super().__init__()
        self._elem_type = DField.LOCAL_SOFTWARE_SYSTEM
        self.name = DLabel.LOCAL_SOFTWARE_SYSTEM
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
            if rec[DField.ENABLED]:
                self._enabled = True
            else:
                self._enabled = False
        except KeyError:
            raise ValueError(
                f"LocalSoftwareSystem:from_rec(): Missing '{DField.ENABLED}' field")

    def to_rec(self):
        rec = super().to_rec()
        if self._enabled == True:
            rec[DField.ENABLED] = True
        else:
            rec[DField.ENABLED] = False
        return rec
