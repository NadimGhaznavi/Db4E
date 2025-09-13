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
from copy import deepcopy

try:
    __package_name__ = metadata.metadata(__package__ or __name__)["Name"]
    __version__ = metadata.version(__package__ or __name__)
except Exception:
    __package_name__ = "Db4E"
    __version__ = "N/A"

from db4e.Modules.Db4E import Db4E
from db4e.Modules.Db4ESystemD import Db4ESystemD
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.Db4ELogger import Db4ELogger
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.InternalP2Pool import InternalP2Pool
from db4e.Modules.Job import Job
from db4e.Modules.JobQueue import JobQueue
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.P2PoolWatcher import P2PoolWatcher
from db4e.Modules.XMRig import XMRig
from db4e.Constants.DDef import DDef
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DDir import DDir
from db4e.Constants.DJob import DJob



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
        self.systemd = Db4ESystemD()

        # Get a Mongo manager
        self.db = DbMgr()

        # Get a JobQueue
        self.job_queue = JobQueue(db=self.db)

        # Get a P2Pool log watcher
        self.p2pool_watcher = P2PoolWatcher()

        # {instance_name: (thread, stop_event)}
        self.log_watchers = {}  

        # Setup logging
        vendor_dir = self.depl_mgr.get_dir(DDir.VENDOR)
        logs_dir = DDef.LOG_DIR
        log_file = DDef.DB4E_LOG_FILE
        fq_log_file = os.path.join(vendor_dir, DElem.DB4E, logs_dir, log_file)    
        self.log = Db4ELogger(
            elem_type=DDef.DB4E_SERVER,
            log_file=fq_log_file
        )

        # Flag this process as "running"
        self.running = threading.Event()
        self.running.set()


    def check_deployments(self):
        depls = self.depl_mgr.get_deployments()
        for depl in depls:
            depl_type = type(depl)
            if depl_type == Db4E or depl_type == MoneroDRemote or \
                depl_type == P2PoolRemote or depl_type == InternalP2Pool:
                continue 

            #print(f"Db4eServer:check_deployments(): {depl}")
            if depl.enabled():
                self.ensure_running(depl)
                if depl_type == P2Pool:
                    # Make sure there's a log watcher running                    
                    self.spawn_log_watcher(depl) 

            else:
                self.ensure_stopped(depl)


    def check_jobs(self):
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
            if op == DJob.ENABLE:
                self.enable(job=job)
            elif op == DJob.DISABLE:
                self.disable(job=job)
            elif op == DJob.DELETE:
                self.delete(job=job)
            elif op == DJob.RESTART:
                self.restart(job=job)
            elif op == DJob.UPDATE:
                self.update(job=job)
            elif op == DJob.SET_PRIMARY:
                self.set_primary(job=job)


    def delete(self, job: Job):
        elem_type = job.elem_type()
        instance = job.instance()
        self.log.info(f"Deleting {elem_type}/{instance}")
        elem = self.depl_mgr.get_deployment(elem_type, instance)
        job.msg("Deleted deployment")
        if type(elem) == XMRig:
            self.ensure_stopped(elem)
            config_file = elem.config_file()
            os.remove(config_file)
            self.depl_mgr.del_deployment(elem)
            self.job_queue.complete_job(job=job)
        elif type(elem) == P2Pool:
            self.ensure_stopped(elem)
            vendor_dir = self.depl_mgr.get_dir(DDir.VENDOR)
            p2pool_dir = DElem.P2POOL + '-' + elem.version()
            rmtree(os.path.join(vendor_dir, p2pool_dir, elem.instance()))
            self.depl_mgr.del_deployment(elem)
            self.job_queue.complete_job(job=job)
            self.disable_downstream(elem)
        elif type(elem) == P2PoolRemote or type(elem) == MoneroDRemote:
            self.depl_mgr.del_deployment(elem)
            self.job_queue.complete_job(job=job)
            self.disable_downstream(elem)
        elif type(elem) == MoneroD:
            self.ensure_stopped(elem)
            self.depl_mgr.del_deployment(elem)
            vendor_dir = self.depl_mgr.get_dir(DDir.VENDOR)
            monerod_dir = DElem.MONEROD + '-' + elem.version()
            conf_file = elem.config_file()
            os.remove(conf_file)
            rmtree(os.path.join(vendor_dir, monerod_dir, elem.instance()))
            self.depl_mgr.del_deployment(elem)  
            self.job_queue.complete_job(job=job)
            self.disable_downstream(elem)
            

    def disable(self, job: Job):
        elem_type = job.elem_type()
        instance = job.instance()
        elem = self.depl_mgr.get_deployment(elem_type, instance)
        if elem.enabled():
            job.msg(f"Disabled deployment: enabled: {elem.enabled()}")
            elem.disable()
            self.depl_mgr.update_deployment(elem)
            self.job_queue.complete_job(job)
            if type(elem) == P2Pool or type(elem) == MoneroD or \
                type(elem) == P2PoolRemote or type(elem) == MoneroDRemote:
                self.disable_downstream(elem)
            self.log.critical(f"Disabled deployment {elem}")


    def disable_downstream(self, elem):
        print(f"Db4eServer:disable_downstream(): {elem}")
        elems = self.depl_mgr.get_downstream(elem)
        for elem in elems:
            print(f"Db4eServer:disable_downstream(): elem/enabled: {elem}/{elem.enabled()}")
            elem.disable()
            self.depl_mgr.update_deployment(elem)
            job = Job(op=DJob.DISABLE, elem_type=elem.elem_type(), instance=elem.instance())
            job.msg(f"Disabled downstream instance: {elem.instance()}")
            self.job_queue.complete_job(job)    


    def enable(self, job: Job):
        elem_type = job.elem_type()
        instance = job.instance()
        self.log.info(f"Enabling {elem_type}/{instance}")
        elem = self.depl_mgr.get_deployment(elem_type, instance)
        job.msg(f"Enabled deployment")
        elem.enable()
        self.depl_mgr.update_deployment(elem)
        self.job_queue.complete_job(job)


    def ensure_running(self, elem):
        # Check if the deployment service is running, start it if it's not
        #print(f"Db4eServer:ensure_running(): {elem}")
        sd = self.systemd
        if type(elem) == MoneroD:
            instance = elem.instance()
            sd.service_name('monerod@' + instance)
        elif type(elem) == P2Pool:
            instance = elem.instance()
            sd.service_name('p2pool@' + instance)
        elif type(elem) == XMRig:
            instance = elem.instance()
            sd.service_name('xmrig@' + instance)
        else:
            raise ValueError(f"Unknown deployment type: {elem}")
            
        if not sd.active():
            rc = sd.start()
            if rc == 0:
                self.log.critical(f'Started {elem}')
            else:
                self.log.critical(f'ERROR: Failed to start {elem}, return code was {rc}')


    def ensure_stopped(self, elem):
        #print(f"Db4eServer:ensure_stopped(): {elem}")
        sd = self.systemd
        if type(elem) == MoneroD:
            instance = elem.instance()
            sd.service_name('monerod@' + instance)
        elif type(elem) == P2Pool:
            instance = elem.instance()
            sd.service_name('p2pool@' + instance)
        elif type(elem) == XMRig:
            instance = elem.instance()
            sd.service_name('xmrig@' + instance)
        else:
            raise ValueError(f"Unknown deployment type: {elem}")

        if sd.active():
            rc = sd.stop()
            if rc == 0:
                self.log.critical(f'Stopped {elem}')
                if type(elem) == P2Pool:
                    self.log_watchers.pop(instance, None)
                    watcher = self.log_watchers.pop(instance, None)
                    if watcher:
                        thread, stop_event = watcher
                        stop_event.set()
                        thread.join()
            else:
                self.log.critical(f'ERROR: Failed to stop {elem}, return code was {rc}')
                

    def restart(self, job):
        # Note that XMRig does not need to be restarted, it's smart enough to notice that
        # the JSON config has been updated and reload the settings
        elem_type = job.elem_type()
        instance = job.instance()
        sd = self.systemd
        if elem_type == DElem.MONEROD:
            sd.service_name('monerod@' + instance)
        elif elem_type == DElem.P2POOL:
            sd.service_name('p2pool@' + instance)
        else:
            raise ValueError(f"Unknown deployment type: {elem_type}")
        sd.restart()
        job.msg(f"Restarted instance")
        self.job_queue.complete_job(job)


    def shutdown(self, signum, frame):
        self.log.info(f'Shutdown requested (signal {signum})')
        self.running.clear()
        sys.exit(0)


    def set_int_p2pool_primary_server(self, monerod):
        # Update the internal P2Pool servers.....
        for p2pool in self.depl_mgr.get_internal_p2pools():
            p2pool = deepcopy(p2pool)
            p2pool.parent(monerod.id())
            p2pool.monerod = monerod
            vendor_dir = self.get_dir(DDir.VENDOR)
            tmpl_file = self.get_template(DElem.P2POOL)
            p2pool.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)
            p2pool.enable()
            p2pool.log_file(
                os.path.join(
                    vendor_dir, self.get_dir(DElem.P2POOL), p2pool.instance(), 
                    DDir.LOG, 'p2pool.log'))
            self.db_cache.update_one(p2pool)


    def set_primary(self, monerod):

        for aMonerod in self.depl_mgr.get_monerods():
            if aMonerod.instance() != monerod.instance():
                if aMonerod.primary_server():
                    aMonerod.primary_server(False)
                    self.db_cache.update_one(aMonerod)
        self.set_int_p2pool_primary_server(monerod)        


    def start(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        self.log.info("Starting Db4E Server")
        count = 0
        while self.running.is_set():
            count += 1
            self.log.debug(f"Ticking . . .. ... ..... ........ ............. {count}")
            self.check_deployments()
            self.check_jobs()
            time.sleep(POLL_INTERVAL)


    def spawn_log_watcher(self, p2pool):
        instance = p2pool.instance()
        if instance in self.log_watchers:
            # Already watching
            return

        stop_event = threading.Event()

        def _runner():
            try:
                print(f"Db4eServer:spawn_log_watcher(): {p2pool}")
                self.p2pool_watcher.monitor_log(p2pool.log_file(), stop_event)
            finally:
                # Cleanup on exit
                self.log_watchers.pop(instance, None)

        t = threading.Thread(target=_runner, name=f"LogWatcher-{instance}", daemon=True)
        self.log_watchers[instance] = (t, stop_event)
        t.start()


    def update(self, job):
        elem = job.elem()
        print(f"Db4eServer:update(): {elem}")

        elem = self.depl_mgr.update_deployment(elem)
        #print(f"Db4eServer:update(): rec {elem.to_rec()}")
        msgs = ""
        for msg in elem.pop_msgs():
            for key, val in msg.items():
                msgs += val[DField.MESSAGE] + "\n"
        job.msg(msgs[:-1])
        self.job_queue.complete_job(job)



def main():
    # Set environment variables for better color support
    os.environ[DField.TERM_ENVIRON] = DDef.TERM
    os.environ[DField.COLORTERM_ENVIRON] = DDef.COLORTERM

    server = Db4eServer()
    server.start()
if __name__ == "__main__":
    main()