"""
db4e/Constants/DOps.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup
from db4e.Constants.DField import DField

###############################################################
#                                                             #
#  CAUTION: Changes here will result in Mongo schema changes  #
#                                                             #
#       You will likely break historical reporting!           #
#                                                             #
###############################################################


class DOps(ConstGroup):
    CURRENT_UPTIME : str = "current_uptime"
    START_STOP_EVENT : str = "start_stop_event"
    START_TIME : str = "start_time"
    STOP_TIME : str = "stop_time"
    TOTAL_UPTIME : str = "total_uptime"
