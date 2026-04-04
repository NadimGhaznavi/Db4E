"""
db4e/Modules/Db4ESystemd.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

# Import supporting modules
import time
from pystemd.systemd1 import Manager, Unit

from db4e.db.OpsDb import OpsDb

from db4e.constants.DSystemD import DSystemD
from db4e.constants.DElem import DElem
from db4e.constants.DLabel import DLabel


# How long to wait until timing out
TIMEOUT = 30


class Db4ESystemD:
    """
    Helper for controlling and querying systemd services.
    """

    def __init__(self, ops_db: OpsDb, service_name=None):
        """
        Initialize the systemd helper.

        :param ops_db: Operations database handle for runtime logs.
        :type ops_db: OpsDb
        :param service_name: Optional systemd service name.
        :type service_name: str or None
        :return: None
        :rtype: None
        """
        # Make sure systemd doesn't clutter the output with color codes or use a pager
        self.ops_db = ops_db
        if service_name:
            self._service_name = service_name + DSystemD.SERVICE_SUFFIX
            self._unit = Unit(self._service_name.encode(), _autoload=True)
        else:
            self._service_name = None

        self._mgr = Manager()
        self._mgr.load()

    def disable(self):
        """
        Disable the service.

        :return: systemctl return code.
        :rtype: int
        """
        self._mgr.EnableUnitFiles(files=[self._service_name.encode()], runtime=False)

    def enable(self):
        """
        Enable the service.

        :return: systemctl return code.
        :rtype: int
        """
        self._mgr.EnableUnitFiles(
            files=[self._service_name.encode()], runtime=False, force=True
        )

    def enabled(self):
        """
        Return a boolean indicating if the service is running or not.

        :return: True if service is active.
        :rtype: bool or None
        """
        state = self._unit.Unit.ActiveState.decode()
        if state == DSystemD.ACTIVE:
            return True
        elif state == DSystemD.INACTIVE:
            return False
        else:
            raise ValueError(f"ERROR: Invalid service state: {state}")

    def log_event(self, service_name, event):
        """
        Log a start/stop event to the ops database.

        :param service_name: Service name with instance suffix.
        :type service_name: str
        :param event: Event type (start/stop).
        :type event: str
        :return: None
        :rtype: None
        """
        elem_type, instance = service_name.split("@")
        # Map the field names to the labels for the Runtime Log
        TYPE_TABLE = {
            DElem.MONEROD: DLabel.MONEROD,
            DElem.P2POOL: DLabel.P2POOL,
            DElem.XMRIG: DLabel.XMRIG,
        }
        if event == DSystemD.START:
            self.ops_db.add_start_event(elem_type=elem_type, instance=instance)
        elif event == DSystemD.STOP:
            self.ops_db.add_stop_event(elem_type=elem_type, instance=instance)

    def pid(self):
        """
        Return the PID of a running service.

        :return: PID of the service.
        :rtype: int or None
        """
        return self._unit.Service.MainPID

    def restart(self):
        """
        Restart a service.

        :return: None
        :rtype: None
        """
        self._unit.Unit.Stop(DSystemD.REPLACE.encode())
        time.sleep(1)
        self._unit.Unit.Start(DSystemD.REPLACE.encode())

    def running(self):
        """
        Check if a service is running.

        :return: Flag
        :rtype: bool
        """
        return (
            self._unit.Unit.ActiveState == b"active"
            and self._unit.Unit.SubState == b"running"
        )

    def service_name(self, service_name=None):
        """
        Get/Set the service_name.

        :param service_name: Optional service name to set.
        :type service_name: str or None
        :return: Current service name.
        :rtype: str or None
        """
        if service_name:
            self._service_name = service_name + DSystemD.SERVICE_SUFFIX
            self._unit = Unit(self._service_name.encode(), _autoload=True)
        return self._service_name

    def start(self):
        """
        Start a systemd service.

        :return: systemctl return code.
        :rtype: int
        """
        self._unit.Unit.Start(DSystemD.REPLACE.encode())

    def stop(self):
        """
        Stop a systemd service.

        :return: systemctl return code.
        :rtype: int
        """
        self._unit.Unit.Stop(DSystemD.REPLACE.encode())
