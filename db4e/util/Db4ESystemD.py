"""
db4e/Modules/Db4ESystemd.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

# Import supporting modules
import os
import subprocess
import re
import time

from db4e.db.OpsDb import OpsDb

from db4e.constants.DField import DField
from db4e.constants.DSystemD import DSystemD
from db4e.constants.DFile import DFile
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
        os.environ[DField.SYSTEMD_COLORS] = "0"
        os.environ[DField.SYSTEMD_PAGER] = ""
        self.result = {
            DSystemD.ACTIVE: None,
            DSystemD.PID: None,
            DSystemD.ENABLED: None,
            DSystemD.RAW_STDOUT: "",
            DSystemD.RAW_STDERR: "",
        }
        if service_name:
            self._service_name = service_name
        else:
            self._service_name = None
        self.status()

    def active(self):
        """
        Return a boolean indicating if the service is running or not.

        :return: True if service is active.
        :rtype: bool or None
        """
        self.status()
        return self.result[DSystemD.ACTIVE]

    def disable(self):
        """
        Disable the service.

        :return: systemctl return code.
        :rtype: int
        """
        return self._run_systemd(DSystemD.DISABLE)

    def enable(self):
        """
        Enable the service.

        :return: systemctl return code.
        :rtype: int
        """
        return self._run_systemd(DSystemD.ENABLE)

    def enabled(self):
        """
        Return a boolean indicating if a service is enabled or not.

        :return: True if service is enabled.
        :rtype: bool or None
        """
        return self.result[DSystemD.ENABLED]

    def installed(self):
        """
        Return a boolean indicating if the service is present at all.

        :return: True if service is installed.
        :rtype: bool
        """
        if self.stderr():
            return False
        return True

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
        return self.result[DSystemD.PID]

    def restart(self):
        """
        Restart a service.

        :return: None
        :rtype: None
        """
        self.stop()
        time.sleep(1)
        self.start()

    def service_name(self, service_name=None):
        """
        Get/Set the service_name.

        :param service_name: Optional service name to set.
        :type service_name: str or None
        :return: Current service name.
        :rtype: str or None
        """
        old_service_name = self._service_name
        if service_name:
            self._service_name = service_name
            if service_name != old_service_name:
                self.status()
        return self._service_name

    def start(self):
        """
        Start a systemd service.

        :return: systemctl return code.
        :rtype: int
        """
        return self._run_systemd(DSystemD.START)

    def status(self):
        """
        (Re)load the instance's result's dictionary.

        :return: None
        :rtype: None
        """

        self._run_systemd(DSystemD.STATUS)
        stdout = self.stdout()
        stderr = self.stderr()

        if "could not be found" in stderr:
            return

        # print(f"Db4ESystemD:status(): stdout: {stdout}")
        # Check for active state
        if re.search(r"^\s*Active:\s+active \(running\).*", stdout, re.MULTILINE):
            self.result[DSystemD.ACTIVE] = True
        elif re.search(r"^\s*Active:\s+inactive \(dead\).*", stdout, re.MULTILINE):
            self.result[DSystemD.ACTIVE] = False
        elif re.search(r"^\s*Active:\s+failed.*", stdout, re.MULTILINE):
            self.result[DSystemD.ACTIVE] = False

        # Check for enabled state
        if re.search(r"Loaded: .*; enabled;", stdout):
            self.result[DSystemD.ENABLED] = True
        elif re.search(r"Loaded: .*; disabled;", stdout):
            self.result[DSystemD.ENABLED] = False

        # Get PID
        pid_match = re.search(r"^\s*Main PID:\s+(\d+)", stdout, re.MULTILINE)
        if pid_match and self.result[DSystemD.ACTIVE]:
            self.result[DSystemD.PID] = int(pid_match.group(1))

    def stdout(self):
        """
        Return the raw STDOUT of a 'systemctl status service_name' command.

        :return: Raw stdout string.
        :rtype: str
        """
        return self.result[DSystemD.RAW_STDOUT]

    def stderr(self):
        """
        Return the raw STDERR of a 'systemctl status service_name' command.

        :return: Raw stderr string.
        :rtype: str
        """
        return self.result[DSystemD.RAW_STDERR]

    def stop(self):
        """
        Stop a systemd service.

        :return: systemctl return code.
        :rtype: int
        """
        return self._run_systemd(DSystemD.STOP)

    def _run_systemd(self, arg):
        """
        Execute a 'systemd [start|stop|status|enable|disable] service_name' command and load the
        instance's result dictionary.

        :param arg: systemctl action argument.
        :type arg: str
        :return: systemctl return code.
        :rtype: int
        """
        if arg == DSystemD.STATUS:
            cmd = [DFile.SYSTEMCTL, arg, self._service_name]
        else:
            cmd = [DFile.SUDO, DFile.SYSTEMCTL, arg, self._service_name]

        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input="",
                timeout=TIMEOUT,
            )
            stdout = proc.stdout.decode(errors="replace")
            stderr = proc.stderr.decode(errors="replace")

        except subprocess.TimeoutExpired:
            self.result[DSystemD.RAW_STDERR] = "systemctl timed out"
            return 5

        except Exception as e:
            self.result[DSystemD.RAW_STDERR] = str(e)
            return 5

        self.result[DSystemD.RAW_STDOUT] = stdout
        self.result[DSystemD.RAW_STDERR] = stderr

        if arg == DSystemD.ENABLE or arg == DSystemD.DISABLE:
            # Reload the status information
            self.status()

        if proc.returncode == 0 and arg == DSystemD.START:
            self.log_event(event=DSystemD.START, service_name=self._service_name)
            time.sleep(30)
        elif proc.returncode == 0 and arg == DSystemD.STOP:
            self.log_event(event=DSystemD.STOP, service_name=self._service_name)

        # Return the return code for the systemctl command
        return proc.returncode
