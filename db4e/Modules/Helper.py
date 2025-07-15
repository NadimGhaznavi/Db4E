"""
db4e/Modules/Helper.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0

Helper functions that are used in multiple modules   
"""
import os, grp, getpass

from textual.widgets import RadioSet, RadioButton

from db4e.Constants.Fields import(
    COMPONENT_FIELD, GOOD_FIELD, GROUP_FIELD, ERROR_FIELD, MONEROD_FIELD, 
    P2POOL_FIELD, USER_FIELD, WARN_FIELD, XMRIG_FIELD
)

def get_effective_identity():
    """Return the effective user and group for the account running Db3e"""
    # User account
    user = getpass.getuser()
    # User's group
    effective_gid = os.getegid()
    group_entry = grp.getgrgid(effective_gid)
    group = group_entry.gr_name
    return { USER_FIELD: user, GROUP_FIELD: group }

def result_row(label: str, status: str, msg:str ):
    """Return a standardized result dict for display in Results pane."""
    assert status in {GOOD_FIELD, WARN_FIELD, ERROR_FIELD}, f"invalid status: {status}"
    return {label: {'status': status, 'msg': msg}}

def get_radio_map(rec, depl_mgr):
    component_map = {
        P2POOL_FIELD: MONEROD_FIELD,
        XMRIG_FIELD: P2POOL_FIELD
    }
    component = rec[COMPONENT_FIELD]
    instances = depl_mgr.get_deployment_ids_and_instances(component_map[component])
    radio_map = {}
    for (instance, id) in instances:
        radio_map[instance] = id
    return radio_map
    