# db4e/mgr/DeplMgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

import os
from datetime import datetime
from shutil import rmtree
import socket
from typing import overload
import subprocess

from db4e.mgr.BootstrapMgr import BootstrapMgr
from db4e.util.Db4ELogger import Db4ELogger
from db4e.db.DeplDb import DeplDb
from db4e.db.OpsDb import OpsDb

from db4e.recs.monero.Db4E import Db4E
from db4e.recs.monero.P2PoolInternal import P2PoolInternal
from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.BaseP2Pool import CHAIN_TO_CHAIN_LABEL_MAP
from db4e.recs.monero.XMRig import XMRig
from db4e.recs.monero.XMRigRemote import XMRigRemote
from db4e.util.Helper import sudo_del_file

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
from db4e.constants.DSQL import DTable


class Default:
    """
    Default constants and template identifiers used by the deployment manager.
    """

    MONEROD_VERSION = DDef.MONEROD_VERSION
    P2POOL_VERSION = DDef.P2POOL_VERSION
    XMRIG_VERSION = DDef.XMRIG_VERSION
    MONEROD_CONFIG = DDef.MONEROD_CONFIG
    P2POOL_CONFIG = DDef.P2POOL_CONFIG
    PYTHON = DDef.PYTHON
    XMRIG_CONFIG = DDef.XMRIG_CONFIG


