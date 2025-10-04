"""
db4e/Modules/Helper.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Helper functions that are used in multiple modules   
"""
import os, grp, getpass, re

from rich import box
from rich.table import Table

from db4e.Constants.DStatus import DStatus
from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel
   


error_color = "#935fcf"


def del_config(config_file: str):
    results = []
    try:
        os.remove(config_file)
        results.append(result_row(
            DLabel.XMRIG, DStatus.GOOD,
            f"Removed old configration file: {config_file}"
        ))
    except OSError as e:
        result_row.append(result_row(
            DLabel.XMRIG, DStatus.WARN,
            f"Unable to remove {config_file} {e} "
        ))
    return results


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
    
    components = data.get(DField.COMPONENTS, [])
    
    for component in components:
        if isinstance(component, dict) and component.get(DField.FIELD) == field_name:
            return component.get(DField.VALUE)
    
    return None


def get_effective_identity():
    """Return the effective user and group for the account running Db3e"""
    # User account
    user = getpass.getuser()
    # User's group
    effective_gid = os.getegid()
    group_entry = grp.getgrgid(effective_gid)
    group = group_entry.gr_name
    return { DField.USER: user, DField.GROUP: group }


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
    
    components = data.get(DField.COMPONENTS, [])
    
    for component in components:
        if isinstance(component, dict) and component.get(DField.FIELD) == DField.REMOTE:
            return component.get(DField.VALUE)
    
    return None


def gen_results_table(results):
    
    table = Table(show_header=True, header_style="bold #31b8e6", style="#0c323e", box=box.SIMPLE)
    table.add_column("Component", width=25)
    table.add_column("Details")

    for item in results:
        for category, msg_dict in item.items():
            message = msg_dict[DField.MESSAGE]
            if msg_dict[DField.STATUS] == DStatus.GOOD:
                table.add_row(f"✅ [bold]{category}[/]", f"{message}")
            elif msg_dict[DField.STATUS] == DStatus.WARN:
                table.add_row(f"⚠️  [yellow]{category}[/]", f"[yellow]{message}[/]")
            elif msg_dict[DField.STATUS] == DStatus.ERROR:
                table.add_row(f"💥 [b {error_color}]{category}[/]", f"[{error_color}]{message}[/]")
    return table


def result_row(label: str, status: str, msg:str ):
    """Return a standardized result dict for display in Results pane."""
    assert status in {DStatus.GOOD, DStatus.WARN, DStatus.ERROR}, f"invalid status: {status}"
    return {label: {'status': status, 'msg': msg}}


def set_component_value(rec, updates):
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
    for component in rec.get(DField.COMPONENTS, []):
        field = component.get(DField.FIELD)
        if field in updates:
            component[DField.VALUE] = updates[field]
    return rec


def uptime_to_minutes(uptime_str: str):
    pattern = re.compile(r'(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?')
    match = pattern.fullmatch(uptime_str)
    if not match:
        raise ValueError(f"Unrecognized uptime format: {uptime_str}")

    days, hours, minutes, seconds = (int(x) if x else 0 for x in match.groups())

    total_minutes = days * 24 * 60 + hours * 60 + minutes
    # optionally: round up if seconds >= 30
    if seconds >= 30:
        total_minutes += 1
    
    return total_minutes


def minutes_to_uptime(minutes: int):
    # Return a string like:
    # 0h 0m 45s
    # 1d 7h 32m
    days, minutes = divmod(minutes, 1440)
    hours, minutes = divmod(minutes, 60)
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"