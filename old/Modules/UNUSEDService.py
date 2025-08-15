"""
db4e/Modules/Db4eService.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

The Db4E Service, started and stopped using 'systemctl [start|stop] db4e'.
"""
import os
import signal
import time
import subprocess
import threading

from db4e.Modules.ConfigMgr import Config, ConfigMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.Db4eSystemd import Db4eSystemd
from db4e.Constants.Fields import(
    COMPONENT_FIELD, P2POOL_FIELD, TERM_ENVIRON_FIELD, 
    COLORTERM_ENVIRON_FIELD, P2POOL_FIELD, DB4E_FIELD, DB4E_REFRESH_FIELD,
    XMRIG_FIELD, INSTANCE_FIELD, OP_FIELD, ENABLE_FIELD, DISABLE_FIELD,
    DELETE_FIELD, REMOTE_FIELD, STATUS_FIELD, RUNNING_FIELD, STOPPED_FIELD
    )
from db4e.Constants.Defaults import(
    TERM_DEFAULT, COLORTERM_DEFAULT
)

class Db4eService:

    def __init__(self, config = Config):
        self.ini = config
        self.refresh = self.ini.config[DB4E_FIELD][DB4E_REFRESH_FIELD]
        self.depl_mgr = DeploymentMgr(config=config)
        self.systemd = Db4eSystemd(DB4E_FIELD)
        self.running = threading.Event()
        self.running.set()

        self.p2pool_monitors = {}
        print(f"Db4E service initialized")

    def process_queue(self):
        print(f"🛠️ Processing op {op['transaction_id']}...")
        

    def cleanup(self):
        for instance_id, (thread, stop_event) in self.p2pool_monitors.items():
            stop_event.set()
            thread.join()
            # Ops DB event
            print(f'Stopped P2Pool monitor thread for {instance_id}')

    def ensure_running(self, depl):
        # Check if the deployment service is running, start it if it's not
        component = depl[COMPONENT_FIELD]
        instance = depl[INSTANCE_FIELD]
        sd = self.systemd
        sd.service_name(component + '@' + instance)
        if not sd.active():
            rc = sd.start()
            if rc == 0:
                self.depl_mgr.update_deployment(
                    component, instance, {STATUS_FIELD: RUNNING_FIELD})
                print(f'Started {component}/{instance}')
            else:
                print(f'ERROR: Failed to start {component}/{instance}, return code was {rc}')

    def ensure_stopped(self, depl):
        sd = self.systemd
        component = depl[COMPONENT_FIELD]
        instance = depl[INSTANCE_FIELD]
        sd.service_name(component + '@' + instance)
        if sd.active():
            rc = sd.stop()
            if rc == 0:
                self.depl_mgr.update_deployment(
                    component, instance, {STATUS_FIELD: STOPPED_FIELD})
                print(f'Stopped {component}/{instance}')
            else:
                print(f'ERROR: Failed to stop {component}/{instance}, return code was {rc}')

    def launch_p2pool_monitor(self):
        p2pools = self.depl_mgr.get_deployment(P2POOL_FIELD)


    def launch_p2pool_writer(self):
        # Send 'status' and 'workers' commands to local P2Pool deployments
        def writer_loop():
            while True:
                try:
                    deployments = self.depl_mgr.get_deployments(P2POOL_FIELD)
                    for depl in deployments:
                        if depl[REMOTE_FIELD]:
                            continue
                        pipe = 'DEBUG' # depl['instance'])
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
        
    def start(self):
        print(f"Db4eService:start()")
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        while self.running.is_set():
            self.proces_queue()
            time.sleep(self.refresh)
        self.cleanup()

    def shutdown(self, signum, frame):
        self.running.clear()

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
        if 'component' == P2POOL_FIELD:
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

def main():
    # Set environment variables for better color support
    os.environ[TERM_ENVIRON_FIELD] = TERM_DEFAULT
    os.environ[COLORTERM_ENVIRON_FIELD] = COLORTERM_DEFAULT

    config_manager = ConfigMgr(__version__)
    config = config_manager.get_config()
    app = Db4eService(config)
    app.start()

if __name__ == "__main__":
    main()