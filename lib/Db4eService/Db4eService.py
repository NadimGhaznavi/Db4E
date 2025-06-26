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
import signal
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

POLL_INTERVAL = 10

class Db4eService:

    def __init__(self):
        self.ini = Db4eConfig()
        self.osdb = Db4eOSDb()
        self.log = Db4eLogger('Db4eService')
        self.model = Db4eOSModel()

        self.running = threading.Event()
        self.running.set()

        self.p2pool_monitors = {}
        self.xmrig_monitors = {}

        self.log.debug('db4e service initialized')

    def start(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        while self.running.is_set():
            self.check_deployments()
            time.sleep(POLL_INTERVAL)
        
        self.cleanup()

    def shutdown(self, signum, frame):
        # Ops DB event
        self.log.debug(f'Shutdown requested (signal {signum})')
        self.running.clear()

    def cleanup(self):
        for instance_id, (thread, stop_event) in self.p2pool_monitors.items():
            stop_event.set()
            thread.join()
            # Ops DB event
            self.log.debug(f'Stopped P2Pool monitor thread for {instance_id}')

        for instance_id, (thread, stop_event) in self.p2pool_monitors.items():
            stop_event.set()
            thread.join()
            # Ops DB event
            self.log.debug(f'Stopped XMRig monitor thread for {instance_id}')

    def check_deployments(self):
        for component in ['p2pool', 'xmrig']:
            depls = self.model.get_deployments_by_component(component)
            for depl in depls:
                if depl.get('remote'):
                    continue
                if depl.get('enable', False):
                    self.ensure_running(depl)
                else:
                    self.ensure_stopped(depl)

    def ensure_running(self, depl):
        # Check deployment type and spawn threads or start services
        component = depl['component']
        instance = depl['instance']
        print(f'Ensuring that {component}/{instance} is running')

    def ensure_stopped(self, depl):
        # TODO
        print(f"Ensuring that {depl['component']}/{depl['instance']} is stopped")

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
