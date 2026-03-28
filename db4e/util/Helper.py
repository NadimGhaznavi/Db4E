"""
db4e/Modules/Helper.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Helper functions that are used in multiple modules
"""

import os, grp, getpass, re, subprocess
from decimal import Decimal

from rich import box
from rich.table import Table

from db4e.constants.DStatus import DStatus
from db4e.constants.DField import DField
from db4e.constants.DFile import DFile


error_color = "#935fcf"
PICONEROS_PER_XMR = 1_000_000_000_000  # 10^12


def get_component_value(data, field_name):
    """
    Generic helper to get any component value by field name.

    :param data: Dictionary containing components with field/value pairs.
    :type data: dict
    :param field_name: The field name to search for.
    :type field_name: str
    :return: The component value, or None if not found.
    :rtype: object or None
    """
    if not isinstance(data, dict) or "components" not in data:
        return None

    components = data.get(DField.COMPONENTS, [])

    for component in components:
        if isinstance(component, dict) and component.get(DField.FIELD) == field_name:
            return component.get(DField.VALUE)

    return None


def get_effective_identity():
    """
    Return the effective user and group for the account running Db4E.

    :return: Mapping of user and group.
    :rtype: dict
    """
    # User account
    user = getpass.getuser()
    # User's group
    effective_gid = os.getegid()
    group_entry = grp.getgrgid(effective_gid)
    group = group_entry.gr_name
    return {DField.USER: user, DField.GROUP: group}


def get_remote_state(data):
    """
    Parse out the remote state from a data structure.

    :param data: Dictionary containing components with field/value pairs.
    :type data: dict
    :return: The remote state value, or None if not found.
    :rtype: bool or None
    """
    if not isinstance(data, dict) or "components" not in data:
        return None

    components = data.get(DField.COMPONENTS, [])

    for component in components:
        if isinstance(component, dict) and component.get(DField.FIELD) == DField.REMOTE:
            return component.get(DField.VALUE)

    return None


def gen_results_table(results):
    """
    Build a Rich table of result rows.

    :param results: List of result dictionaries.
    :type results: list
    :return: Rich table instance.
    :rtype: Table
    """

    table = Table(
        show_header=True, header_style="bold #31b8e6", style="#0c323e", box=box.SIMPLE
    )
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
                table.add_row(
                    f"💥 [b {error_color}]{category}[/]", f"[{error_color}]{message}[/]"
                )
    return table


def minutes_to_uptime(minutes: int):
    """
    Convert minutes into a compact uptime string.

    :param minutes: Uptime in minutes.
    :type minutes: int
    :return: Uptime string.
    :rtype: str
    """
    # Return a string like:
    # 0h 0m 45s
    # 1d 7h 32m
    days, minutes = divmod(int(minutes), 1440)
    hours, minutes = divmod(minutes, 60)
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def normalize_hashrate(hashrate, units):
    """
    Normalize a hashrate to H/s based on its units.

    :param hashrate: Hashrate value.
    :type hashrate: int or float or str
    :param units: Hashrate units (e.g., kH/s, MH/s).
    :type units: str
    :return: Normalized hashrate in H/s.
    :rtype: float
    """
    # Convert the hashrate units into H/s
    if units.lower() == "kh/s":
        hashrate = float(hashrate) * 1000
    elif units.lower() == "mh/s":
        hashrate = float(hashrate) * 1000_000
    elif units.lower() == "gh/s":
        hashrate = float(hashrate) * 1000_000_000
    else:
        hashrate = float(hashrate)
    return hashrate


def piconero_to_xmr(piconeros: int) -> Decimal:
    """
    Convert integer piconeros to human-readable XMR (as Decimal).

    :param piconeros: Amount in piconeros.
    :type piconeros: int
    :return: Amount in XMR.
    :rtype: Decimal
    """
    return Decimal(piconeros) / PICONEROS_PER_XMR


def result_row(label: str, status: str, msg: str):
    """
    Return a standardized result dict for display in Results pane.

    :param label: Result label.
    :type label: str
    :param status: Status string.
    :type status: str
    :param msg: Message string.
    :type msg: str
    :return: Result dictionary.
    :rtype: dict
    """
    assert status in {
        DStatus.GOOD,
        DStatus.WARN,
        DStatus.ERROR,
    }, f"invalid status: {status}"
    return {label: {"status": status, "msg": msg}}


def set_component_value(rec, updates):
    """
    Update multiple component values in a deployment record from a dictionary.

    This function iterates through the 'components' list of a given record.
    For each component, it checks if its 'field' name exists as a key in the
    'updates' dictionary. If it does, the component's 'value' is updated
    with the corresponding value from the 'updates' dictionary.

    The modification is done in-place on the 'rec' dictionary.

    :param rec: Deployment record dictionary to update.
    :type rec: dict
    :param updates: Mapping of field names to new values.
    :type updates: dict
    :return: The modified deployment record dictionary.
    :rtype: dict
    """
    for component in rec.get(DField.COMPONENTS, []):
        field = component.get(DField.FIELD)
        if field in updates:
            component[DField.VALUE] = updates[field]
    return rec


def split_timestamp(timestamp: str):
    """
    Split a timestamp into discrete components.

    :param timestamp: Timestamp string in "%Y-%m-%d %H:%M:%S" format.
    :type timestamp: str
    :return: (year, month, day, hour, minute, second) tuple.
    :rtype: tuple
    """
    year_month_day, hour_minute_second = timestamp.split(" ")
    year, month, day = year_month_day.split("-")
    hour, minute, second = hour_minute_second.split(":")
    return (year, month, day, hour, minute, second)


def sudo_del_file(aFile: str):
    """
    Remove a file using sudo, returning command output.

    :param aFile: Path to file to delete.
    :type aFile: str
    :return: Command result dictionary.
    :rtype: dict or None
    """
    if not os.path.exists(aFile):
        # Nothing to do
        return

    cmd = [DFile.SUDO, DFile.RM, "-f", aFile]
    try:
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=""
        )
        return {
            DField.STDOUT: proc.stdout.decode("utf-8"),
            DField.STDERR: proc.stderr.decode("utf-8"),
            DField.RC: proc.returncode,
        }
    except Exception as e:
        return {
            DField.STDOUT: proc.stdout.decode("utf-8"),
            DField.STDERR: proc.stderr.decode("utf-8"),
            DField.RC: proc.returncode,
        }


def uptime_to_minutes(uptime_str: str):
    """
    Convert an uptime string to total minutes.

    :param uptime_str: Uptime string (e.g., "1d 2h 3m 4s").
    :type uptime_str: str
    :return: Total minutes.
    :rtype: int
    :raises ValueError: If the format is invalid.
    """
    pattern = re.compile(r"(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?")
    match = pattern.fullmatch(uptime_str)
    if not match:
        raise ValueError(f"Unrecognized uptime format: {uptime_str}")

    days, hours, minutes, seconds = (int(x) if x else 0 for x in match.groups())

    total_minutes = days * 24 * 60 + hours * 60 + minutes
    # optionally: round up if seconds >= 30
    if seconds >= 30:
        total_minutes += 1

    return total_minutes


def xmr_to_piconero(xmr: float | str) -> int:
    """
    Convert an XMR value to integer piconeros (avoids float rounding).

    :param xmr: XMR amount.
    :type xmr: float or str
    :return: Amount in piconeros.
    :rtype: int
    """
    return int(Decimal(str(xmr)) * PICONEROS_PER_XMR)
