"""
lib/Db4eService/Db4eService.py

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
import time
import threading

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eOSDb.Db4eOSDb import Db4eOSDb
from Db4eLogger.Db4eLogger import Db4eLogger
from Db4eOSModel.Db4eOSModel import Db4eOSModel

class Db4eService:

    def __init__(self):
        self.ini = Db4eConfig()
        self.osdb = Db4eOSDb()
        self.log = Db4eLogger('Db4eService')
        self.model = Db4eOSModel()
        # Set the location of the socket
        db4e_version = self.ini.config['db4e']['version']
        vendor_dir = self.osdb.get_dir('vendor')
        vendor_db4e_dir = 'db4e-' + db4e_version
        run_dir = self.ini.config['db4e']['run_dir']
        if not os.path.exists(os.path.join(vendor_dir, vendor_db4e_dir)):
            os.mkdir(os.path.join(vendor_dir, vendor_db4e_dir))
        if not os.path.exists(os.path.join(vendor_dir, vendor_db4e_dir, run_dir)):
            os.mkdir(os.path.join(vendor_dir, vendor_db4e_dir, run_dir))
        uds = self.ini.config['db4e']['uds']
        self.fq_uds = os.path.join(vendor_dir, vendor_db4e_dir, run_dir, uds)

        # Keep track of the threads we're spawning
        self.p2pool_writer_threads = {}

        # Delete old socket if it's there
        if os.path.exists(self.fq_uds):
            os.remove(self.fq_uds)
        # Start sending commands to the P2Pool STDIN pipe
        self.launch_p2pool_writer()
        # Start monitoring local P2Pool instances for mining data
        self.launch_p2pool_monitor()

    def listen(self):
        # Create the UDS and start handling requests
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(self.fq_uds)
        server.listen(1)

        self.log.info("The db4e service API is up and listening for requests...")

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
                            response = self.start_instance(component, instance)
                        elif request.get('op') == 'stop':
                            component = request.get('component')
                            instance = request.get('instance')
                            response = self.stop_instance(component, instance)
                        else:
                            response = {'error': 'Unknown op'}
                    except Exception as e:
                        response = {'error': str(e)}

                    conn.sendall(json.dumps(response).encode())
        finally:
            server.close()
            os.remove(self.fq_uds)

    def launch_p2pool_monitor(self):
        p2pools = self.osdb.get_deployments_by_component('p2pool')


    def launch_p2pool_writer(self):
        # Send 'status' and 'workers' commands to local P2Pool deployments
        def writer_loop():
            while True:
                try:
                    deployments = self.osdb.get_deployments_by_component('p2pool')
                    for depl in deployments:
                        if depl['remote']:
                            continue
                        pipe = self.model.get_deployment_stdin('p2pool', depl['instance'])
                        if not os.path.exists(pipe):
                            continue
                        with open(pipe, 'w') as fifo:
                            fifo.write("status\n")
                            fifo.flush()
                        time.sleep(30)
                        with open(pipe, 'w') as fifo:
                            fifo.write("workers\n")
                            fifo.flush()
                except Exception as e:
                    self.log.critical(f"Writer loop error: {e}")
                time.sleep(30)

        thread = threading.Thread(target=writer_loop, daemon=True)
        thread.start()

    def start_instance(self, component, instance):
        try:
            # If the user is playing with the startup options, it's not uncommon for the service
            # socket (monerod and p2pool) to be created, but the service isn't running. 
            # Subsequent attempts to start the service will fail. So, if the socket exists
            # delete it before starting the service.
            fq_socket = self.model.get_deployment_stdin(component, instance)
            if fq_socket and os.path.exists(fq_socket):
                os.remove(fq_socket)
            systemd_instance = component + '@' + instance
            cmd_result = subprocess.run(
                ['sudo', 'systemctl', 'start', systemd_instance],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()
            if cmd_result.returncode == 0:
                return { 'result': 'started', 'msg': stdout}
            else:
                return { 'error': True, 'msg': stderr}
        except Exception as e:
            return {'error': True, 'msg': f'Error starting {component} - {instance}: {e}'}

    def stop_instance(self, component, instance):
        fq_socket = self.model.get_deployment_stdin(component, instance)
        if 'component' == 'p2pool':
            with open(fq_socket, 'w') as fifo:
                fifo.write("exit\n")
                fifo.flush()
            return {'result': True, 'msg': f'Write "exit" command to {fq_socket}'}
        try:
            systemd_instance = component + '@' + instance
            cmd_result = subprocess.run(
                ['sudo', 'systemctl', 'stop', systemd_instance],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()
            if cmd_result.returncode == 0:
                return { 'result': 'stopped', 'msg': stdout}
            else:
                return { 'result': 'failed', 'msg': stderr}
        except Exception as e:
            return {'error': True, 'msg': f'Error stopping {component} - {instance}: {e}'}
