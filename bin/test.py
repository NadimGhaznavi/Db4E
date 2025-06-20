#!/opt/qa/db4e/venv/bin/python
"""
bin/db4e-purge-logs.py

This is a utility program that purges old log records from MongoDB.
This *only* purges log records. It does not touch the mining,
deployment or other MongoDB collections. This is basic housekeeping.
"""


"""
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


# The directory that this script is in
script_dir = os.path.dirname(__file__)
# DB4E modules are in the lib_dir
lib_dir = script_dir + '/../lib/'

# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eOS.Db4eOS import Db4eOS
from Db4eOSModel.Db4eOSModel import Db4eOSModel

db_os = Db4eOSModel()
results = db_os.get_status('db4e')
for aResult in results:
  print(aResult)
"""
SOCKET_PATH = '/home/sally/vendor/db4e-latest/run/db4e.sock'

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(SOCKET_PATH)

msg = json.dumps({"op": "ping"})
client.sendall(msg.encode())

data = client.recv(1024)
response = json.loads(data.decode())

print("Response from db4e service:", response)

client.close()
"""

