"""
db4e/Constants/DSystemD.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup

class DSystemD(ConstGroup):
    ACTIVE : str = "active"
    DISABLE : str = "disable"
    ENABLE : str = "enable"
    ENABLED : str = "enabled"
    PID : str = "pid"
    RAW_STDOUT : str = "raw_stdout"
    RAW_STDERR : str = "raw_stderr"
    START : str = "start"
    STATUS : str = "status"
    STOP : str = "stop"
