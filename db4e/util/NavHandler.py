"""
db4e/util/NavHandler.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.db.DeplDb import DeplDb
from db4e.constants.DField import DField
from db4e.constants.DElem import DElem


class NavHandler:
    """Class to handle NavPane requests"""

    def __init__(self, depl_db: DeplDb):
        self.depl_db = depl_db

    def get_deployment(self, request):
        elem_type = request.get(DField.ELEMENT_TYPE)
        instance = request.get(DField.INSTANCE)
        return self.depl_db.get_deployment(elem_type=elem_type, instance=instance)
