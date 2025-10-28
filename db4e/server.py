"""
db4e/server.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

import os, sys

# Turn off buffering
sys.stdout.reconfigure(line_buffering=True)
from datetime import datetime
import time
import signal
import threading
from importlib import metadata
import shutil
import subprocess
import gzip
from pathlib import Path
import re
import fastapi

try:
    __package_name__ = metadata.metadata(__package__ or __name__)["Name"]
    __version__ = metadata.version(__package__ or __name__)
except Exception:
    __package_name__ = "Db4E"
    __version__ = "N/A"

from db4e.util.BootstrapMgr import BootstrapMgr
from db4e.util.Db4ESystemD import Db4ESystemD
from db4e.util.Db4ELogger import Db4ELogger
from db4e.util.P2PoolWatcher import P2PoolWatcher
from db4e.misc.DeplMgr import DeplMgr

from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
from db4e.recs.monero.XMRig import XMRig

from db4e.db.SQLDb import SQLDb
from db4e.db.DeplDb import DeplDb
from db4e.db.MiningDb import MiningDb
from db4e.db.OpsDb import OpsDb


from db4e.constants.DDebug import DDebug
from db4e.constants.DDef import DDef
from db4e.constants.DField import DField
from db4e.constants.DElem import DElem
from db4e.constants.DDir import DDir
from db4e.constants.DJob import DJob
from db4e.constants.DFile import DFile
from db4e.constants.DModule import DModule
from db4e.constants.OLD_DMongo import DMongo
from db4e.constants.DSystemD import DSystemD
from db4e.constants.DLabel import DLabel
from db4e.constants.OLD_DMongo import DMongo


DDebug.FUNCTION = False

POLL_INTERVAL = 5


class Db4eServer:
    """
    Db4E Server
    Server Class Relationships Diagram:
    https://db4e.osoyalce.com/images/Server-Relationships.png
    """

    def __init__(self):

        # Bootstrap Manager
        self.bs_mgr = BootstrapMgr()
        if not self.bs_mgr.is_initialized():
            raise ValueError("ERROR: Db4E initial install not completed!")

        # Setup logging
        vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
        logs_dir = DDef.LOG_DIR
        log_file = DDef.DB4E_LOG_FILE
        fq_log_file = os.path.join(vendor_dir, DElem.DB4E, logs_dir, log_file)
        self.log_file = fq_log_file
        self.log = Db4ELogger(db4e_module=DModule.DB4E_SERVER, log_file=fq_log_file)

        # SQLite DB module
        self.sql_db = SQLDb(db_type=DField.SERVER, log_file=fq_log_file)
        self.sql_db.initialize(self.bs_mgr.get_dir(DDir.DB))

        # Operations DB module
        self.ops_db = OpsDb(sql_db=self.sql_db, log_file=fq_log_file)

        # Deployment DB module
        self.depl_db = DeplDb(sql_db=self.sql_db, log_file=fq_log_file)
        # Deployment Manager
        self.depl_mgr = DeplMgr(
            bs_mgr=self.bs_mgr, depl_db=self.depl_db, ops_db=self.ops_db
        )

        #  systemd wrapper
        self.systemd = Db4ESystemD(ops_db=self.ops_db)

        # Mining DB object
        self.mining_db = MiningDb(
            sql_db=self.sql_db,
            log_file=fq_log_file,
        )

        # Track when we last ran `logrotate`
        self.last_logrotate = None

        # {instance_name: (thread, stop_event)}
        self.log_watchers = {}

        # Track which services are in the process of being stopped/started to avoid
        # sending multiple "systemctl [start|stop] <service>" commands
        self.starting = set()
        self.stopping = set()

        # Flag this process as "running"
        self.running = threading.Event()
        self.running.set()

        # Create an Ops record to record the startup time
        self.ops_db.add_start_event(DElem.DB4E_SERVER, DElem.DB4E_SERVER)

        # Make sure the permissions on the logrotate files are correct
        self.chown_logrotate_files()

    def add_deployment(self, elem):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:add_deployment(): {elem}")
        self.depl_mgr.add_deployment(elem)

    def check_deployments(self):
        depls = self.depl_mgr.get_deployments()
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:check_deployments(): {depls}")
        found_primary = False
        for elem in depls:
            time.sleep(0.25)
            elem_type = type(elem)

            # Nothing to do for these classes
            if elem_type == P2PoolRemote:
                continue

            # Look for primary Monero deployments
            if elem_type == Db4E:
                primary_server = elem.primary_server()
                # print(f"Db4eServer:check_deployments(): primary_server: {primary_server}")
                if primary_server == DField.DISABLE:
                    self.unset_int_p2pool_primary()
                else:
                    self.set_int_p2pool_primary(elem.primary_server())
                    found_primary = True
                continue

            # Make sure anything that's enabled is running
            if elem_type in [MoneroD, P2Pool, InternalP2Pool, XMRig] and elem.enabled():
                self.ensure_running(elem)
                if elem_type in [P2Pool, InternalP2Pool]:
                    # Make sure there's a log watcher running
                    self.spawn_log_watcher(elem)

            # Makre sure anything that's disabled is stopped
            # self.log.debug(f"Db4eServer:check_deployments(): enabled: {elem}: {elem.enabled()}")
            if (
                elem_type in [MoneroD, P2Pool, InternalP2Pool, XMRig]
                and not elem.enabled()
            ):
                self.ensure_stopped(elem)

            # There are no primary Monery deployments
            if not found_primary:
                self.unset_int_p2pool_primary()

    def chown_logrotate_files(self):
        if DDebug.FUNCTION:
            self.log.debug("Db4eServer:chown_logrotate_files():")
        logrotate_dir = self.bs_mgr.get_dir(DDir.LOGROTATE)
        # Get a list of files in the logrotate_dir
        file_list = os.listdir(logrotate_dir)
        for aFile in file_list:
            fq_file = os.path.join(logrotate_dir, aFile)
            try:
                cmd = [DFile.SUDO, DFile.CHOWN, DDef.ROOT, fq_file]
                proc = subprocess.run(cmd, stderr=subprocess.PIPE, input="")
                stderr = proc.stderr.decode("utf-8")
                self.log.info(f"Set permissions on logrotate file: {fq_file}")
            except Exception as e:
                self.log.critical(f"chown_logrotate_files() failed: {e} {stderr}")

    def delete(self, elem):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:delete(): {elem}")
        self.log.info(f"Job: Deleting {elem}")
        if type(elem) == XMRig:
            elem.enabled(False)
            self.ensure_stopped(elem)
            self.depl_mgr.delete_deployment(elem)
        elif type(elem) == P2Pool:
            self.disable_downstream(elem)
            elem.enabled(False)
            self.ensure_stopped(elem)
            self.depl_mgr.delete_deployment(elem)
            control = self.log_watchers.pop(elem.instance(), None)
            if control:
                thread, stop_event, watcher = control
                watcher.stop_sub_thread()
                stop_event.set()
                thread.join()
        elif type(elem) == P2PoolRemote or type(elem) == MoneroDRemote:
            self.disable_downstream(elem)
            self.depl_mgr.delete_deployment(elem)
        elif type(elem) == MoneroD:
            self.disable_downstream(elem)
            elem.enabled(False)
            self.ensure_stopped(elem)
            self.depl_mgr.delete_deployment(elem)

    def disable(self, elem):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:disable(): {job}")
        # print(f"Db4eServer:disable(): {elem}: current: {elem.enabled()}")
        if not elem.enabled():
            return
        elem.enabled(False)
        self.depl_mgr.update_deployment(elem)
        if (
            type(elem) == P2Pool
            or type(elem) == MoneroD
            or type(elem) == P2PoolRemote
            or type(elem) == MoneroDRemote
        ):
            self.disable_downstream(elem)
        self.log.info(f"Disable: {elem}")
        # Create an Ops record when remote elements are disabled
        if type(elem) == MoneroDRemote:
            stop_rec = StartStopRec(
                elem_type=DElem.MONEROD_REMOTE,
                instance=elem.instance(),
                rec_type=DField.STOP,
            )
            self.sql_mgr.insert_one(stop_rec)
        elif type(elem) == P2PoolRemote:
            stop_rec = StartStopRec(
                elem_type=DElem.P2POOL_REMOTE,
                instance=elem.instance(),
                rec_type=DField.STOP,
            )
            self.sql_mgr.insert_one(stop_rec)

    def disable_downstream(self, elem):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:disable_downstream(): {elem}")

        if type(elem) == MoneroD or type(elem) == MoneroDRemote:
            p2pools = self.depl_mgr.get_p2pools()
            for p2pool in p2pools:
                if p2pool.parent() == elem.id():
                    p2pool.monerod = None
                    p2pool.enabled(False)
                    self.ensure_stopped(p2pool)
                    self.depl_mgr.update_deployment(p2pool)
                    p2pool.parent(DField.DISABLE)
                    # TODO add TuiLogRec
                    self.disable_downstream(p2pool)

        elif type(elem) == P2Pool or type(elem) == P2PoolRemote:
            int_p2pools = self.depl_mgr.get_internal_p2pools()
            for int_p2pool in int_p2pools:
                if int_p2pool.parent() == elem.id():
                    int_p2pool.monerod = None
                    int_p2pool.enabled(False)
                    self.ensure_stopped(int_p2pool)
                    self.depl_mgr.update_deployment(int_p2pool)
                    int_p2pool.parent(DField.DISABLE)
                    # TODO add TuiLogRec

        elif type(elem) == P2Pool or type(elem) == P2PoolRemote:
            xmrigs = self.depl_mgr.get_xmrigs()
            for xmrig in xmrigs:
                if xmrig.parent() == elem.id():
                    xmrig.p2pool = None
                    self.ensure_stopped(xmrig)
                    xmrig.enabled(False)
                    xmrig.parent(DField.DISABLE)
                    self.depl_mgr.update_deployment(xmrig)
                    # TODO add TuiLogRec

    def enable(self, elem):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:enable(): {elem}")
        # print(f"Db4eServer:enable(): {elem}: current: {elem.enabled()}")
        if elem.enabled():
            return
        self.log.info(f"Enable: {elem}")

        elem.enabled(True)
        self.depl_mgr.update_deployment(elem)
        # Create an Ops record when remote elements are enabled
        if type(elem) == MoneroDRemote:
            start_rec = StartStopRec(
                elem_type=DElem.MONEROD_REMOTE,
                instance=elem.instance(),
                rec_type=DField.START,
            )
            self.sql_mgr.insert_one(start_rec)
        elif type(elem) == P2PoolRemote:
            start_rec = StartStopRec(
                elem_type=DElem.P2POOL_REMOTE,
                instance=elem.instance(),
                rec_type=DField.START,
            )
            self.sql_mgr.insert_one(start_rec)

    def ensure_running(self, elem):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:ensure_running(): {elem}")
        # Check if the deployment service is running, start it if it's not
        sd = self.systemd
        if type(elem) == MoneroD:
            instance = elem.instance()
            sd.service_name("monerod@" + instance)
        elif type(elem) == P2Pool or type(elem) == InternalP2Pool:
            instance = elem.instance()
            sd.service_name("p2pool@" + instance)
        elif type(elem) == XMRig:
            instance = elem.instance()
            sd.service_name("xmrig@" + instance)
        else:
            raise ValueError(f"Unknown deployment type: {elem}")

        ## Don't keep issuing 'systemctl start <service>' if it's just starting up....
        if sd.active():
            # It's up - clear the "stopping" and clear the "starting" too
            self.stopping.discard(instance)
            self.starting.discard(instance)
            return
        if instance in self.starting:
            # It's already in the process of starting, do nothing
            return
        # Not active and not starting, start it up
        self.starting.add(instance)
        rc = sd.start()
        if rc == 0:
            self.log.info(f"Started: {elem}")
            time.sleep(30)
        else:
            self.log.critical(f"ERROR: Failed to start {elem}, return code was {rc}")
            self.stopping.discard(instance)
            self.starting.discard(instance)

    def ensure_stopped(self, elem):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:ensure_stopped(): {elem}")
        sd = self.systemd
        if type(elem) == MoneroD:
            instance = elem.instance()
            sd.service_name("monerod@" + instance)
        elif isinstance(elem, P2Pool):
            instance = elem.instance()
            sd.service_name("p2pool@" + instance)
        elif type(elem) == XMRig:
            instance = elem.instance()
            sd.service_name("xmrig@" + instance)
        else:
            raise ValueError(f"Unknown deployment type: {elem}")

        ## Don't keep issuing 'systemctl stop <service>' if it's just shutting down....
        if not sd.active():
            # It's down - clear the "stopping" and clear the "starting" too
            self.stopping.discard(instance)
            self.starting.discard(instance)
            return
        if instance in self.stopping:
            # It's already in the process of stopping, do nothing
            return

        # Active and not already stopping -> issue stop
        self.stopping.add(instance)
        rc = sd.stop()
        if rc == 0:
            self.log.info(f"Stopped: {elem}")
            time.sleep(30)
            if isinstance(elem, P2Pool):
                control = self.log_watchers.pop(instance, None)
                if control:
                    thread, stop_event, watcher = control
                    watcher.stop_sub_thread()
                    stop_event.set()
                    thread.join()
        else:
            self.log.critical(f"ERROR: Failed to stop {elem}, return code was {rc}")

    def restart(self, elem):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:restart(): {elem}")
        # Note that XMRig does not need to be restarted, it's smart enough to notice that
        # the JSON config has been updated and reload the settings
        sd = self.systemd
        instance = elem.instance()
        if type(elem) == MoneroD:
            sd.service_name("monerod@" + instance)
        elif type(elem) == P2Pool:
            sd.service_name("p2pool@" + instance)
        else:
            raise ValueError(f"Unknown deployment type: {elem_type}")
        sd.restart()

    def rotate_logs(self):
        # Run logrotate every two hours
        cur_hour = datetime.now().hour
        vendor_dir = self.depl_mgr.get_dir(DDir.VENDOR)
        if self.last_logrotate is None or self.last_logrotate != cur_hour:
            self.last_logrotate = cur_hour
            try:
                logrotate_dir = self.depl_mgr.get_dir(DDir.LOGROTATE)
                cmd = [DFile.SUDO, DFile.LOGROTATE, "-v", logrotate_dir]
                proc = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=""
                )
                stdout = proc.stdout.decode()
                stderr = proc.stderr.decode()
                # self.log.debug(f"rotate_logs(): {stdout}{stderr}")

                output_lines = stderr.split("\n")
                depls = {}
                cur_elem_type = None
                cur_instance = None
                for line in output_lines:
                    # self.log.critical(line)
                    # Parse the elem_type and instance out of the logrotate output
                    pattern = r".*reading config file\s(?P<config>.*.conf)"
                    match = re.search(pattern, line)
                    if match:
                        config_file = match.group("config")
                        # self.log.critical(f"Found config: {config_file}")
                        if config_file == DElem.DB4E + DDef.CONF_SUFFIX:
                            continue
                        else:
                            pattern = r"(?P<elem_type>.*)-(?P<instance>.*).conf"
                            match = re.search(pattern, config_file)
                            if match:
                                elem_type = match.group("elem_type")
                                instance = match.group("instance")
                                # self.log.critical(f"Found {elem_type}/{instance}")
                                depls[(elem_type, instance)] = False

                    # Watch to see if a log was rotated
                    pattern = rf"considering log {re.escape(vendor_dir)}/(?P<elem_type>[^/]+)(?:/(?P<instance>[^/]+))?/logs/(?P<logname>[^/]+)\.log"
                    match = re.search(pattern, line)
                    if match:
                        # self.log.critical(f"line: {line}")
                        cur_elem_type = match.group("elem_type")
                        cur_instance = match.group("instance") or match.group("logname")
                        # self.log.critical(f"{cur_elem_type}/{cur_instance}")
                    pattern = r"\s+log needs rotating.*"
                    match = re.search(pattern, line)
                    if match:
                        if cur_elem_type != DElem.DB4E:
                            depls[(cur_elem_type, cur_instance)] = True
                            self.log.info(
                                f"{cur_elem_type}/{cur_instance} rotating log file"
                            )

                for elem_type, instance in depls:
                    if depls[(elem_type, instance)]:
                        # Create a restart job
                        job = Job(
                            op=DJob.RESTART, elem_type=elem_type, instance=instance
                        )
                        self.job_queue.post_job(job)

            except Exception as e:
                self.log.error(f"rotate_logs(): {e} {stderr}")
                return

    def shutdown(self, signum, frame):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:shutdown(): {signum}")
        self.log.info(f"Shutdown requested (signal {signum})")
        self.running.clear()
        for instance in self.log_watchers.keys():
            stop_rec = StartStopRec(
                elem_type=DElem.P2POOL_WATCHER, instance=instance, rec_type=DField.STOP
            )
            self.sql_mgr.insert_one(stop_rec)

        # Create a stop event in the ops collection
        stop_rec = StartStopRec(
            elem_type=DElem.DB4E_SERVER,
            instance=DElem.DB4E_SERVER,
            rec_type=DField.STOP,
        )
        self.sql_mgr.insert_one(stop_rec)
        sys.exit(0)

    def set_int_p2pool_primary(self, monerod_id):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:set_int_p2pool_primary(): {monerod_id}")
        for p2pool in self.depl_mgr.get_internal_p2pools():
            if p2pool.parent() != monerod_id:
                self.log.info(f"Regenerating {p2pool.instance()} P2Pool config file")
                p2pool.parent(monerod_id)
                p2pool.monerod = self.depl_mgr.get_deployment_by_id(monerod_id)
                vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
                tmpl_file = self.bs_mgr.get_template(DElem.P2POOL)
                p2pool.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)
                p2pool.log_file(
                    os.path.join(
                        vendor_dir,
                        self.bs_mgr.get_dir(DElem.P2POOL),
                        p2pool.instance(),
                        DDir.LOG,
                        DFile.P2POOL_LOG,
                    )
                )
                p2pool.enabled(True)
                self.depl_mgr.update_deployment(p2pool)
                self.ensure_running(p2pool)

    def spawn_log_watcher(self, p2pool):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:spawn_log_watcher(): {p2pool}")
        instance = p2pool.instance()
        if instance in self.log_watchers:
            # Already watching
            return

        stop_event = threading.Event()
        # User defined, local P2Pool instance
        if type(p2pool) == P2Pool:
            watcher = P2PoolWatcher(
                mining_db=self.mining_db,
                chain=p2pool.chain(),
                log_file=p2pool.log_file(),
                stdin_path=p2pool.stdin_path(),
                stop_event=stop_event,
                pool=instance,
                depl_mgr=self.depl_mgr,
                db4e_log_file=self.log_file,
            )
        elif type(p2pool) == InternalP2Pool:
            watcher = P2PoolWatcher(
                mining_db=self.mining_db,
                chain=p2pool.chain(),
                log_file=p2pool.log_file(),
                stdin_path=p2pool.stdin_path(),
                stop_event=stop_event,
                pool=instance,
                depl_mgr=self.depl_mgr,
                db4e_log_file=self.log_file,
                stats_mod=p2pool.stats_mod(),
            )
        else:
            raise ValueError(
                f"spawn_log_watcher(): Unknown deployment type: {type(p2pool)}"
            )

        def _runner():
            try:
                watcher.monitor_log()
            except Exception as e:
                self.log.error(f"Watcher for {instance} crashed: {e}", exc_info=True)
            finally:
                # Cleanup on exit
                watcher.stop_sub_thread()
                self.log_watchers.pop(instance, None)
                self.log.debug(f"Watcher thread exiting: {instance}")
                if instance not in [
                    DLabel.MAIN_CHAIN,
                    DLabel.MINI_CHAIN,
                    DLabel.NANO_CHAIN,
                ]:
                    stop_rec = StartStopRec(
                        elem_type=DLabel.P2POOL_WATCHER,
                        instance=instance,
                        rec_type=DField.STOP,
                    )
                    self.sql_mgr.insert_one(stop_rec)

        t = threading.Thread(target=_runner, name=f"LogWatcher-{instance}", daemon=True)
        self.log_watchers[instance] = (t, stop_event, watcher)
        t.start()
        self.log.info(f"Started P2Pool watcher: {instance}")
        start_rec = StartStopRec(
            elem_type=DLabel.P2POOL_WATCHER, instance=instance, rec_type=DField.START
        )
        self.sql_mgr.insert_one(start_rec)

    def start(self):
        if DDebug.FUNCTION:
            self.log.debug("Db4eServer:start():")
        self.log.info("Starting Db4E Server")
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        count = 0
        while self.running.is_set():
            count += 1
            self.log.debug(f"Ticking . . .. ... ..... ........ ............. {count}")
            self.check_deployments()
            self.rotate_logs()
            time.sleep(POLL_INTERVAL)

    def update(self, elem):
        if DDebug.FUNCTION:
            self.log.debug(f"Db4eServer:update(): {elem}")
        self.log.info(f"Updated: {elem}")

        # TODO check return value, restart if needed
        self.depl_mgr.update_deployment(elem)
        # Restart Monerod and P2Pool deployments if their config has been updated
        if type(elem) == MoneroD or type(elem) == P2Pool:
            # Create a restart job
            pass
            # TODO implement restart

    def unset_int_p2pool_primary(self):
        if DDebug.FUNCTION:
            self.log.debug("Db4eServer:unset_int_p2pool_primary():")
        for p2pool in self.depl_mgr.get_internal_p2pools():
            p2pool.parent(DField.DISABLE)
            p2pool.enabled(False)
            self.depl_mgr.update_deployment(p2pool)


def main():
    # Set environment variables for better color support
    os.environ[DField.TERM_ENVIRON] = DDef.TERM
    os.environ[DField.COLORTERM_ENVIRON] = DDef.COLORTERM

    server = Db4eServer()
    server.start()


if __name__ == "__main__":
    main()
