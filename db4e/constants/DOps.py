# db4e/Constants/DOps.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from typing import Final
from db4e.constants.DField import DField

###############################################################
#                                                             #
#  CAUTION: Changes here will result in Mongo schema changes  #
#                                                             #
#       You will likely break historical reporting!           #
#                                                             #
###############################################################


class DOps:
    CURRENT_UPTIME: Final[str] = "current_uptime"
    START_STOP_EVENT: Final[str] = "start_stop_event"
    START_TIME: Final[str] = "start_time"
    STOP_TIME: Final[str] = "stop_time"
    TOTAL_UPTIME: Final[str] = "total_uptime"
