"""
db4e/Modules/DeplMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import os
from datetime import datetime
from shutil import rmtree
import socket
from typing import overload
import subprocess

from db4e.db.DeplDb import DeplDb
from db4e.db.OpsDb import OpsDb

from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig
from db4e.recs.monero.XMRigRemote import XMRigRemote
from db4e.util.Helper import sudo_del_file
from db4e.util.BootstrapMgr import BootstrapMgr

from db4e.constants.DField import DField
from db4e.constants.DLabel import DLabel
from db4e.constants.DDef import DDef
from db4e.constants.DDir import DDir
from db4e.constants.DElem import DElem
from db4e.constants.DFile import DFile
from db4e.constants.DField import DField
from db4e.constants.DStatus import DStatus
from db4e.constants.DModule import DModule
from db4e.constants.DMethod import DMethod
from db4e.constants.DField import DField


class Default:
    MONEROD_VERSION = DDef.MONEROD_VERSION
    P2POOL_VERSION = DDef.P2POOL_VERSION
    XMRIG_VERSION = DDef.XMRIG_VERSION
    MONEROD_CONFIG = DDef.MONEROD_CONFIG
    P2POOL_CONFIG = DDef.P2POOL_CONFIG
    PYTHON = DDef.PYTHON
    XMRIG_CONFIG = DDef.XMRIG_CONFIG


class DeplMgr:

    # update_p2pool_deployment() is overloaded ...
    @overload
    def update_p2pool_deployment(self, p2pool: P2Pool) -> P2Pool: ...
    @overload
    def update_p2pool_deployment(self, p2pool: P2PoolInternal) -> P2PoolInternal: ...

    def __init__(self, bs_mgr: BootstrapMgr, depl_db: DeplDb, ops_db: OpsDb):
        self.bs_mgr = bs_mgr
        self.depl_db = depl_db
        self.ops_db = ops_db

    def add_deployment(self, elem):
        elem_class = type(elem)

        # Add a remote Monero daemon deployment
        if elem_class == MoneroD:
            return self.add_monerod_deployment(elem)

        # Add a remote Monero daemon deployment
        elif elem_class == MoneroDRemote:
            return self.add_remote_monerod_deployment(elem)

        # A P2Pool or P2PoolInternal instance
        elif isinstance(elem, P2Pool):
            return self.add_p2pool_deployment(elem)

        # Add a remote P2Pool deployment
        elif elem_class == P2PoolRemote:
            return self.add_remote_p2pool_deployment(elem)

        # Add a XMRig deployment
        elif elem_class == XMRig:
            return self.add_xmrig_deployment(elem)

        # Add a remote XMRig deployment
        elif elem_class == XMRigRemote:
            return self.add_remote_xmrig_deployment(elem)

        # Catchall
        else:
            raise ValueError(f"DeplMgr:add_deployment(): No handler for {elem_class}")

    def add_monerod_deployment(self, monerod: MoneroD) -> MoneroD:
        monerod.ip_addr(socket.gethostname())
        vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
        tmpl_file = self.bs_mgr.get_template(DElem.MONEROD)

        # Monero log file
        os.makedirs(
            os.path.join(vendor_dir, DDir.MONEROD, monerod.instance(), DDef.LOG_DIR),
            exist_ok=True,
        )
        monerod.log_file(
            os.path.join(
                vendor_dir,
                DDir.MONEROD,
                monerod.instance(),
                DDef.LOG_DIR,
                DDef.MONEROD_LOG_FILE,
            )
        )

        # Blockchain directory
        os.makedirs(
            os.path.join(
                vendor_dir, DDir.MONEROD, monerod.instance(), DDef.BLOCKCHAIN_DIR
            ),
            exist_ok=True,
        )
        monerod.blockchain_dir(
            os.path.join(
                vendor_dir, DDir.MONEROD, monerod.instance(), DDef.BLOCKCHAIN_DIR
            )
        )

        # Run directory
        os.makedirs(
            os.path.join(vendor_dir, DDir.MONEROD, monerod.instance(), DDef.RUN_DIR),
            exist_ok=True,
        )

        # Path to STDIN named pipe
        monerod.stdin_path(
            os.path.join(
                vendor_dir,
                DDir.MONEROD,
                monerod.instance(),
                DDef.RUN_DIR,
                DDef.MONEROD_STDIN_PIPE,
            )
        )

        # Generate the configuration
        monerod.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)

        # Add the record to the DB
        monerod = self.depl_db.insert_one(monerod)

        # Create a console log line
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.MONEROD,
            tracked_instance=monerod.instance(),
            status=DStatus.COMPLETE,
            operation=DField.NEW,
            message="New deployment",
        )
        return monerod

    def add_remote_monerod_deployment(self, monerod: MoneroDRemote):
        monerod = self.depl_db.insert_one(monerod)
        # Create a console log message
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.MONEROD_REMOTE,
            tracked_instance=monerod.instance(),
            status=DStatus.COMPLETE,
            operation=DField.NEW,
            message="New deployment",
        )
        return monerod

    def add_p2pool_deployment(self, p2pool: P2Pool):
        # Generate the configuration
        if p2pool.parent() != DField.DISABLE:
            vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
            tmpl_file = self.bs_mgr.get_template(DElem.P2POOL)
            p2pool.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)
            p2pool.log_file(
                os.path.join(
                    vendor_dir,
                    DDir.P2POOL,
                    p2pool.instance(),
                    DDef.LOG_DIR,
                    DFile.P2POOL_LOG,
                )
            )
        # Create the per-instance directories
        os.makedirs(
            os.path.join(vendor_dir, DDir.P2POOL, p2pool.instance(), DDef.LOG_DIR),
            exist_ok=True,
        )
        os.makedirs(
            os.path.join(vendor_dir, DDir.P2POOL, p2pool.instance(), DDef.API_DIR),
            exist_ok=True,
        )
        os.makedirs(
            os.path.join(vendor_dir, DDir.P2POOL, p2pool.instance(), DDef.RUN_DIR),
            exist_ok=True,
        )
        p2pool.stdin_path(
            os.path.join(
                vendor_dir,
                DDir.P2POOL,
                p2pool.instance(),
                DDef.RUN_DIR,
                DFile.P2POOL_STDIN,
            )
        )
        # Generate the logrotate configuration file
        logrotate_tmpl = self.bs_mgr.get_logrotate_template(DElem.P2POOL)
        db4e = self.get_deployment(DElem.DB4E, DElem.DB4E)
        db4e_group = db4e.group()
        p2pool.gen_logrotate_config(
            tmpl_file=logrotate_tmpl, vendor_dir=vendor_dir, db4e_group=db4e_group
        )
        # Add the new record
        p2pool = self.depl_db.insert_one(p2pool)

        # Create a console log message
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.P2POOL,
            tracked_instance=p2pool.instance(),
            status=DStatus.COMPLETE,
            operation=DField.NEW,
            message="New deployment",
        )
        return p2pool

    def add_remote_p2pool_deployment(self, p2pool: P2PoolRemote) -> P2PoolRemote:
        p2pool = self.depl_db.insert_one(p2pool)
        # Create a console log message
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.P2POOL_REMOTE,
            tracked_instance=p2pool.instance(),
            status=DStatus.COMPLETE,
            operation=DField.NEW,
            message="New deployment",
        )
        return p2pool

    def add_xmrig_deployment(self, xmrig: XMRig) -> XMRig:
        # Generate the XMRig configuration
        if xmrig.parent() != DField.DISABLE:
            # Generate the configuration
            vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
            tmpl_file = self.bs_mgr.get_template(DElem.XMRIG)
            xmrig.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)
        # Generate the log file name
        xmrig.log_file(
            os.path.join(
                vendor_dir, DElem.XMRIG, DDef.LOG_DIR, xmrig.instance() + ".log"
            )
        )
        # Generate the logrotate configuration file
        logrotate_tmpl = self.bs_mgr.get_logrotate_template(DElem.XMRIG)
        db4e = self.depl_db.get_deployment(DElem.DB4E, DElem.DB4E)
        db4e_group = db4e.db4e_group()
        xmrig.gen_logrotate_config(
            tmpl_file=logrotate_tmpl, vendor_dir=vendor_dir, db4e_group=db4e_group
        )
        # Add the new record
        xmrig = self.depl_db.insert_one(xmrig)
        # Create a console log message
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.XMRIG,
            tracked_instance=xmrig.instance(),
            status=DStatus.COMPLETE,
            operation=DField.NEW,
            message="New deployment",
        )
        return xmrig

    def add_remote_xmrig_deployment(self, xmrig: XMRigRemote) -> XMRigRemote:
        """
        Add a remote XMRig deployment.

        Remote XMRig deployments are not added from the TUI, they are detected from the
        P2Pool log. The Db4E application sends regular "workers" commands to the user
        defined, local P2Pool deployments. The P2Pool software outputs a list of connected
        miners. The P2PoolWatcher class watches for these log lines and calls this
        function for every connected miner.

        However, this list of miners also includes local deployments. We need to make
        sure we don't create a remote XMRig deployment record for a local XMRig deployment.
        """

        # Don't create a remote XMRig deployment record for a local XMRig deployment.
        for local_xmrig in self.depl_db.get_xmrigs():
            if local_xmrig.instance() == xmrig.instance():
                return

        # Don't create a remote XMRig deployment record if one already exists.
        for remote_xmrig in self.depl_db.get_remote_xmrigs():
            if remote_xmrig.instance() == xmrig.instance():
                return

        xmrig = self.depl_db.insert_one(xmrig)
        # Create a console log message
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.XMRIG_REMOTE,
            tracked_instance=xmrig.instance(),
            status=DStatus.COMPLETE,
            operation=DField.NEW,
            message="New deployment",
        )
        return xmrig

    def create_vendor_dir(self, new_dir: str, db4e: Db4E):
        update_flag = True
        if os.path.exists(new_dir):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
            backup_vendor_dir = new_dir + "." + timestamp
            try:
                os.rename(new_dir, backup_vendor_dir)
                # Add a console log message
                self.ops_db.add_tui_log_line(
                    tracked_type=DElem.DB4E,
                    tracked_instance=DLabel.VENDOR_DIR,
                    status=DStatus.WARN,
                    operation=DField.UPDATE,
                    message="Backed up directory",
                    details=f"{new_dir} > {backup_vendor_dir}",
                )
            except (PermissionError, OSError) as e:
                update_flag = False
                # Add a console log message
                self.ops_db.add_tui_log_line(
                    tracked_type=DElem.DB4E,
                    tracked_instance=DLabel.VENDOR_DIR,
                    status=DStatus.ERROR,
                    operation=DField.UPDATE,
                    message="Unable to backup directory",
                    details=e,
                )
                return db4e, update_flag
        try:
            os.makedirs(new_dir)
            # Add a console log message
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.VENDOR_DIR,
                status=DStatus.COMPLETE,
                operation=DField.NEW,
                message="Created new directory",
                details=new_dir,
            )
        except (PermissionError, OSError) as e:
            update_flag = False
            # Add a console log message
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.VENDOR_DIR,
                status=DStatus.ERROR,
                operation=DField.NEW,
                message="Unable to create directory",
                details=e,
            )
        return update_flag

    def delete_deployment(self, elem):
        vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
        if type(elem) == MoneroD:
            config = elem.config_file()
            if os.path.exists(config):
                os.remove(config)
            depl_dir = os.path.join(vendor_dir, DDir.MONEROD, elem.instance())
            if os.path.isdir(depl_dir):
                rmtree(depl_dir)
        elif type(elem) == P2Pool or type(elem) == P2PoolInternal:
            config = elem.config_file()
            if os.path.exists(config):
                os.remove(config)
            logrotate_config = elem.logrotate_config()
            sudo_del_file(logrotate_config)
            depl_dir = os.path.join(vendor_dir, DDir.P2POOL, elem.instance())
            if os.path.isdir(depl_dir):
                rmtree(depl_dir)
        elif type(elem) == XMRig:
            config = elem.config_file()
            if os.path.exists(config):
                os.remove(config)
            logrotate_config = elem.logrotate_config()
            sudo_del_file(logrotate_config)
            depl_dir = os.path.join(vendor_dir, DElem.XMRIG, elem.instance())
            if os.path.isdir(depl_dir):
                rmtree(depl_dir)
        self.depl_db.delete_deployment(elem)
        # Create a console log message
        self.ops_db.add_tui_log_line(
            tracked_type=type(elem),
            tracked_instance=elem.instance(),
            status=DStatus.COMPLETE,
            operation=DField.DELETE,
            message="Deleted deployment",
        )

    def update_db4e_deployment(self, new_db4e: Db4E):
        update_flag = False
        # The current record, we'll update this and write it back in
        db4e = self.get_deployment(elem_type=DElem.DB4E, instance=DElem.DB4E)

        # Updating user wallet
        if db4e.user_wallet != new_db4e.user_wallet:
            # Create a console log message
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.USER_WALLET,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated user wallet",
                details=f"{db4e.user_wallet()[:6]}... > {new_db4e.user_wallet()[:6]}...",
            )
            db4e.user_wallet(new_db4e.user_wallet())
            update_flag = True

        # Updating vendor dir
        if db4e.vendor_dir != new_db4e.vendor_dir:
            if not db4e.vendor_dir():
                update_flag = self.create_vendor_dir(
                    new_dir=new_db4e.vendor_dir(), db4e=db4e
                )
            else:
                update_flag = self.update_vendor_dir(
                    new_dir=new_db4e.vendor_dir(), old_dir=db4e.vendor_dir(), db4e=db4e
                )

            # Create a console log line
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.VENDOR_DIR,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated vendor dir",
                details=f"{db4e.vendor_dir()} > {new_db4e.vendor_dir()}",
            )
            if update_flag:
                db4e.vendor_dir(new_db4e.vendor_dir())

        # Updating the primary server
        if db4e.primary_server != new_db4e.primary_server:
            if db4e.primary_server() != DField.DISABLE:
                old_instance = self.depl_db.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=db4e.primary_server()
                ).instance()
            else:
                old_instance = "None"
            if new_db4e.primary_server() != DField.DISABLE:
                new_instance = self.depl_db.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=new_db4e.primary_server()
                ).instance()
            else:
                new_instance = "None"
            db4e.primary_server(new_db4e.primary_server())
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.PRIMARY_SERVER,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated primary server",
                details=f"{old_instance} > {new_instance}",
            )
            update_flag = True
        # Update the database
        if update_flag:
            self.depl_db.update_one(db4e)

    def update_deployment(self, elem):
        # print(f"DeplMgr:update_deployment(): {rec}")
        if type(elem) == Db4E:
            return self.update_db4e_deployment(elem)
        elif type(elem) == MoneroD:
            return self.update_monerod_deployment(elem)
        elif type(elem) == MoneroDRemote:
            return self.update_monerod_remote_deployment(elem)
        elif type(elem) == P2Pool or type(elem) == P2PoolInternal:
            return self.update_p2pool_deployment(elem)
        elif type(elem) == P2PoolRemote:
            return self.update_p2pool_remote_deployment(elem)
        elif type(elem) == XMRig:
            return self.update_xmrig_deployment(elem)
        else:
            raise ValueError(
                f"{DModule.DEPLOYMENT_MGR}:update_deployment(): "
                f" No handler for ({elem})"
            )

    def update_monerod_deployment(self, new_monerod: MoneroD):
        # Flags to indicate if we're updaing the DB and/or the startup config
        update, update_config = False, False

        # Retrive the current/old deployment
        monerod = self.depl_db.get_deployment(DElem.MONEROD, new_monerod.instance())
        if not monerod:
            raise ValueError(
                f"DeplMgr:update_monerod_deployment(): "
                f"No monerod found for {new_monerod}"
            )

        # This is an enable/disable operation
        if monerod.enabled() != new_monerod.enabled():
            if monerod.enabled():
                monerod.enabled(False)
            else:
                monerod.enabled(True)
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated enabled flag",
                details=f"{monerod.enabled()} > {new_monerod.enabled()}",
            )
            update, update_config = True, False

        # In Peers
        if monerod.in_peers != new_monerod.in_peers:
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated inbound max peers",
                details=f"{monerod.in_peers()} > {new_monerod.in_peers()}",
            )
            monerod.in_peers(new_monerod.in_peers())
            update, update_config = True, True

        # Out Peers
        if monerod.out_peers != new_monerod.out_peers:
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated outbound max peers",
                details=f"{monerod.out_peers()} > {new_monerod.out_peers()}",
            )
            monerod.out_peers(new_monerod.out_peers())
            update, update_config = True, True

        # P2P Bind Port
        if monerod.p2p_bind_port != new_monerod.p2p_bind_port:
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated P2P bind port",
                details=f"{monerod.p2p_bind_port()} > {new_monerod.p2p_bind_port()}",
            )
            monerod.p2p_bind_port(new_monerod.p2p_bind_port())
            update, update_config = True, True

        # RPC Bind Port
        if monerod.rpc_bind_port != new_monerod.rpc_bind_port:
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated RPC bind port",
                details=f"{monerod.rpc_bind_port()} > {new_monerod.rpc_bind_port()}",
            )
            monerod.rpc_bind_port(new_monerod.rpc_bind_port())
            update, update_config = True, True

        # ZMQ Pub Port
        if monerod.zmq_pub_port != new_monerod.zmq_pub_port:
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated ZMQ pub port",
                details=f"{monerod.zmq_pub_port()} > {new_monerod.zmq_pub_port()}",
            )
            monerod.zmq_pub_port(new_monerod.zmq_pub_port())
            update, update_config = True, True

        # ZMQ RPC Port
        if monerod.zmq_rpc_port != new_monerod.zmq_rpc_port:
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated ZMQ RPC port",
                details=f"{monerod.zmq_rpc_port()} > {new_monerod.zmq_rpc_port()}",
            )
            monerod.zmq_rpc_port(new_monerod.zmq_rpc_port())
            update, update_config = True, True

        # Log Level
        if monerod.log_level != new_monerod.log_level:
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated log level",
                details=f"{monerod.log_level()} > {new_monerod.log_level()}",
            )
            monerod.log_level(new_monerod.log_level())
            update, update_config = True, True

        # Max Log Files
        if monerod.max_log_files != new_monerod.max_log_files:
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated max log files",
                details=f"{monerod.max_log_files()} > {new_monerod.max_log_files()}",
            )
            monerod.max_log_files(new_monerod.max_log_files())
            update, update_config = True, True

        # Max Log Size
        if monerod.max_log_size != new_monerod.max_log_size:
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated max log size",
                details=f"{monerod.max_log_size()} > {new_monerod.max_log_size()}",
            )
            monerod.max_log_size(new_monerod.max_log_size())
            update, update_config = True, True

        # Priority Node 1 hostname
        if monerod.priority_node_1 != new_monerod.priority_node_1:
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated priority node 1",
                details=f"{monerod.priority_node_1()} > {new_monerod.priority_node_1()}",
            )
            monerod.priority_node_1(new_monerod.priority_node_1())
            update, update_config = True, True

        # Priority Port 1
        if monerod.priority_port_1 != new_monerod.priority_port_1:
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated priority port 1",
                details=f"{monerod.priority_port_1()} > {new_monerod.priority_port_1()}",
            )
            monerod.priority_port_1(new_monerod.priority_port_1())
            update, update_config = True, True

        # Priority Node 2 hostname
        if monerod.priority_node_2 != new_monerod.priority_node_2:
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated priority node 2",
                details=f"{monerod.priority_node_2()} > {new_monerod.priority_node_2()}",
            )
            monerod.priority_node_2(new_monerod.priority_node_2())
            update, update_config = True, True

        # Priority Port 2
        if monerod.priority_port_2 != new_monerod.priority_port_2:
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated priority port 2",
                details=f"{monerod.priority_port_2()} > {new_monerod.priority_port_2()}",
            )
            monerod.priority_port_2(new_monerod.priority_port_2())
            update, update_config = True, True

        # Update the configuration
        if update_config:
            vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
            tmpl_file = self.bs_mgr.get_template(DElem.MONEROD)
            monerod.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)

        # Update the database
        if update:
            monerod.version(DDef.MONEROD_VERSION)
            self.depl_db.update_one(monerod)

    def update_monerod_remote_deployment(self, new_monerod: MoneroDRemote):
        update = False
        monerod = self.get_deployment(DElem.MONEROD_REMOTE, new_monerod.instance())
        if not monerod:
            raise ValueError(
                f"DeplMgr:update_monerod_remote_deployment(): "
                f"No monerod found for {new_monerod.id()}"
            )

        ## Field-by-field comparison
        # IP Address
        if monerod.ip_addr != new_monerod.ip_addr:
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD_REMOTE,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated IP address",
                details=f"{monerod.ip_addr()} > {new_monerod.ip_addr()}",
            )
            monerod.ip_addr(new_monerod.ip_addr())
            update = True

        # RPC Bind Port
        if monerod.rpc_bind_port != new_monerod.rpc_bind_port:
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD_REMOTE,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated RPC bind port",
                details=f"{monerod.rpc_bind_port()} > {new_monerod.rpc_bind_port()}",
            )
            monerod.rpc_bind_port(new_monerod.rpc_bind_port())
            update = True

        # ZMQ Pub Port
        if monerod.zmq_pub_port != new_monerod.zmq_pub_port:
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD_REMOTE,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated ZMQ pub port",
                details=f"{monerod.zmq_pub_port()} > {new_monerod.zmq_pub_port()}",
            )
            monerod.zmq_pub_port(new_monerod.zmq_pub_port())
            update = True

        # Update the database
        if update:
            monerod = self.depl_db.update_one(monerod)

    def update_p2pool_deployment(self, new_p2pool):
        # Flags indicating what needs to be done at the end of the function
        update, update_config = False, False
        # Resolve which P2Pool type we're updating
        if new_p2pool.elem_type() == DElem.P2POOL:
            p2pool = self.get_deployment(DElem.P2POOL, new_p2pool.instance())
            p2pool_type = DElem.P2POOL
        else:
            p2pool = self.get_deployment(DElem.INT_P2POOL, new_p2pool.instance())
            p2pool_type = DElem.INT_P2POOL

        ## Field-by-field comparison
        # Enable/disable
        if p2pool.enabled() != new_p2pool.enabled():
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated enabled flag",
                details=f"{p2pool.enabled()} > {new_p2pool.enabled()}",
            )
            p2pool.enabled(new_p2pool.enabled())
            update = True

        # In Peers
        if p2pool.in_peers != new_p2pool.in_peers:
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated max incoming peers",
                details=f"{p2pool.in_peers()} > {new_p2pool.in_peers()}",
            )
            p2pool.in_peers(new_p2pool.in_peers())
            update_config, update = True, True

        # Out Peers
        if p2pool.out_peers != new_p2pool.out_peers:
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated max outbound peers",
                details=f"{p2pool.out_peers()} > {new_p2pool.out_peers()}",
            )
            p2pool.out_peers(new_p2pool.out_peers())
            update_config, update = True, True

        # P2P Bind Port
        if p2pool.p2p_port != new_p2pool.p2p_port:
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated P2P port",
                details=f"{p2pool.p2p_port()} > {new_p2pool.p2p_port()}",
            )
            p2pool.p2p_port(new_p2pool.p2p_port())
            update_config, update = True, True

        # Stratum port
        if p2pool.stratum_port != new_p2pool.stratum_port:
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated stratum port",
                details=f"{p2pool.stratum_port()} > {new_p2pool.stratum_port()}",
            )
            p2pool.stratum_port(new_p2pool.stratum_port())
            update_config, update = True, True

        # Log level
        if p2pool.log_level != new_p2pool.log_level:
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated log level",
                details=f"{p2pool.log_level()} > {new_p2pool.log_level()}",
            )
            p2pool.log_level(new_p2pool.log_level())
            update_config, update = True, True

        # Upstream Monerod
        if p2pool.parent != new_p2pool.parent:
            if new_p2pool.parent() == DField.DISABLE:
                self.ops_db.add_tui_log_line(
                    tracked_instance=p2pool.instance(),
                    tracked_type=p2pool_type,
                    status=DStatus.COMPLETE,
                    operation=DField.UPDATE,
                    message="Updated upstream MoneroD",
                    details=f"{p2pool.parent()} > DISABLE",
                )
            elif p2pool.parent() == DField.DISABLE:
                new_monerod = self.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=new_p2pool.parent()
                )
                new_instance = new_monerod.instance()
                self.ops_db.add_tui_log_line(
                    tracked_instance=p2pool.instance(),
                    tracked_type=p2pool_type,
                    status=DStatus.COMPLETE,
                    operation=DField.UPDATE,
                    message="Updated upstream MoneroD",
                    details=f"DISABLE > {new_instance}",
                )
            else:
                new_monerod = self.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=new_p2pool.parent()
                )
                new_instance = new_monerod.instance()
                monerod = self.get_deployment(DElem.MONEROD, p2pool.parent())
                old_instance = monerod.instance()
                self.ops_db.add_tui_log_line(
                    tracked_instance=p2pool.instance(),
                    tracked_type=p2pool_type,
                    status=DStatus.COMPLETE,
                    operation=DField.UPDATE,
                    message="Updated upstream MoneroD",
                    details=f"{old_instance} > {new_instance}",
                )
                p2pool.parent(new_p2pool.parent())
                update, update_config = True, True

        # Update the configuration file
        if update_config:
            vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
            tmpl_file = self.bs_mgr.get_template(DElem.P2POOL)
            p2pool.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)

        # Update the database
        if update:
            p2pool.version(DDef.P2POOL_VERSION)
            self.depl_db.update_one(p2pool)

    def update_p2pool_remote_deployment(self, new_p2pool: P2PoolRemote) -> P2PoolRemote:
        update = False
        p2pool = self.get_deployment(DElem.P2POOL_REMOTE, new_p2pool.instance())

        # IP Address
        if p2pool.ip_addr != new_p2pool.ip_addr:
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=DElem.P2POOL_REMOTE,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated IP/hostname",
                details=f"{p2pool.ip_addr()} > {new_p2pool.ip_addr()}",
            )
            p2pool.ip_addr(new_p2pool.ip_addr())
            update = True

        # Stratum Port
        if p2pool.stratum_port != new_p2pool.stratum_port:
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=DElem.P2POOL_REMOTE,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated stratum port",
                details=f"{p2pool.stratum_port()} > {new_p2pool.stratum_port()}",
            )
            p2pool.stratum_port(new_p2pool.stratum_port())
            update = True

        # Update the database
        if update:
            self.depl_db.update_one(p2pool)

    def update_vendor_dir(self, new_dir: str, old_dir: str, db4e: Db4E) -> Db4E:
        # print(f"DeplMgr:update_vendor_dir(): {old_dir} > {new_dir}")
        update_flag = True
        if old_dir == new_dir:
            return

        if not new_dir:
            raise ValueError(f"update_vendor_dir(): Missing new directory")

        # The target vendor dir exists, make a backup
        if os.path.exists(new_dir):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
            backup_vendor_dir = new_dir + "." + timestamp
            try:
                os.rename(new_dir, backup_vendor_dir)
                self.ops_db.add_tui_log_line(
                    tracked_type=DElem.DB4E,
                    tracked_instance=DLabel.VENDOR_DIR,
                    status=DStatus.WARN,
                    operation=DField.UPDATE,
                    message="Backed up vendor dir",
                    details=f"{new_dir} > {backup_vendor_dir}",
                )
            except (PermissionError, OSError) as e:
                update_flag = False
                self.ops_db.add_tui_log_line(
                    tracked_type=DElem.DB4E,
                    tracked_instance=DLabel.VENDOR_DIR,
                    status=DStatus.ERROR,
                    operation=DField.UPDATE,
                    message=f"Backup error",
                    details=f"{e}",
                )

        # No need to move if old_dir is empty (first-time initialization)
        if not old_dir:
            db4e.vendor_dir(new_dir)
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
                self.ops_db.add_tui_log_line(
                    tracked_type=DElem.DB4E,
                    tracked_instance=DLabel.VENDOR_DIR,
                    status=DStatus.COMPLETE,
                    operation=DField.UPDATE,
                    message="Created vendor dir",
                    details=f"{new_dir}",
                )
            return update_flag

        # Move the vendor_dir to the new location
        try:
            os.rename(old_dir, new_dir)
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.VENDOR_DIR,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Moved vendor dir",
                details=f"{old_dir} > {new_dir}",
            )

        except (PermissionError, OSError) as e:
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.VENDOR_DIR,
                status=DStatus.ERROR,
                operation=DField.UPDATE,
                message="Move error",
                details=f"{e}",
            )
            update_flag = False
        return update_flag

    def update_xmrig_deployment(self, new_xmrig: XMRig) -> XMRig:
        update = False
        update_config = False

        xmrig = self.get_deployment(DElem.XMRIG, new_xmrig.instance())

        # Enabled/disable flag
        if xmrig.enabled() != new_xmrig.enabled():
            # This is an enable/disable operation
            self.ops_db.add_tui_log_line(
                tracked_instance=xmrig.instance(),
                tracked_type=DElem.XMRIG,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated enabled flag",
                details=f"{xmrig.enabled()} > {new_xmrig.enabled()}",
            )
            xmrig.enabled(new_xmrig.enabled())
            update = True

        # Num Threads
        if xmrig.num_threads != new_xmrig.num_threads:
            self.ops_db.add_tui_log_line(
                tracked_instance=xmrig.instance(),
                tracked_type=DElem.XMRIG,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message="Updated number of threads",
                details=f"{xmrig.num_threads()} > {new_xmrig.num_threads()}",
            )
            xmrig.num_threads(new_xmrig.num_threads())
            update, update_config = True, True

        # Parent ID
        if xmrig.parent != new_xmrig.parent:

            # New XMRig's upstream P2Pool is unset
            if new_xmrig.parent() == DField.DISABLE:
                self.ops_db.add_tui_log_line(
                    tracked_instance=xmrig.instance(),
                    tracked_type=DElem.XMRIG,
                    status=DStatus.COMPLETE,
                    operation=DField.UPDATE,
                    message="Updated upstream P2Pool",
                    details=f"{xmrig.parent()} > DISABLE",
                )
                xmrig.parent(DField.DISABLE)
                update, update_config = True, False

            # New XMRig has a valid upstream P2Pool instance
            elif xmrig.parent() == DField.DISABLE:
                new_parent_instance = self.get_deployment_by_id(
                    elem_type=DElem.P2POOL, id=new_xmrig.parent()
                ).instance()
                self.ops_db.add_tui_log_line(
                    tracked_instance=xmrig.instance(),
                    tracked_type=DElem.XMRIG,
                    status=DStatus.COMPLETE,
                    message="Updated upstream P2Pool",
                    details=f"DISABLE > {new_parent_instance}",
                )
                xmrig.parent(new_xmrig.parent())
                update, update_config = True, True

            else:
                new_parent_instance = self.get_deployment_by_id(
                    elem_type=DElem.P2POOL, id=new_xmrig.parent()
                ).instance()
                parent_instance = self.get_deployment_by_id(
                    elem_type=DElem.P2POOL, id=xmrig.parent()
                ).instance()
                self.ops_db.add_tui_log_line(
                    tracked_instance=xmrig.instance(),
                    tracked_type=DElem.XMRIG,
                    status=DStatus.COMPLETE,
                    message="Updated upstream P2Pool",
                    details=f"{parent_instance} > {new_parent_instance}",
                )
                xmrig.parent(new_xmrig.parent())
                update, update_config = True, True

        # Regenerate config if required
        if update_config:
            vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
            tmpl_file = self.bs_mgr.get_template(DElem.XMRIG)
            xmrig.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)

        if update:
            xmrig.version(DDef.XMRIG_VERSION)
            self.depl_db.update_one(xmrig)
