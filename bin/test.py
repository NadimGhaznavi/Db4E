#!/opt/qa/db4e/venv/bin/python
"""
bin/test.py

Test program used for debugging.


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

  You should have received a copy (LICENSE.txt) of the GNU General 
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""


# Import supporting modules
import os
import sys
import socket
import json

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..', 'lib')
sys.path.append(lib_dir)

# Import DB4E modules
#from Db4eOSModel.Db4eOSModel import Db4eOSModel
#from Db4eClient.Db4eClient import Db4eClient
#from Db4eOSInitialSetupUI.Db4eOSInitialSetupUI import Db4eOSInitialSetupUI
#from Db4eOSP2PoolRemoteEditUI.Db4eOSP2PoolRemoteEditUI import Db4eOSP2PoolRemoteEditUI
from Db4eSystemd.Db4eSystemd import Db4eSystemd

systemd = Db4eSystemd('db4e')
print(f"Active: {systemd.active()}")
print(f"PID: {systemd.pid()}")
print(f"Enabled: {systemd.enabled()}")
print(f"STDOUT:\n{systemd.stdout()}")
print(f"STDERR:\n{systemd.stderr()}")
print("Disabling...")
systemd.disable()
print(f"Active: {systemd.active()}")
print(f"PID: {systemd.pid()}")
print(f"Enabled: {systemd.enabled()}")
print("Enabling...")
systemd.enable()
print(f"Active: {systemd.active()}")
print(f"PID: {systemd.pid()}")
print(f"Enabled: {systemd.enabled()}")
