"""
db4e/Constants/DMethod.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup
from db4e.Constants.DField import DField

# Methods
class DMethod(ConstGroup):
    ADD_DEPLOYMENT : str = "add_deployment"
    ANALYTICS : str = "analytics"
    DELETE_DEPLOYMENT : str = "del_deployment"
    ENABLE_DEPLOYMENT : str = "enable_deployment"
    DISABLE_DEPLOYMENT : str = "disable_deployment"
    GET_NEW : str = "get_new"
    GET_DEPL : str = "get_deployment"
    GET_TUI_LOG : str = "get_tui_log"
    GET_RUNTIME_LOG : str = "get_runtime_log"
    GET_UPTIME : str = "get_uptime"
    HASHRATES : str = "hashrates"
    INITIAL_SETUP : str = "initial_setup"
    INITIAL_SETUP_PROCEED : str = "initial_setup_proceed"
    LOG_VIEWER : str = DField.LOG_VIEWER
    PLOT : str = "plot"
    POST_JOB : str = "post_job"
    RESTART : str = "restart"
    SET_DONATIONS : str = "set_donations"
    SET_PANE : str = DField.SET_PANE
    SET_PRIMARY : str = "set_primary"
    UPDATE_DEPLOYMENT : str = "update_deployment"
    RUNTIME : str = "runtime"