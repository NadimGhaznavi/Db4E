"""
lib/Db4eSystemd/Db4eSystemd.py

This is a wrapper to for systemctl status, start and stop commands.


  This file is part of *db4e*, the *Database 4 Everything* project
  <https://github.com/NadimGhaznavi/db4e>, developed independently
  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
  <https://github.com/NadimGhaznavi/db4e>.
 
  This program is free software: you can redistribute it and/or 
  modify it under the terms of the GNU General Public License as 
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received aLine copy (LICENSE.txt) of the GNU General 
  if match:
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""
# Import supporting modules
import os, sys
import subprocess
import re
import time

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules

# How long to wait until timing out
TIMEOUT = 30

class Db4eSystemd:

    def __init__(self, service_name):
        # Make sure systemd doesn't clutter the output with color codes or use a pager
        os.environ['SYSTEMD_COLORS'] = '0'
        os.environ['SYSTEMD_PAGER'] = ''
        self.result = {
            'active': None,
            'pid': None,
            'enabled': None,
            'raw_stdout': '',
            'raw_stderr': ''
        }
        self.service_name = service_name
        self.status()

    def active(self):
        """
        Return a boolean indicating if the service is running or not.
        """
        return self.result['active']

    def disable(self):
        """
        Disable the service.
        """
        self._run_systemd('disable')

    def enable(self):
        """
        Enable the service.
        """
        self._run_systemd('enable')

    def enabled(self):
        """
        Return a boolean indicating if a service is enabled or not.
        """
        return self.result['enabled']
    
    def installed(self):
        """
        Return a boolean indicating if the service is present at all.
        """
        if self.stderr():
            return False
        return True
    
    def pid(self):
        """
        Return the PID of a running service.
        """
        return self.result['pid']

    def restart(self):
        """
        Restart a service.
        """
        self.stop()
        time.sleep(1)
        self.start()

    def service_name(self, service_name=None):
        """
        Get/Set the service_name.
        """
        old_service_name = self.service_name
        if service_name:
            self.service_name = service_name
            if service_name != old_service_name:
                self.status()
        return service_name

    def start(self):
        """
        Start a systemd service.
        """
        self._run_systemd('start')

    def status(self):
        """
        (Re)load the instance's result's dictionary.
        """

        self._run_systemd('status')
        stdout = self.stdout()
        stderr = self.stderr()

        if 'could not be found' in stderr:
            return

        # Check for active state
        if re.search(r'^\s*Active:\s+active \(running\)', stdout, re.MULTILINE):
            self.result['active'] = True
        elif re.search(r'^\s*Active:\s+inactive \(dead\)', stdout, re.MULTILINE):
            self.result['active'] = False
        elif re.search(r'^\s*Active:\s+failed ', stdout, re.MULTILINE):
            self.result['active'] = False

        # Check for enabled state
        if re.search(r'Loaded: .*; enabled;', stdout):
            self.result['enabled'] = True
        elif re.search(r'Loaded: .*; disabled;', stdout):
            self.result['enabled'] = False

        # Get PID
        pid_match = re.search(r'^\s*Main PID:\s+(\d+)', stdout, re.MULTILINE)
        if pid_match and self.result['active']:
            self.result['pid'] = int(pid_match.group(1))

    def stdout(self):
        """
        Return the raw STDOUT of a 'systemctl status service_name' command.
        """
        return self.result['raw_stdout']
    
    def stderr(self):
        """
        Return the raw STDERR of a 'systemctl status service_name' command.
        """
        return self.result['raw_stderr']
    
    def stop(self):
        """
        Stop a systemd service.
        """
        self._run_systemd('stop')

    def _run_systemd(self, arg):
        """
        Execute a 'systemd [start|stop|status] service_name' command and load the
        instance's result dictionary.
        """
        # systemctl [enable|disable] requires sudo access
        if arg == 'enable' or arg == 'disable':
            cmd = ['sudo', 'systemctl', arg, self.service_name]
        else:
            cmd = ['systemctl', arg, self.service_name]
            
        try:
            proc = subprocess.run(cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  input='',
                                  timeout=TIMEOUT)
            stdout = proc.stdout.decode(errors='replace')
            stderr = proc.stderr.decode(errors='replace')

        except subprocess.TimeoutExpired:
            self.result['raw_stderr'] = 'systemctl timed out'

        except Exception as e:
            self.result['raw_stderr'] = str(e)

        self.result['raw_stdout'] = stdout
        self.result['raw_stderr'] = stderr

        if arg == 'enable' or arg == 'disable':
            # Reload the status information
            self.status()
