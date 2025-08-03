"""
db4e/Modules/Helper.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Helper functions that are used in multiple modules   
"""
import os, grp, getpass
import socket, ipaddress
import re

from rich import box
from rich.table import Table

from textual.widgets import RadioSet, RadioButton

from db4e.Constants.Fields import(
    P2POOL_REMOTE_FIELD, GOOD_FIELD, GROUP_FIELD, ERROR_FIELD, 
    P2POOL_FIELD, USER_FIELD, WARN_FIELD, XMRIG_FIELD, COMPONENTS_FIELD,
    FIELD_FIELD, REMOTE_FIELD, VALUE_FIELD, ACTIVE_FIELD, ELEMENT_TYPE_FIELD,
    PENDING_FIELD, ENABLE_FIELD, PARENT_ID_FIELD, INSTANCE_FIELD)

class Status:
    ACTIVE = ACTIVE_FIELD
    ENABLED = ENABLE_FIELD
    ERROR = ERROR_FIELD
    WARNING = WARN_FIELD
    PENDING = PENDING_FIELD

error_color = "#935fcf"

def get_component_value(data, field_name):
    """
    Generic helper to get any component value by field name.
    
    Args:
        data (dict): Dictionary containing components with field/value pairs
        field_name (str): The field name to search for
        
    Returns:
        any or None: The component value, or None if not found
    """
    if not isinstance(data, dict) or 'components' not in data:
        return None
    
    components = data.get(COMPONENTS_FIELD, [])
    
    for component in components:
        if isinstance(component, dict) and component.get(FIELD_FIELD) == field_name:
            return component.get(VALUE_FIELD)
    
    return None


def get_effective_identity():
    """Return the effective user and group for the account running Db3e"""
    # User account
    user = getpass.getuser()
    # User's group
    effective_gid = os.getegid()
    group_entry = grp.getgrgid(effective_gid)
    group = group_entry.gr_name
    return { USER_FIELD: user, GROUP_FIELD: group }


def get_remote_state(data):
    """
    Parse out the remote state from a data structure.
    
    Args:
        data (dict): Dictionary containing components with field/value pairs
        
    Returns:
        bool or None: The remote state value, or None if not found
    """
    if not isinstance(data, dict) or 'components' not in data:
        return None
    
    components = data.get(COMPONENTS_FIELD, [])
    
    for component in components:
        if isinstance(component, dict) and component.get(FIELD_FIELD) == REMOTE_FIELD:
            return component.get(VALUE_FIELD)
    
    return None


def gen_radio_map(rec, depl_mgr):
    elem_type = rec[ELEMENT_TYPE_FIELD]
    
    if elem_type == XMRIG_FIELD:
        local_instances = depl_mgr.get_deployment_ids_and_instances(P2POOL_FIELD)
        remote_instances = depl_mgr.get_deployment_ids_and_instances(P2POOL_REMOTE_FIELD)
        instances = local_instances + remote_instances
        instances.sort()
        
        radio_set = {}
        for (instance, id) in instances:
            radio_set[instance] = id

        return radio_set
    

def gen_results_table(results):
    #print(f"Helper:gen_results_table(): Results list:")
    #if not results:
    #    return ""
    
    table = Table(show_header=True, header_style="bold #31b8e6", style="#0c323e", box=box.SIMPLE)
    table.add_column("Component", width=25)
    table.add_column("Message")

    for item in results:
        for category, msg_dict in item.items():
            message = msg_dict["msg"]
            if msg_dict["status"] == "good":
                table.add_row(f"✅ [bold]{category}[/]", f"{message}")
            elif msg_dict["status"] == "warn":
                table.add_row(f"⚠️  [yellow]{category}[/]", f"[yellow]{message}[/]")
            elif msg_dict["status"] == "error":
                table.add_row(f"💥 [b {error_color}]{category}[/]", f"[{error_color}]{message}[/]")
    return table


def is_port_open(ip_addr, port_num):
    #print(f"Helper:is_port_open(): {ip_addr}/{port_num}")
    if not is_valid_ip_or_hostname(ip_addr):
        return False
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)  # Set aLine timeout for the connection attempt
            result = sock.connect_ex((ip_addr, int(port_num)))
            return result == 0
    except socket.gaierror:
        return False  # Handle cases like invalid hostname
    

def is_valid_ip_or_hostname(host: str) -> str:
    try:
        socket.getaddrinfo(host, None)  # works for IPv4/IPv6
        return True
    except socket.gaierror:
        return False
    

def result_row(label: str, status: str, msg:str ):
    """Return a standardized result dict for display in Results pane."""
    assert status in {GOOD_FIELD, WARN_FIELD, ERROR_FIELD}, f"invalid status: {status}"
    return {label: {'status': status, 'msg': msg}}


def set_component_value(element, field_name, value):
    """
    Generic helper to set any component value by field name.
    
    Args:
        element (dict): Dictionary containing components with field/value pairs
        field_name (str): The field name to search for
        value (any): The value to set
        
    Returns:
        element (possibly updated)
    """
    if not isinstance(element, dict) or 'components' not in element:
        raise ValueError("Helper:set_component_value():Invalid input")
        
    components = element.get(COMPONENTS_FIELD, [])
    
    for component in components:
        if isinstance(component, dict) and component.get(FIELD_FIELD) == field_name:
            component[VALUE_FIELD] = value
            return element
            
    return element


def update_component_values(rec, updates):
    """Updates multiple component values in a deployment record from a dictionary.

    This function iterates through the 'components' list of a given record.
    For each component, it checks if its 'field' name exists as a key in the
    'updates' dictionary. If it does, the component's 'value' is updated
    with the corresponding value from the 'updates' dictionary.

    The modification is done in-place on the 'rec' dictionary.

    Args:
        rec (dict): The deployment record dictionary to update. It is expected
            to have a 'components' key containing a list of component dicts.
        updates (dict): A dictionary where keys are the 'field' names to
            update and values are the new values.

    Returns:
        dict: The modified deployment record dictionary.

    Usage Example:
        rec = {
            'components': [{'field': 'user', 'value': 'old_user'}]
        }
        updates = {'user': 'new_user'}
        updated_rec = update_component_values(rec, updates)
        # updated_rec['components'][0]['value'] is now 'new_user'
    """
    for component in rec.get(COMPONENTS_FIELD, []):
        field = component.get(FIELD_FIELD)
        if field in updates:
            component[VALUE_FIELD] = updates[field]
    return rec

def worst_status(results):
    worst_status = GOOD_FIELD
    for line_item in results:
        for key in line_item:
            if line_item[key]["status"] == ERROR_FIELD:
                return ERROR_FIELD
            elif line_item[key]["status"] == WARN_FIELD:
                worst_status = WARN_FIELD

    return worst_status
    