class DeplMgr:
    """
    Deployment manager for adding, updating, and deleting runtime deployments.
    """

    # update_p2pool_deployment() is overloaded ...
    @overload
    def update_p2pool_deployment(self, p2pool: P2Pool) -> P2Pool: ...
    @overload
    def update_p2pool_deployment(self, p2pool: P2PoolInternal) -> P2PoolInternal: ...

    def __init__(
        self,
        bs_mgr: BootstrapMgr,
        depl_db: DeplDb,
        ops_db: OpsDb,
        sql_db=None,
        log_file=None,
    ):
        """
        Initialize the deployment manager.

        :param bs_mgr: Bootstrap manager for directory and template access.
        :type bs_mgr: BootstrapMgr
        :param depl_db: Deployment database manager.
        :type depl_db: DeplDb
        :param ops_db: Operations database manager.
        :type ops_db: OpsDb
        :param sql_db: Optional SQL database wrapper.
        :type sql_db: SQLDb or None
        """
        self.bs_mgr = bs_mgr
        self.depl_db = depl_db
        self.ops_db = ops_db
        self.sql_db = sql_db
        if log_file:
            self.log = Db4ELogger(db4e_module=DModule.DEPLOYMENT_MGR, log_file=log_file)

    def add_deployment(self, elem):
        """
        Dispatch to the appropriate add handler for a deployment element.

        :param elem: Deployment object to add.
        :type elem: object
        :return: The created deployment object.
        :rtype: object
        """
        elem_class = type(elem)
        # Add the core Db4E deployment
        if elem_class == Db4E:
            return self.add_db4e_deployment(elem)

        # Add a remote Monero daemon deployment
        elif elem_class == MoneroD:
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

        # Add an Internal P2Pool deployment
        elif elem_class == P2PoolInternal:
            return self.add_internal_p2pool_deployment(elem)

        # Add a XMRig deployment
        elif elem_class == XMRig:
            return self.add_xmrig_deployment(elem)

        # Add a remote XMRig deployment
        elif elem_class == XMRigRemote:
            return self.add_remote_xmrig_deployment(elem)

        # Catchall
        else:
            self.log.error(f"ERROR: Unrcognized element {elem}")
            raise ValueError(f"DeplMgr:add_deployment(): No handler for {elem_class}")

    def add_db4e_deployment(self, db4e: Db4E) -> Db4E:
        """
        Add the core Db4E deployment which includes the Db4E service.

        :param db4e: Db4E deployment object.
        :type db4e: Db4E
        :return: The created cb4e deployment object.
        :rtype: Db4E
        """
        db4e = self.depl_db.insert_one(db4e)
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.DB4E,
            tracked_instance=db4e.instance(),
            status=DStatus.COMPLETE,
            operation=DField.NEW,
            message="New deployment",
        )
        return db4e

    def add_monerod_deployment(self, monerod: MoneroD) -> MoneroD:
        """
        Add a local MoneroD deployment and generate its filesystem artifacts.

        :param monerod: MoneroD deployment object.
        :type monerod: MoneroD
        :return: The created MoneroD deployment object.
        :rtype: MoneroD
        """
        if not monerod.ip_addr():
            monerod.ip_addr(socket.gethostname())
        tmpl_file = self.bs_mgr.get_template(DElem.MONEROD)

        # Monero log file
        os.makedirs(
            os.path.join(
                DDef.DB4E_INSTALL_DIR, DDir.MONEROD, monerod.instance(), DDef.LOG_DIR
            ),
            exist_ok=True,
        )
        monerod.log_file(
            os.path.join(
                DDef.DB4E_INSTALL_DIR,
                DDir.MONEROD,
                monerod.instance(),
                DDef.LOG_DIR,
                DDef.MONEROD_LOG_FILE,
            )
        )

        # Blockchain directory
        os.makedirs(
            os.path.join(
                DDef.DB4E_INSTALL_DIR,
                DDir.MONEROD,
                monerod.instance(),
                DDef.BLOCKCHAIN_DIR,
            ),
            exist_ok=True,
        )
        monerod.blockchain_dir(
            os.path.join(
                DDef.DB4E_INSTALL_DIR,
                DDir.MONEROD,
                monerod.instance(),
                DDef.BLOCKCHAIN_DIR,
            )
        )

        # Run directory
        os.makedirs(
            os.path.join(
                DDef.DB4E_INSTALL_DIR, DDir.MONEROD, monerod.instance(), DDef.RUN_DIR
            ),
            exist_ok=True,
        )

        # Path to STDIN named pipe
        monerod.stdin_path(
            os.path.join(
                DDef.DB4E_INSTALL_DIR,
                DDir.MONEROD,
                monerod.instance(),
                DDef.RUN_DIR,
                DDef.MONEROD_STDIN_PIPE,
            )
        )

        # Generate the configuration
        monerod.gen_config(tmpl_file=tmpl_file)

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
        """
        Add a remote MoneroD deployment.

        :param monerod: Remote MoneroD deployment object.
        :type monerod: MoneroDRemote
        :return: The created MoneroDRemote deployment object.
        :rtype: MoneroDRemote
        """
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
        """
        Add a local P2Pool deployment and generate its filesystem artifacts.

        :param p2pool: P2Pool deployment object.
        :type p2pool: P2Pool
        :return: The created P2Pool deployment object.
        :rtype: P2Pool
        """
        # Generate the configuration
        db4e = self.depl_db.get_deployment(DElem.DB4E, DElem.DB4E)
        if not p2pool.any_ip():
            p2pool.any_ip(socket.gethostname())

        if p2pool.parent() != DField.DISABLE:
            tmpl_file = self.bs_mgr.get_template(DElem.P2POOL)
            # Upstream monero daemon is remote
            if p2pool.parent_remote():
                p2pool.monerod = self.depl_db.get_deployment_by_id(
                    DElem.MONEROD_REMOTE, p2pool.parent()
                )
            # Upstream monero daemon is local
            else:
                p2pool.monerod = self.depl_db.get_deployment_by_id(
                    DElem.MONEROD, p2pool.parent()
                )
            # Uptream monero daemon deployment has been deleted
            if not p2pool.monerod:
                p2pool.parent(DField.DISABLE)

            # We need to know the upstream Monero to build a config
            if p2pool.parent() != DField.DISABLE:
                # Add the user's Monero wallet to the instance's record
                p2pool.user_wallet(db4e.user_wallet())
                p2pool.gen_config(tmpl_file=tmpl_file)

        p2pool.log_file(
            os.path.join(
                DDef.DB4E_INSTALL_DIR,
                DDir.P2POOL,
                p2pool.instance(),
                DDef.LOG_DIR,
                DFile.P2POOL_LOG,
            )
        )
        # Create the per-instance directories
        os.makedirs(
            os.path.join(
                DDef.DB4E_INSTALL_DIR, DDir.P2POOL, p2pool.instance(), DDef.LOG_DIR
            ),
            exist_ok=True,
        )
        os.makedirs(
            os.path.join(
                DDef.DB4E_INSTALL_DIR, DDir.P2POOL, p2pool.instance(), DDef.API_DIR
            ),
            exist_ok=True,
        )
        os.makedirs(
            os.path.join(
                DDef.DB4E_INSTALL_DIR, DDir.P2POOL, p2pool.instance(), DDef.RUN_DIR
            ),
            exist_ok=True,
        )
        p2pool.stdin_path(
            os.path.join(
                DDef.DB4E_INSTALL_DIR,
                DDir.P2POOL,
                p2pool.instance(),
                DDef.RUN_DIR,
                DFile.P2POOL_STDIN,
            )
        )
        # Generate the logrotate configuration file
        logrotate_tmpl = self.bs_mgr.get_logrotate_template(DElem.P2POOL)
        db4e_group = db4e.db4e_group()
        p2pool.gen_logrotate_config(tmpl_file=logrotate_tmpl, db4e_group=db4e_group)

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
        """
        Add a remote P2Pool deployment.

        :param p2pool: Remote P2Pool deployment object.
        :type p2pool: P2PoolRemote
        :return: The created P2PoolRemote deployment object.
        :rtype: P2PoolRemote
        """
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

    def add_internal_p2pool_deployment(self, p2pool: P2PoolInternal) -> P2PoolInternal:
        """
        Add an internal P2Pool deployment.

        :param p2pool: Internal P2Pool deployment object.
        :type p2pool: P2PoolInternal
        :return: The created P2PoolInternal deployment object.
        :rtype: P2PoolInternal
        """
        p2pool = self.depl_db.insert_one(p2pool)
        # Create a console log message
        self.ops_db.add_tui_log_line(
            tracked_type=DElem.P2POOL_INTERNAL,
            tracked_instance=f"{p2pool.instance()} Sidechain",
            status=DStatus.COMPLETE,
            operation=DField.NEW,
            message="New deployment",
        )
        return p2pool

    def add_xmrig_deployment(self, xmrig: XMRig) -> XMRig:
        """
        Add a local XMRig deployment and generate its filesystem artifacts.

        :param xmrig: XMRig deployment object.
        :type xmrig: XMRig
        :return: The created XMRig deployment object.
        :rtype: XMRig
        """
        # Generate the XMRig configuration
        if xmrig.parent() != DField.DISABLE:
            # Generate the configuration
            tmpl_file = self.bs_mgr.get_template(DElem.XMRIG)

            # Upstream P2Pool is remote
            if xmrig.parent_remote():
                xmrig.p2pool = self.depl_db.get_deployment_by_id(
                    DElem.P2POOL_REMOTE, xmrig.parent()
                )
            # Upstream P2Pool is local
            xmrig.p2pool = self.depl_db.get_deployment_by_id(
                DElem.P2POOL, xmrig.parent()
            )

            # Upstream P2Pool deployment has been deleted
            if not xmrig.p2pool:
                xmrig.parent(DField.DISABLE)

            # We need an upstream P2Pool intance to generate the config
            if xmrig.parent() != DField.DISABLE:
                xmrig.gen_config(tmpl_file=tmpl_file)

        # Set the location of the instance's log file
        xmrig.log_file(
            os.path.join(
                DDef.DB4E_INSTALL_DIR,
                DElem.XMRIG,
                DDef.LOG_DIR,
                xmrig.instance() + ".log",
            )
        )

        # Generate the logrotate configuration file
        logrotate_tmpl = self.bs_mgr.get_logrotate_template(DElem.XMRIG)
        xmrig.gen_logrotate_config(tmpl_file=logrotate_tmpl)
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
        for remote_xmrig in self.depl_db.get_xmrig_remotes():
            if remote_xmrig.instance() == xmrig.instance():
                # TODO route to update() so the timestamp is updated.
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

    def delete_deployment(self, elem):
        """
        Delete a deployment and remove its filesystem artifacts.

        :param elem: Deployment object to delete.
        :type elem: object
        """
        if type(elem) == MoneroD:
            tracked_type = DElem.MONEROD
            # Delete filesystem artifacts
            config = elem.config_file()
            if os.path.exists(config):
                os.remove(config)
            depl_dir = os.path.join(
                DDef.DB4E_INSTALL_DIR, DDir.MONEROD, elem.instance()
            )
            if os.path.isdir(depl_dir):
                rmtree(depl_dir)

        elif type(elem) == MoneroDRemote:
            tracked_type = DElem.MONEROD_REMOTE

        elif type(elem) == P2Pool:
            tracked_type = DElem.P2POOL
            config = elem.config_file()
            if os.path.exists(config):
                os.remove(config)
            logrotate_config = elem.logrotate_config()
            sudo_del_file(logrotate_config)
            depl_dir = os.path.join(DDef.DB4E_INSTALL_DIR, DDir.P2POOL, elem.instance())
            if os.path.isdir(depl_dir):
                rmtree(depl_dir)

        elif type(elem) == P2PoolRemote:
            tracked_type = DElem.P2POOL_REMOTE

        elif type(elem) == XMRig:
            tracked_type = DElem.XMRIG
            config = elem.config_file()
            if os.path.exists(config):
                os.remove(config)
            logrotate_config = elem.logrotate_config()
            sudo_del_file(logrotate_config)
            depl_dir = os.path.join(DDef.DB4E_INSTALL_DIR, DElem.XMRIG, elem.instance())
            if os.path.isdir(depl_dir):
                rmtree(depl_dir)

        elif type(elem) == XMRigRemote:
            tracked_type = DElem.XMRIG_REMOTE

        else:
            raise ValueError(f"DeplMgr:delete_deployment(): No handler for {elem}")

        self.depl_db.delete_deployment(elem)
        # Create a console log message
        self.ops_db.add_tui_log_line(
            tracked_type=tracked_type,
            tracked_instance=elem.instance(),
            status=DStatus.COMPLETE,
            operation=DField.DELETE,
            message="Deleted deployment",
        )

    def disable_deployment(self, elem, elem_type):
        self.depl_db.disable_deployment(elem)
        self.ops_db.add_tui_log_line(
            tracked_type=elem_type,
            tracked_instance=elem.instance(),
            status=DStatus.COMPLETE,
            operation=DField.STOPPED,
            message="Stopped deployment",
        )

    def enable_deployment(self, elem, elem_type):
        self.depl_db.enable_deployment(elem)
        self.ops_db.add_tui_log_line(
            tracked_type=elem_type,
            tracked_instance=elem.instance(),
            status=DStatus.COMPLETE,
            operation=DField.STARTED,
            message="Started deployment",
        )

    def update_db4e_deployment(self, new_db4e: Db4E):
        """
        Update the Db4E deployment record and propagate dependent changes.

        :param new_db4e: Updated Db4E deployment object.
        :type new_db4e: Db4E
        """
        update_flag = False
        update_p2pool_flag = False
        # The current record, we'll update this and write it back in
        db4e = self.depl_db.get_deployment(elem_type=DElem.DB4E, instance=DLabel.DB4E)

        # Updating user wallet
        if db4e.user_wallet() != new_db4e.user_wallet():
            # Create a console log message
            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.DB4E,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.USER_WALLET,
                details=f"{db4e.user_wallet()[:6]}... > {new_db4e.user_wallet()[:6]}...",
            )
            db4e.user_wallet(new_db4e.user_wallet())
            update_flag, update_p2pool_flag = True, True

        ## Updating the primary server
        # Keep the original primary_server for the primary_remote update
        # below.
        if (
            db4e.primary_server() != new_db4e.primary_server()
            or db4e.primary_remote != new_db4e.primary_remote()
        ):
            # The primary server is configured with two attributes:
            # 1. primary_server: The ID of the row in SQLite for the Monero or Remote Monero
            # instance or -1 if the primary server is disabled.
            # 2. primary_remote:
            #    Value of 1  : Primary server is remote (monerod_remote table)
            #    Value of 0  : Primary server is local (monerod table)
            #    Value of -1 : Primary server is disabled
            #

            if db4e.primary_server() == DField.DISABLE:
                old_instance = "DISABLE"
            else:
                if db4e.primary_remote():
                    old_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.MONEROD_REMOTE, id=db4e.primary_server()
                    ).instance()
                else:
                    old_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.MONEROD, id=db4e.primary_server()
                    ).instance()

            if new_db4e.primary_server() == DField.DISABLE:
                new_instance = "DISABLE"
                new_db4e.primary_remote(DField.DISABLE)
            else:
                if new_db4e.primary_remote():
                    new_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.MONEROD_REMOTE, id=new_db4e.primary_server()
                    ).instance()
                else:
                    new_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.MONEROD, id=new_db4e.primary_server()
                    ).instance()

            db4e.primary_server(new_db4e.primary_server())
            db4e.primary_remote(new_db4e.primary_remote())

            self.ops_db.add_tui_log_line(
                tracked_type=DElem.DB4E,
                tracked_instance=DLabel.DB4E,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.PRIMARY_SERVER,
                details=f"{old_instance} > {new_instance}",
            )
            update_flag, update_p2pool_flag = True, True

        # Update the database
        if update_flag:
            self.depl_db.update_one(db4e)

        # Update the P2Pool instances
        if update_p2pool_flag:
            # Internal P2Pool instances
            for p2pool in self.depl_db.get_p2pool_internals():
                p2pool.parent(db4e.primary_server())
                p2pool.parent_remote(db4e.primary_remote())
                self.update_deployment(p2pool)
            # Local P2Pool instances
            for p2pool in self.depl_db.get_p2pools():
                p2pool.user_wallet(db4e.user_wallet())
                self.update_deployment(p2pool)

    def update_deployment(self, elem):
        """
        Dispatch to the appropriate update handler for a deployment element.

        :param elem: Deployment object with updated values.
        :type elem: object
        :return: Updated deployment object, if applicable.
        :rtype: object
        """
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
        """
        Update a local MoneroD deployment.

        :param new_monerod: Updated MoneroD deployment object.
        :type new_monerod: MoneroD
        """
        # Flags to indicate if we're updaing the DB and/or the startup config
        update, update_config = False, False
        # print(f"DeplMgr:update_monerod_deployment(): {new_monerod}")
        # Retrive the current/old deployment
        monerod = self.depl_db.get_deployment(DElem.MONEROD, new_monerod.instance())
        if not monerod:
            raise ValueError(
                f"DeplMgr:update_monerod_deployment(): "
                f"No monerod found for {new_monerod}"
            )

        # Blockchain dir
        if monerod.blockchain_dir() != new_monerod.blockchain_dir():
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.BLOCKCHAIN_DIR,
                details=f"{monerod.blockchain_dir()} > {new_monerod.blockchain_dir()}",
            )
            monerod.blockchain_dir(new_monerod.blockchain_dir())
            update, update_config = True, True

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
                message=DLabel.ENABLED_FLAG,
                details=f"{monerod.enabled()} > {new_monerod.enabled()}",
            )
            update = True

        # In Peers
        if monerod.in_peers() != new_monerod.in_peers():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.IN_PEERS,
                details=f"{monerod.in_peers()} > {new_monerod.in_peers()}",
            )
            monerod.in_peers(new_monerod.in_peers())
            update, update_config = True, True

        # IP Address
        if monerod.ip_addr() != new_monerod.ip_addr():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.IP_ADDR,
                details=f"{monerod.ip_addr()} > {new_monerod.ip_addr()}",
            )
            monerod.ip_addr(new_monerod.ip_addr())
            update, update_config = True, True

        # Log Level
        if monerod.log_level() != new_monerod.log_level():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.LOG_LEVEL,
                details=f"{monerod.log_level()} > {new_monerod.log_level()}",
            )
            monerod.log_level(new_monerod.log_level())
            update, update_config = True, True

        # Out Peers
        if monerod.out_peers() != new_monerod.out_peers():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.OUT_PEERS,
                details=f"{monerod.out_peers()} > {new_monerod.out_peers()}",
            )
            monerod.out_peers(new_monerod.out_peers())
            update, update_config = True, True

        # P2P Bind Port
        if monerod.p2p_bind_port() != new_monerod.p2p_bind_port():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.P2P_BIND_PORT,
                details=f"{monerod.p2p_bind_port()} > {new_monerod.p2p_bind_port()}",
            )
            monerod.p2p_bind_port(new_monerod.p2p_bind_port())
            update, update_config = True, True

        # RPC Bind Port
        if monerod.rpc_bind_port() != new_monerod.rpc_bind_port():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.RPC_BIND_PORT,
                details=f"{monerod.rpc_bind_port()} > {new_monerod.rpc_bind_port()}",
            )
            monerod.rpc_bind_port(new_monerod.rpc_bind_port())
            update, update_config = True, True

        # Max Log Files
        if monerod.max_log_files() != new_monerod.max_log_files():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.MAX_LOG_FILES,
                details=f"{monerod.max_log_files()} > {new_monerod.max_log_files()}",
            )
            monerod.max_log_files(new_monerod.max_log_files())
            update, update_config = True, True

        # Max Log Size
        if monerod.max_log_size() != new_monerod.max_log_size():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.MAX_LOG_SIZE,
                details=f"{monerod.max_log_size()} > {new_monerod.max_log_size()}",
            )
            monerod.max_log_size(new_monerod.max_log_size())
            update, update_config = True, True

        # Priority Node 1 hostname
        if monerod.priority_node_1() != new_monerod.priority_node_1():
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.PRIORITY_NODE_1,
                details=f"{monerod.priority_node_1()} > {new_monerod.priority_node_1()}",
            )
            monerod.priority_node_1(new_monerod.priority_node_1())
            update, update_config = True, True

        # Priority Port 1
        if monerod.priority_port_1() != new_monerod.priority_port_1():
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.PRIORITY_PORT_1,
                details=f"{monerod.priority_port_1()} > {new_monerod.priority_port_1()}",
            )
            monerod.priority_port_1(new_monerod.priority_port_1())
            update, update_config = True, True

        # Priority Node 2 hostname
        if monerod.priority_node_2() != new_monerod.priority_node_2():
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.PRIORITY_NODE_2,
                details=f"{monerod.priority_node_2()} > {new_monerod.priority_node_2()}",
            )
            monerod.priority_node_2(new_monerod.priority_node_2())
            update, update_config = True, True

        # Priority Port 2
        if monerod.priority_port_2() != new_monerod.priority_port_2():
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.PRIORITY_PORT_2,
                details=f"{monerod.priority_port_2()} > {new_monerod.priority_port_2()}",
            )
            monerod.priority_port_2(new_monerod.priority_port_2())
            update, update_config = True, True

        # Max Log Files
        if monerod.max_log_files() != new_monerod.max_log_files():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.MAX_LOG_FILES,
                details=f"{monerod.max_log_files()} > {new_monerod.max_log_files()}",
            )
            monerod.max_log_files(new_monerod.max_log_files())
            update, update_config = True, True

        # Max Log Size
        if monerod.max_log_size() != new_monerod.max_log_size():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.MAX_LOG_SIZE,
                details=f"{monerod.max_log_size()} > {new_monerod.max_log_size()}",
            )
            monerod.max_log_size(new_monerod.max_log_size())
            update, update_config = True, True

        # ZMQ Pub Port
        if monerod.zmq_pub_port() != new_monerod.zmq_pub_port():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.ZMQ_PUB_PORT,
                details=f"{monerod.zmq_pub_port()} > {new_monerod.zmq_pub_port()}",
            )
            monerod.zmq_pub_port(new_monerod.zmq_pub_port())
            update, update_config = True, True

        # ZMQ RPC Port
        if monerod.zmq_rpc_port() != new_monerod.zmq_rpc_port():
            # Create console log line
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.ZMQ_RPC_PORT,
                details=f"{monerod.zmq_rpc_port()} > {new_monerod.zmq_rpc_port()}",
            )
            monerod.zmq_rpc_port(new_monerod.zmq_rpc_port())
            update, update_config = True, True

        # Update the configuration
        if update_config:
            tmpl_file = self.bs_mgr.get_template(DElem.MONEROD)
            monerod.gen_config(tmpl_file=tmpl_file)

        # Update the database
        if update:
            monerod.version(DDef.MONEROD_VERSION)
            self.depl_db.update_one(monerod)

    def update_monerod_remote_deployment(self, new_monerod: MoneroDRemote):
        """
        Update a remote MoneroD deployment.

        :param new_monerod: Updated MoneroDRemote deployment object.
        :type new_monerod: MoneroDRemote
        """
        update = False
        monerod = self.depl_db.get_deployment(
            DElem.MONEROD_REMOTE, new_monerod.instance()
        )
        if not monerod:
            raise ValueError(
                f"DeplMgr:update_monerod_remote_deployment(): "
                f"No monerod found for {new_monerod.id()}"
            )

        ## Field-by-field comparison
        # IP Address
        if monerod.ip_addr() != new_monerod.ip_addr():
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD_REMOTE,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.IP_ADDR,
                details=f"{monerod.ip_addr()} > {new_monerod.ip_addr()}",
            )
            monerod.ip_addr(new_monerod.ip_addr())
            update = True

        # RPC Bind Port
        if monerod.rpc_bind_port() != new_monerod.rpc_bind_port():
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD_REMOTE,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.RPC_BIND_PORT,
                details=f"{monerod.rpc_bind_port()} > {new_monerod.rpc_bind_port()}",
            )
            monerod.rpc_bind_port(new_monerod.rpc_bind_port())
            update = True

        # ZMQ Pub Port
        if monerod.zmq_pub_port() != new_monerod.zmq_pub_port():
            self.ops_db.add_tui_log_line(
                tracked_instance=monerod.instance(),
                tracked_type=DElem.MONEROD_REMOTE,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.ZMQ_PUB_PORT,
                details=f"{monerod.zmq_pub_port()} > {new_monerod.zmq_pub_port()}",
            )
            monerod.zmq_pub_port(new_monerod.zmq_pub_port())
            update = True

        # Update the database
        if update:
            monerod = self.depl_db.update_one(monerod)

    def update_p2pool_deployment(self, new_p2pool):
        """
        Update a local or internal P2Pool deployment.

        :param new_p2pool: Updated P2Pool or P2PoolInternal deployment object.
        :type new_p2pool: P2Pool or P2PoolInternal
        """
        # Flags indicating what needs to be done at the end of the function
        update, update_config = False, False
        # Resolve which P2Pool type we're updating
        if type(new_p2pool) == P2Pool:
            p2pool = self.depl_db.get_deployment(DElem.P2POOL, new_p2pool.instance())
            p2pool_type = DElem.P2POOL
        elif type(new_p2pool) == P2PoolInternal:
            p2pool = self.depl_db.get_deployment(
                DElem.P2POOL_INTERNAL, new_p2pool.instance()
            )
            p2pool_type = DElem.P2POOL_INTERNAL

        ## Field-by-field comparison
        # Enable/disable
        if p2pool.enabled() != new_p2pool.enabled():
            # Create console log line
            if p2pool.enabled():
                old_flag = "ENABLED"
            else:
                old_flag = "DISABLED"
            if new_p2pool.enabled():
                new_flag = "ENABLED"
            else:
                new_flag = "DISABLED"
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.ENABLED_FLAG,
                details=f"{old_flag} > {new_flag}",
            )
            p2pool.enabled(new_p2pool.enabled())
            update = True

        # In Peers
        if p2pool.in_peers() != new_p2pool.in_peers():
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.IN_PEERS,
                details=f"{p2pool.in_peers()} > {new_p2pool.in_peers()}",
            )
            p2pool.in_peers(new_p2pool.in_peers())
            update_config, update = True, True

        # Out Peers
        if p2pool.out_peers() != new_p2pool.out_peers():
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.OUT_PEERS,
                details=f"{p2pool.out_peers()} > {new_p2pool.out_peers()}",
            )
            p2pool.out_peers(new_p2pool.out_peers())
            update_config, update = True, True

        # P2P Bind Port
        if p2pool.p2p_port() != new_p2pool.p2p_port():
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.P2P_PORT,
                details=f"{p2pool.p2p_port()} > {new_p2pool.p2p_port()}",
            )
            p2pool.p2p_port(new_p2pool.p2p_port())
            update_config, update = True, True

        # Stratum port
        if p2pool.stratum_port() != new_p2pool.stratum_port():
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.STRATUM_PORT,
                details=f"{p2pool.stratum_port()} > {new_p2pool.stratum_port()}",
            )
            p2pool.stratum_port(new_p2pool.stratum_port())
            update_config, update = True, True

        # Log level
        if p2pool.log_level() != new_p2pool.log_level():
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.LOG_LEVEL,
                details=f"{p2pool.log_level()} > {new_p2pool.log_level()}",
            )
            p2pool.log_level(new_p2pool.log_level())
            update_config, update = True, True

        ## Upstream Monerod
        if (
            p2pool.parent() != new_p2pool.parent()
            or p2pool.parent_remote() != new_p2pool.parent_remote()
        ):

            if new_p2pool.parent() == DField.DISABLE:
                new_instance = "DISABLE"
            else:
                if new_p2pool.parent_remote():
                    new_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.MONEROD_REMOTE, id=new_p2pool.parent()
                    ).instance()
                else:
                    new_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.MONEROD, id=new_p2pool.parent()
                    ).instance()
                update_config = True

            if p2pool.parent() == DField.DISABLE:
                old_instance = "DISABLE"
            else:
                if p2pool.parent_remote():
                    old_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.MONEROD_REMOTE, id=p2pool.parent()
                    ).instance()
                else:
                    old_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.MONEROD, id=p2pool.parent()
                    ).instance()

            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=f"Upstream {DLabel.MONEROD_SHORT}",
                details=f"{old_instance} > {new_instance}",
            )
            p2pool.parent(new_p2pool.parent())
            p2pool.parent_remote(new_p2pool.parent_remote())
            update = True

        # Switching chains
        if p2pool.chain() != new_p2pool.chain():
            old_label = CHAIN_TO_CHAIN_LABEL_MAP[p2pool.chain()]
            new_label = CHAIN_TO_CHAIN_LABEL_MAP[new_p2pool.chain()]
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=p2pool_type,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.CHAIN,
                details=f"{old_label} > {new_label}",
            )
            p2pool.chain(new_p2pool.chain())
            update, update_config = True, True

        # Update the configuration file
        if update_config:
            tmpl_file = self.bs_mgr.get_template(DElem.P2POOL)
            ## Get the upstream monero deployment
            # Check if it's local or remote:
            if p2pool.parent_remote():
                elem_type = DElem.MONEROD_REMOTE
            else:
                elem_type = DElem.MONEROD
            p2pool.monerod = self.depl_db.get_deployment_by_id(
                elem_type=elem_type, id=p2pool.parent()
            )
            p2pool.gen_config(tmpl_file=tmpl_file)

        # Update the database
        if update:
            p2pool.version(DDef.P2POOL_VERSION)
            self.depl_db.update_one(p2pool)

    def update_p2pool_remote_deployment(self, new_p2pool: P2PoolRemote) -> P2PoolRemote:
        """
        Update a remote P2Pool deployment.

        :param new_p2pool: Updated P2PoolRemote deployment object.
        :type new_p2pool: P2PoolRemote
        :return: Updated P2PoolRemote deployment object.
        :rtype: P2PoolRemote
        """
        update = False
        p2pool = self.depl_db.get_deployment(DElem.P2POOL_REMOTE, new_p2pool.instance())

        # IP Address
        if p2pool.ip_addr() != new_p2pool.ip_addr():
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=DElem.P2POOL_REMOTE,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.IP_ADDR,
                details=f"{p2pool.ip_addr()} > {new_p2pool.ip_addr()}",
            )
            p2pool.ip_addr(new_p2pool.ip_addr())
            update = True

        # Stratum Port
        if p2pool.stratum_port() != new_p2pool.stratum_port():
            self.ops_db.add_tui_log_line(
                tracked_instance=p2pool.instance(),
                tracked_type=DElem.P2POOL_REMOTE,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.STRATUM_PORT,
                details=f"{p2pool.stratum_port()} > {new_p2pool.stratum_port()}",
            )
            p2pool.stratum_port(new_p2pool.stratum_port())
            update = True

        # Update the database
        if update:
            self.depl_db.update_one(p2pool)

    def update_xmrig_deployment(self, new_xmrig: XMRig) -> XMRig:
        """
        Update a local XMRig deployment.

        :param new_xmrig: Updated XMRig deployment object.
        :type new_xmrig: XMRig
        :return: Updated XMRig deployment object.
        :rtype: XMRig
        """
        update, update_config = False, False

        xmrig = self.depl_db.get_deployment(DElem.XMRIG, new_xmrig.instance())

        # Enabled/disable flag
        if xmrig.enabled() != new_xmrig.enabled():
            # This is an enable/disable operation
            self.ops_db.add_tui_log_line(
                tracked_instance=xmrig.instance(),
                tracked_type=DElem.XMRIG,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.ENABLED_FLAG,
                details=f"{xmrig.enabled()} > {new_xmrig.enabled()}",
            )
            xmrig.enabled(new_xmrig.enabled())
            update = True

        # Num Threads
        if xmrig.num_threads() != new_xmrig.num_threads():
            self.ops_db.add_tui_log_line(
                tracked_instance=xmrig.instance(),
                tracked_type=DElem.XMRIG,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=DLabel.NUM_THREADS,
                details=f"{xmrig.num_threads()} > {new_xmrig.num_threads()}",
            )
            xmrig.num_threads(new_xmrig.num_threads())
            update, update_config = True, True

        # Parent ID
        if (
            xmrig.parent() != new_xmrig.parent()
            or xmrig.parent_remote() != new_xmrig.parent_remote()
        ):

            # New XMRig's upstream P2Pool is unset
            if new_xmrig.parent() == DField.DISABLE:
                new_instance = "DISABLE"
            else:
                # New upstream P2Pool is remote
                if new_xmrig.parent_remote():
                    new_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.P2POOL_REMOTE, id=new_xmrig.parent()
                    ).instance()
                # New upstream P2Pool is local
                else:
                    new_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.P2POOL, id=new_xmrig.parent()
                    ).instance()
                update_config = True

            # Old XMRig's upstream P2Pool is unset
            if xmrig.parent() == DField.DISABLE:
                old_instance = "DISABLE"
            else:
                # Old upstream P2Pool is remote
                if xmrig.parent_remote():
                    old_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.P2POOL_REMOTE, id=xmrig.parent()
                    ).instance()
                # Old upstream P2Pool is local
                else:
                    old_instance = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.P2POOL, id=xmrig.parent()
                    ).instance()

            self.ops_db.add_tui_log_line(
                tracked_instance=xmrig.instance(),
                tracked_type=DElem.XMRIG,
                status=DStatus.COMPLETE,
                operation=DField.UPDATE,
                message=f"Upstream {DLabel.P2POOL_SHORT}",
                details=f"{old_instance} > {new_instance}",
            )
            xmrig.parent(new_xmrig.parent())
            xmrig.parent_remote(new_xmrig.parent_remote())
            update = True

        # Regenerate config if required
        if update_config:
            tmpl_file = self.bs_mgr.get_template(DElem.XMRIG)
            if xmrig.parent() != DField.DISABLE:
                if xmrig.parent_remote():
                    xmrig.p2pool = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.P2POOL_REMOTE, id=xmrig.parent()
                    )
                else:
                    xmrig.p2pool = self.depl_db.get_deployment_by_id(
                        elem_type=DElem.P2POOL, id=xmrig.parent()
                    )
            xmrig.gen_config(tmpl_file=tmpl_file)

        if update:
            xmrig.version(DDef.XMRIG_VERSION)
            self.depl_db.update_one(xmrig)
