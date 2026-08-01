# db4e/Modules/Helper.py
# 
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0
#
# Helper functions that are used in multiple modules
#
from dataclasses import dataclass

from db4e.constants.DField import DField
from db4e.constants.DSQL import DCol


@dataclass(slots=True, frozen=True)
class HealthMsg:
    category: DField
    instance: str
    elem_type: str
    message: str
    status: DField

    def to_dict(self):
        return {
            DCol.CATEGORY: self.category,
            DCol.INSTANCE: self.instance,
            DCol.ELEMENT_TYPE: self.elem_type,
            DCol.MESSAGE: self.message,
            DCol.STATUS: self.status,
        }

    def __repr__(self):
        return f"<HealthMsg [{self.elem_type}:{self.instance}][{self.category}][{self.status.upper()}]: {self.message}>"