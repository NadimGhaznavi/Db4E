"""
db4e/Constants/DStatus.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup

# Status
class DStatus(ConstGroup):
    ERROR : str = "error"
    GOOD : str = "good"
    UNKNOWN : str = "unknown"
    WARN : str = "warn"

    