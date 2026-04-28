# db4e/Constants/DElem.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from typing import Final

from db4e.constants.DField import DField


# Elements
class DSync:
    ELEMENT: Final[str] = "element"
    ELEM_TYPE: Final[str] = "elem_type"
    LOG_LINES = DField.LOG_LINES
    PING: Final[str] = "ping"
    TABLE_NAME: Final[str] = "table_name"
