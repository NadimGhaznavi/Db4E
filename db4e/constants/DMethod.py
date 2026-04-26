# db4e/Constants/DMethod.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from typing import Final
from db4e.constants.DField import DField


# Methods
class DMethod:
    ADD_DEPLOYMENT: Final[str] = "add_deployment"
    BLOCKS_FOUND: Final[str] = "blocks_found"
    DELETE_DEPLOYMENT: Final[str] = "del_deployment"
    ENABLE_DEPLOYMENT: Final[str] = "enable_deployment"
    DISABLE_DEPLOYMENT: Final[str] = "disable_deployment"
    GET_LOG: Final[str] = "get_log"
    GET_NEW: Final[str] = "get_new"
    GET_DEPL: Final[str] = "get_deployment"
    GET_PAYMENTS: Final[str] = "get_payments"
    GET_TUI_LOG: Final[str] = "get_tui_log"
    GET_RUNTIME_LOG: Final[str] = "get_runtime_log"
    GET_START_STOP_LOG: Final[str] = "get_start_stop_log"
    GET_TABLE_DATA: Final[str] = "get_table_data"
    GET_UPTIME: Final[str] = "get_uptime"
    HASHRATES: Final[str] = "hashrates"
    INITIAL_SETUP: Final[str] = "initial_setup"
    INITIAL_SETUP_PROCEED: Final[str] = "initial_setup_proceed"
    LOG_VIEWER: Final[str] = DField.LOG_VIEWER
    PLOT: Final[str] = "plot"
    POST_JOB: Final[str] = "post_job"
    RESTART: Final[str] = "restart"
    START: Final[str] = "start"
    STOP: Final[str] = "stop"
    SET_DONATIONS: Final[str] = "set_donations"
    SET_PANE: Final[str] = DField.SET_PANE
    SET_PRIMARY: Final[str] = "set_primary"
    SHARES_FOUND: Final[str] = "shares_found"
    UPDATE_DEPLOYMENT: Final[str] = "update_deployment"
    RUNTIME: Final[str] = "runtime"
