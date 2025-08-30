"""
db4e/server.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

import os, sys
import time
import signal
import threading
from importlib import metadata
from shutil import rmtree

try:
    __package_name__ = metadata.metadata(__package__ or __name__)["Name"]
    __version__ = metadata.version(__package__ or __name__)
except Exception:
    __package_name__ = "Db4E"
    __version__ = "N/A"

from db4e.Modules.Db4eLogger import Db4eLogger
from db4e.Modules.JobQueue import JobQueue
from db4e.Modules.Job import Job
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.Db4E import Db4E
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig
from db4e.Modules.Db4ESystemD import Db4ESystemD
from db4e.Constants.Defaults import (
    TERM_DEFAULT, COLORTERM_DEFAULT, DB4E_SERVER_DEFAULT, LOG_DIR_DEFAULT, DB4E_LOG_FILE_DEFAULT)
from db4e.Constants.Fields import (
    DB4E_FIELD, DISABLE_FIELD, VENDOR_DIR_FIELD, TERM_ENVIRON_FIELD, XMRIG_FIELD,
    COLORTERM_ENVIRON_FIELD, ENABLE_FIELD, P2POOL_FIELD)
from db4e.Constants.Jobs import DELETE_FIELD, UPDATE_FIELD, MESSAGE_FIELD

POLL_INTERVAL = 5

class Db4eServer:
    """
    Db4E Server
    """
    def __init__(self):

        # Get an ops manager
        self.ops_mgr = OpsMgr()

        # Get a deployment manager
        self.depl_mgr = DeploymentMgr()

        # Get a systemd object
        self.systemd = Db4ESystemD(DB4E_FIELD)

        # Get a db manager
        self.db = DbMgr()

        # Setup logging
        vendor_dir = self.depl_mgr.get_dir(VENDOR_DIR_FIELD)
        logs_dir = LOG_DIR_DEFAULT
        log_file = DB4E_LOG_FILE_DEFAULT
        fq_log_file = os.path.join(vendor_dir, DB4E_FIELD, logs_dir, log_file)    
        self.log = Db4eLogger(
            elem_type=DB4E_SERVER_DEFAULT,
            log_file=fq_log_file
        )

        # Get a JobQueue
        self.job_queue = JobQueue(db=self.db, log=self.log)

        self.running = threading.Event()
        self.running.set()


    def check_deployments(self):
        depls = self.depl_mgr.get_deployments()
        for depl in depls:
            depl_type = type(depl)
            if depl_type == Db4E or depl_type == MoneroDRemote or depl_type == P2PoolRemote:
                continue # We conly control the local deployments and Db4E is never started/stoped here

            print(f"Db4eServer:check_deployments(): {depl}")
            if depl is not None and depl.enabled():
                self.ensure_running(depl)
            else:
                self.ensure_stopped(depl)


    def check_jobs(self):
        self.log.info("Checking jobs:")
        jobs = []
        found_job = True
        while found_job:
            job = self.job_queue.grab_job()
            if job:
                jobs.append(job)
            else:
                found_job = False
        
        for job in jobs:
            #print(f"Db4eServer:check_jobs(): job.elem(): {job.elem()}")
            op = job.op()
            if op == ENABLE_FIELD:
                self.enable(job=job)
            elif op == DISABLE_FIELD:
                self.disable(job=job)
            elif op == DELETE_FIELD:
                self.delete(job=job)
            elif op == UPDATE_FIELD:
                self.update(job=job)



    def delete(self, job: Job):
        elem_type = job.elem_type()
        instance = job.instance()
        self.log.info(f"Deleting {elem_type}/{instance}")
        elem = self.depl_mgr.get_deployment(elem_type, instance)
        if type(elem) == XMRig:
            self.ensure_stopped(elem)
            config_file = elem.config_file()
            os.remove(config_file)
            self.depl_mgr.del_deployment(elem)
            job.msg("Deleted")
            self.job_queue.complete_job(job=job)
        elif type(elem) == P2Pool:
            print(f"Db4eServer:delete(): {elem}")
            self.ensure_stopped(elem)
            vendor_dir = self.depl_mgr.get_dir(VENDOR_DIR_FIELD)
            p2pool_dir = P2POOL_FIELD + '-' + elem.version()
            rmtree(os.path.join(vendor_dir, p2pool_dir, elem.instance()))
            self.depl_mgr.del_deployment(elem)
            job.msg("Deleted")
            self.job_queue.complete_job(job=job)
        elif type(elem) == P2PoolRemote or type(elem) == MoneroDRemote:
            self.ensure_stopped(elem)
            self.depl_mgr.del_deployment(elem)
            job.msg("Deleted")
            self.job_queue.complete_job(job=job)
    

    def disable(self, job: Job):
        elem_type = job.elem_type()
        instance = job.instance()
        self.log.info(f"Disbling {elem_type}/{instance}")
        elem = self.depl_mgr.get_deployment(elem_type, instance)
        job.msg("Disabled")
        elem.disable()
        self.depl_mgr.update_deployment(elem)
        self.job_queue.complete_job(job)


    def enable(self, job: Job):
        elem_type = job.elem_type()
        instance = job.instance()
        self.log.info(f"Enabling {elem_type}/{instance}")
        elem = self.depl_mgr.get_deployment(elem_type, instance)
        print(f"server:enabled(): 1. {elem.enabled()}")
        job.msg("Enabled")
        elem.enable()
        self.depl_mgr.update_deployment(elem)
        elem2 = self.depl_mgr.get_deployment(elem_type, instance)
        print(f"server:enabled(): 4. {elem2.enabled()}")
        self.job_queue.complete_job(job)


    def ensure_running(self, elem):
        # Check if the deployment service is running, start it if it's not
        print(f"Db4eServer:ensure_running(): {elem}")
        sd = self.systemd
        if type(elem) == XMRig:
            instance = elem.instance()
            sd.service_name('xmrig@' + instance)
        elif type(elem) == P2Pool:
            instance = elem.instance()
            sd.service_name('p2pool@' + instance)
            
        if not sd.active():
            rc = sd.start()
            if rc == 0:
                self.log.critical(f'Started {elem}')
            else:
                self.log.critical(f'ERROR: Failed to start {elem}, return code was {rc}')


    def ensure_stopped(self, elem):
        print(f"Db4eServer:ensure_stopped(): {elem}")
        sd = self.systemd
        if type(elem) == XMRig:
            instance = elem.instance()
            sd.service_name('xmrig@' + instance)
        elif type(elem) == P2Pool:
            instance = elem.instance()
            sd.service_name('p2pool@' + instance)

        print(f"Db4eServer:ensure_stopped(): sd.active(): {sd.active()}")
        if sd.active():
            rc = sd.stop()
            if rc == 0:
                self.log.critical(f'Stopped {elem}')
            else:
                self.log.critical(f'ERROR: Failed to stop {elem}, return code was {rc}')
                

    def shutdown(self, signum, frame):
        self.log.info(f'Shutdown requested (signal {signum})')
        self.running.clear()
        sys.exit(0)


    def start(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        self.log.info("Starting Db4E Server")
        count = 0
        while self.running.is_set:
            count += 1
            self.log.debug(f"Ticking... {count}...")
            self.check_deployments()
            self.check_jobs()
            time.sleep(POLL_INTERVAL)

        self.cleanup()


    def update(self, job):
        elem = job.elem()
        print(f"Db4eServer:update(): {elem}")
        elem = self.depl_mgr.update_deployment(elem)
        msgs = ""
        for msg in elem.pop_msgs():
            print(f"Db4eServer:update(): msg: {msg}")
            for key, val in msg.items():
                msgs += val[MESSAGE_FIELD] + "\n"
        job.msg(msgs[:-1])
        self.job_queue.complete_job(job)


def main():
    # Set environment variables for better color support
    os.environ[TERM_ENVIRON_FIELD] = TERM_DEFAULT
    os.environ[COLORTERM_ENVIRON_FIELD] = COLORTERM_DEFAULT

    server = Db4eServer()
    server.start()
if __name__ == "__main__":
    main()