"""
lib/Infrastructure/Db4eClient/Db4eClient.py

This module is encapsulates the db4e client. The client is
responsible for handling the communication with the Db4eService.


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


# Supporting modules
import os, sys
import socket
import json


# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
    lib_dir + 'Infrastructure',
    lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
    sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eOSDb.Db4eOSDb import Db4eOSDb

class Db4eClient:

    def __init__(self):
        self.ini = Db4eConfig()
        self._osDb = Db4eOSDb()
        # Set the location of the socket
        db4e_version = self.ini.config['db4e']['version']
        vendor_dir = self._osDb.get_vendor_dir()
        vendor_db4e_dir = 'db4e-' + db4e_version
        run_dir = self.ini.config['db4e']['run_dir']
        if not os.path.exists(os.path.join(vendor_dir, vendor_db4e_dir)):
            os.mkdir(os.path.join(vendor_dir, vendor_db4e_dir))
        if not os.path.exists(os.path.join(vendor_dir, vendor_db4e_dir, run_dir)):
            os.mkdir(os.path.join(vendor_dir, vendor_db4e_dir, run_dir))
        uds = self.ini.config['db4e']['uds']
        self.socket = os.path.join(vendor_dir, vendor_db4e_dir, run_dir, uds)

    def _send_msg(self, msg):
        try:

            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.socket)
            client.sendall(msg.encode())
            # Handle larger messages
            data = b''
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
                if len(data) < 4096:
                    break
            # Close the connection and return the results
            client.close()
            return json.loads(data.decode())
        
        except Exception as e:
            return {'error': str(e)}


    def start(self, component, instance):
        msg = json.dumps({'op': 'start', 'component': component, 'instance': instance})
        return self._send_msg(msg)

