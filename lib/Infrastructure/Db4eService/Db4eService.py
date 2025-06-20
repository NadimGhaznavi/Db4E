"""
lib/Infrastructure/Db4eService/Db4eService.py

This module is encapsulates the db4e service. The service is
responsible for monitoring the P2Pool log file and performing
start/stop operations on the deployed components.


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
import subprocess


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

class Db4eService:

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
        self.fq_uds = os.path.join(vendor_dir, vendor_db4e_dir, run_dir, uds)

        # Make sure there's no old socket still there
        if os.path.exists(self.fq_uds):
            os.remove(self.fq_uds)

    def listen(self):
        # Create the UDS and start handling requests
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(self.fq_uds)
        server.listen(1)

        # TODO replace with logging
        print("The db4e service API is up and listening for requests...")

        try:
            while True:
                conn, _ = server.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        continue
                    try:
                        request = json.loads(data.decode())
                        if request.get('op') == 'ping':
                            response = {'result': 'pong'}
                        elif request.get('op') == 'start':
                            component = request.get('component')
                            instance = request.get('instance')
                            response_msg = f'Starting {component} - {instance}'
                            response = {'result': response_msg}
                            self.spawn_process(component, instance)
                        else:
                            response = {'error': 'Unknown op'}
                    except Exception as e:
                        response = {'error': str(e)}

                    conn.sendall(json.dumps(response).encode())
        finally:
            server.close()
            os.remove(self.fq_uds)

    def spawn_process(self, component, instance):
        #print(f'DEBUG Starting {component} - {instance}')
        try:
            fq_stdin = self._osDb.get_deployment_stdin(component, instance)
            stdin = open(fq_stdin, 'r')
            # Get the component's start script and configuration file
            vendor_dir = self._osDb.get_vendor_dir()
            bin_dir = self.ini.config['db4e']['bin_dir']
            version = self.ini.config[component]['version']
            component_dir = component + '-' + str(version)
            start_script = self.ini.config[component]['start_script']
            fq_start_script = os.path.join(vendor_dir, component_dir, bin_dir, start_script)
            config = self._osDb.get_deployment_config(component, instance)
            # Spawn the process, detached from the service process
            print(f'DEBUG {fq_start_script} {config}')
            subprocess.Popen(
                [ fq_start_script, config ],
                stdin=stdin,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid # Detach from parent process
            )
        except Exception as e:
            pass
            #print(f"Error spawning {component} - {instance}: {e}")
