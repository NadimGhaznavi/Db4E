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

from db4e.recs.ops.TUILogLine import TUILogLine
from db4e.db.DeplDb import DeplDb

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
from db4e.constants.DMongo import DMongo


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

    def __init__(self, bs_mgr: BootstrapMgr, depl_db: DeplDb):
        self.bs_mgr = bs_mgr
        self.depl_db = depl_db

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
        self.depl_db.insert_one(monerod)

        log_rec = TUILogLine(
            elem_type=DElem.MONEROD,
            instance=monerod.instance(),
            op=DField.NEW,
            status=DStatus.COMPLETE,
            msg="New deployment",
        )
        self.depl_db.insert_one(log_rec)

    def add_remote_monerod_deployment(self, monerod: MoneroDRemote):
        self.depl_db.insert_one(monerod)
        log_rec = TUILogLine(
            elem_type=DElem.MONEROD,
            instance=monerod.instance(),
            op=DField.NEW,
            status=DStatus.COMPLETE,
            msg="New deployment",
        )
        self.depl_db.insert_one(log_rec)

    def add_p2pool_deployment(self, p2pool: P2Pool):
        # Generate the configuration
        if p2pool.parent() != DField.DISABLE:
            vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
            tmpl_file = self.get_template(DElem.P2POOL)
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
        self.depl_db.insert_one(p2pool)
        # Generate the logrotate configuration file
        logrotate_tmpl = self.bs_mgr.get_logrotate_template(DElem.P2POOL)
        db4e = self.get_deployment(DElem.DB4E, DElem.DB4E)
        db4e_group = db4e.group()
        p2pool.gen_logrotate_config(
            tmpl_file=logrotate_tmpl, vendor_dir=vendor_dir, db4e_group=db4e_group
        )
        # Create a console log message
        log_rec = TUILogLine(
            elem_type=DElem.P2POOL,
            instance=p2pool.instance(),
            op=DField.NEW,
            status=DStatus.COMPLETE,
            msg="New deployment",
        )
        self.depl_db.insert_one(log_rec)

    def add_remote_p2pool_deployment(self, p2pool: P2PoolRemote) -> P2PoolRemote:
        self.depl_db.insert_one(p2pool)
        # Create a console log message
        log_rec = TUILogLine(
            elem_type=DElem.P2POOL_REMOTE,
            instance=p2pool.instance(),
            op=DField.NEW,
            status=DStatus.COMPLETE,
            msg="New deployment",
        )
        self.depl_db.insert_one(log_rec)
        return p2pool

    def add_xmrig_deployment(self, xmrig: XMRig) -> XMRig:
        # Generate the XMRig configuration
        if xmrig.parent() != DField.DISABLE:
            xmrig.p2pool = self.get_deployment_by_id(
                elem_type=DElem.P2POOL, id=xmrig.parent()
            )
            vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
            # Generate the configuration
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
        db4e = self.get_deployment(DElem.DB4E, DElem.DB4E)
        db4e_group = db4e.group()
        xmrig.gen_logrotate_config(
            tmpl_file=logrotate_tmpl, vendor_dir=vendor_dir, db4e_group=db4e_group
        )
        # Add the new record
        self.depl_db.insert_one(xmrig)
        # Create a console log message
        log_rec = TUILogLine(
            elem_type=DElem.XMRIG,
            instance=xmrig.instance(),
            op=DField.NEW,
            status=DStatus.COMPLETE,
            msg="New deployment",
        )
        self.depl_db.insert_one(log_rec)

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
        for local_xmrig in self.get_xmrigs():
            if local_xmrig.instance() == xmrig.instance():
                return

        # Don't create a remote XMRig deployment record if one already exists.
        for remote_xmrig in self.get_remote_xmrigs():
            if remote_xmrig.instance() == xmrig.instance():
                return

        self.depl_db.insert_one(xmrig)
        log_rec = TUILogLine(
            elem_type=DElem.XMRIG_REMOTE,
            instance=xmrig.instance(),
            op=DField.NEW,
            status=DStatus.COMPLETE,
            msg="New deployment",
        )
        self.depl_db.insert_one(log_rec)
        return xmrig

    def create_vendor_dir(self, new_dir: str, db4e: Db4E):
        update_flag = True
        if os.path.exists(new_dir):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
            backup_vendor_dir = new_dir + "." + timestamp
            try:
                os.rename(new_dir, backup_vendor_dir)
                db4e.msg(
                    DLabel.VENDOR_DIR,
                    DStatus.WARN,
                    f"Found existing directory ({new_dir}), backed it "
                    f"up as ({backup_vendor_dir})",
                )
            except (PermissionError, OSError) as e:
                update_flag = False
                db4e.msg(
                    DLabel.VENDOR_DIR,
                    DStatus.ERROR,
                    f"Unable to backup ({new_dir}) as ({backup_vendor_dir}), "
                    f"aborting deployment directory update:\n{e}",
                )
                return db4e, update_flag
        try:
            os.makedirs(new_dir)
            db4e.msg(
                DLabel.VENDOR_DIR,
                DStatus.GOOD,
                f"Created new {DLabel.VENDOR_DIR}: {new_dir}",
            )
        except (PermissionError, OSError) as e:
            db4e.msg(
                DLabel.VENDOR_DIR,
                DStatus.ERROR,
                f"Unable to create new {DLabel.VENDOR_DIR}: {new_dir}, "
                f"aborting deployment directory update:\n{e}",
            )
            update_flag = False
        return db4e, update_flag

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
        self.depl_db.delete_one(elem)

    def get_component_value(self, data, field_name):
        """
        Generic helper to get any component value by field name.

        Args:
            data (dict): Dictionary containing components with field/value pairs
            field_name (str): The field name to search for

        Returns:
            any or None: The component value, or None if not found
        """
        if not isinstance(data, dict) or "components" not in data:
            return None
        components = data.get(DField.COMPONENTS, [])
        for component in components:
            if (
                isinstance(component, dict)
                and component.get(DField.FIELD) == field_name
            ):
                return component.get(DField.VALUE)
        return None

    def get_deployment(self, elem_type, instance):
        rec = self.depl_db.find_one(elem_type, instance)
        if rec:
            obj = self.factory(rec)
            if type(obj) == P2Pool or type(obj) == P2PoolInternal:
                if obj.parent() != DField.DISABLE:
                    obj.monerod = self.get_deployment_by_id(
                        elem_type=DElem.MONEROD, id=obj.parent()
                    )
                    if not obj.monerod:
                        obj.monerod = self.get_deployment_by_id(
                            elem_type=DElem.MONEROD_REMOTE, id=obj.parent()
                        )
            elif type(obj) == XMRig:
                if obj.parent() != DField.DISABLE:
                    obj.p2pool = self.get_deployment_by_id(
                        elem_type=DElem.P2POOL, id=obj.parent()
                    )
                    if not obj.p2pool:
                        obj.p2pool = self.get_deployment_by_id(
                            elem_type=DElem.P2POOL_REMOTE, id=obj.parent()
                        )
                    if (
                        type(obj.p2pool) == P2Pool
                        and obj.p2pool.parent() != DField.DISABLE
                    ):
                        obj.p2pool.monerod = self.get_deployment_by_id(
                            elem_type=DElem.MONEROD, id=obj.p2pool.parent()
                        )
                        if not obj.p2pool.monerod:
                            obj.p2pool.monerod = self.get_deployment_by_id(
                                elem_type=DElem.MONEROD_REMOTE, id=obj.p2pool.parent()
                            )

                obj.instance_map = self.get_deployment_ids_and_instances(
                    elem_type=DElem.P2POOL
                )
            return obj
        else:
            return None

    def get_deployment_by_id(self, elem_type, id):
        if id == DField.DISABLE:
            return None
        else:
            rec = self.depl_db.find_one_by_id(elem_type=elem_type, id=id)
            return self.factory(rec)

    def get_deployment_ids_and_instances(self, elem_type):
        instance_map = {}
        recs = self.depl_db.find_many(elem_type=elem_type)
        for rec in recs:
            instance = self.get_component_value(rec, DField.INSTANCE)
            instance_map[instance] = rec[DMongo.OBJECT_ID]
        return instance_map

    def get_deployments(self):
        recs = self.depl_db.find_many(elem_type=DField.ALL_DEPLOYMENTS)
        obj_list = []
        for rec in recs:
            obj = self.factory(rec)
            if type(obj) == P2Pool or type(obj) == P2PoolInternal:
                if obj.parent() != DField.DISABLE:
                    obj.monerod = self.get_deployment_by_id(
                        elem_type=DElem.MONEROD, id=obj.parent()
                    )
                    if not obj.monerod:
                        obj.monerod = self.get_deployment_by_id(
                            elem_type=DElem.MONEROD_REMOTE, id=obj.parent()
                        )
            elif type(obj) == XMRig:
                if obj.p2pool:
                    if obj.parent() != DField.DISABLE:
                        obj.p2pool = self.get_deployment_by_id(
                            elem_type=DElem.P2POOL, id=obj.parent()
                        )
                        if not obj.p2pool:
                            obj.p2pool = self.get_deployment_by_id(
                                elem_type=DElem.P2POOL_REMOTE, id=obj.parent()
                            )
                        if (
                            type(obj.p2pool) == P2Pool
                            and obj.p2pool.parent() != DField.DISABLE
                        ):
                            obj.p2pool.monerod = self.get_deployment_by_id(
                                elem_type=DElem.MONEROD, id=obj.p2pool.parent()
                            )
                            if not obj.p2pool.monerod:
                                obj.p2pool.monerod = self.get_deployment_by_id(
                                    elem_type=DElem.MONEROD_REMOTE,
                                    id=obj.p2pool.parent(),
                                )
            obj_list.append(obj)
        return obj_list

    def get_downstream(self, elem):
        elem_type = elem.elem_type()
        obj_id = elem.id()
        obj_list = []
        # P2Pool is downstream from MoneroD and MoneroDRemote
        if elem_type == DElem.MONEROD or elem_type == DElem.MONEROD_REMOTE:
            p2pools = self.get_p2pools()
            for p2pool in p2pools:
                if p2pool.parent() == obj_id:
                    obj_list.append(p2pool)
        # XMRig is downstream from P2Pool and P2PoolRemote
        elif elem_type == DElem.P2POOL or elem_type == DElem.P2POOL_REMOTE:
            xmrigs = self.get_xmrigs()
            for xmrig in xmrigs:
                if xmrig.parent() == obj_id:
                    obj_list.append(xmrig)
        return obj_list

    def get_internal_p2pools(self):
        recs = self.depl_db.find_many(elem_type=DElem.INT_P2POOL)
        obj_list = []
        for rec in recs:
            obj = self.factory(rec)
            if obj.parent() != DField.DISABLE:
                obj.monerod = self.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=obj.parent()
                )
            obj_list.append(obj)
        return obj_list

    def get_monerods(self):
        obj_list = []
        recs = self.depl_db.find_many(elem_type=DElem.MONEROD)
        for rec in recs:
            obj_list.append(self.factory(rec))
        return obj_list

    def get_new(self, elem_type):

        if elem_type == DElem.MONEROD:
            return MoneroD()
        elif elem_type == DElem.MONEROD_REMOTE:
            return MoneroDRemote()
        elif elem_type == DElem.P2POOL:
            p2pool = P2Pool()
            db4e = self.get_deployment(DElem.DB4E, DElem.DB4E)
            p2pool.user_wallet(db4e.user_wallet())
            return p2pool
        elif elem_type == DElem.P2POOL_REMOTE:
            return P2PoolRemote()
        elif elem_type == DElem.INT_P2POOL:
            p2pool = P2PoolInternal()
            p2pool.user_wallet(DDef.DONATION_WALLET)
        elif elem_type == DElem.XMRIG:
            return XMRig()
        elif elem_type == DElem.XMRIG_REMOTE:
            return XMRigRemote()
        else:
            raise ValueError(f"DeplMgr:get_new(): No handler for {elem_type}")

    def get_p2pools(self):
        obj_list = []
        recs = self.depl_db.find_many(elem_type=DElem.P2POOL)
        for rec in recs:
            obj = self.factory(rec)
            if obj.parent() != DField.DISABLE:
                obj.monerod = self.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=obj.parent()
                )
            obj_list.append(obj)
        return obj_list

    def get_remote_xmrigs(self):
        recs = self.depl_db.find_many(elem_type=DElem.XMRIG_REMOTE)
        obj_list = []
        for rec in recs:
            obj = self.factory(rec)
            obj_list.append(obj)
        return obj_list

    def get_xmrigs(self):
        recs = self.depl_db.find_many(elem_type=DElem.XMRIG)
        obj_list = []
        for rec in recs:
            obj = self.factory(rec)
            if obj.parent() != DField.DISABLE:
                obj.p2pool = self.get_deployment_by_id(
                    elem_type=DElem.P2POOL, id=obj.parent()
                )
                if not obj.p2pool:
                    obj.p2pool = self.get_deployment_by_id(
                        elem_type=DElem.P2POOL_REMOTE, id=obj.parent()
                    )
                if type(obj.p2pool) == P2Pool and obj.p2pool.parent() != DField.DISABLE:
                    obj.p2pool.monerod = self.get_deployment_by_id(
                        elem_type=DElem.MONEROD, id=obj.p2pool.parent()
                    )
                    if not obj.p2pool.monerod:
                        obj.p2pool.monerod = self.get_deployment_by_id(
                            elem_type=DElem.MONEROD_REMOTE, id=obj.p2pool.parent()
                        )
            obj_list.append(obj)
        return obj_list

    def is_initialized(self):
        return self.bs_mgr.is_initialized()

    def update_db4e_deployment(self, new_db4e: Db4E):
        update_flag = False
        # The current record, we'll update this and write it back in
        db4e = self.get_deployment(elem_type=DElem.DB4E, instance=DElem.DB4E)
        # TUI log entry
        log_rec = TUILogLine(
            elem_type=DElem.DB4E,
            instance=DElem.DB4E,
            op=DField.UPDATE,
            status=DStatus.COMPLETE,
        )
        # Updating user wallet
        if db4e.user_wallet != new_db4e.user_wallet:
            db4e.user_wallet(new_db4e.user_wallet())
            self.depl_db.update_one(db4e)
            log_rec.message("Updated user wallet")
            log_rec.details(
                f"{db4e.user_wallet()[:6]}... > {new_db4e.user_wallet()[:6]}..."
            )
            self.depl_db.insert_one(log_rec)
            update_flag = True
        # Updating vendor dir
        if db4e.vendor_dir != new_db4e.vendor_dir:
            if not db4e.vendor_dir():
                db4e, update_flag = self.create_vendor_dir(
                    new_dir=new_db4e.vendor_dir(), db4e=db4e
                )
            else:
                db4e, update_flag = self.update_vendor_dir(
                    new_dir=new_db4e.vendor_dir(), old_dir=db4e.vendor_dir(), db4e=db4e
                )
            log_rec.message("Updated deployment dir")
            log_rec.details(f"{db4e.vendor_dir()} > {new_db4e.vendor_dir()}")
            self.depl_db.insert_one(log_rec)
            db4e.vendor_dir(new_db4e.vendor_dir())
            update_flag = True
        # Updating the primary server
        if db4e.primary_server != new_db4e.primary_server:
            if db4e.primary_server() != DField.DISABLE:
                old_instance = self.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=db4e.primary_server()
                ).instance()
            else:
                old_instance = "None"
            if new_db4e.primary_server() != DField.DISABLE:
                new_instance = self.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=new_db4e.primary_server()
                ).instance()
            else:
                new_instance = "None"
            db4e.primary_server(new_db4e.primary_server())
            log_rec.message("Updated primary server")
            log_rec.details(f"{old_instance} > {new_instance}")
            self.depl_db.insert_one(log_rec)
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
        update, update_config, restart = False, False, False
        # Retrive the current/old deployment
        monerod = self.get_deployment(DElem.MONEROD, new_monerod.instance())
        if not monerod:
            raise ValueError(
                f"DeplMgr:update_monerod_deployment(): "
                f"No monerod found for {new_monerod}"
            )
        # TUI log entry
        log_rec = TUILogLine(
            elem_type=DElem.MONEROD,
            instance=monerod.instance(),
            op=DField.UPDATE,
            status=DStatus.COMPLETE,
        )
        # This is an enable/disable operation
        if monerod.enabled() != new_monerod.enabled():
            if monerod.enabled():
                monerod.enabled(False)
            else:
                monerod.enabled(True)
            log_rec.message("Updated enabled status")
            log_rec.details(f"{monerod.enabled()} > {new_monerod.enabled()}")
            self.depl_db.insert_one(log_rec)
            update, update_config = True, True
        # In Peers
        if monerod.in_peers != new_monerod.in_peers:
            log_rec.message("Updated incoming max peers")
            log_rec.details(f"{monerod.in_peers()} > {new_monerod.in_peers()}")
            self.depl_db.insert_one(log_rec)
            monerod.in_peers(new_monerod.in_peers())
            update, update_config = True, True
        # Out Peers
        if monerod.out_peers != new_monerod.out_peers:
            log_rec.message("Updated outbound max peers")
            log_rec.details(f"{monerod.out_peers()} > {new_monerod.out_peers()}")
            self.depl_db.insert_one(log_rec)
            monerod.out_peers(new_monerod.out_peers())
            update, update_config = True, True
        # P2P Bind Port
        if monerod.p2p_bind_port != new_monerod.p2p_bind_port:
            log_rec.message("Updated P2P bind port")
            log_rec.details(
                f"{monerod.p2p_bind_port()} > {new_monerod.p2p_bind_port()}"
            )
            self.depl_db.insert_one(log_rec)
            monerod.p2p_bind_port(new_monerod.p2p_bind_port())
            update, update_config = True, True
        # RPC Bind Port
        if monerod.rpc_bind_port != new_monerod.rpc_bind_port:
            log_rec.message("Updated RPC bind port")
            log_rec.details(
                f"{monerod.rpc_bind_port()} > {new_monerod.rpc_bind_port()}"
            )
            self.depl_db.insert_one(log_rec)
            monerod.rpc_bind_port(new_monerod.rpc_bind_port())
            update, update_config = True, True

        # ZMQ Pub Port
        if monerod.zmq_pub_port != new_monerod.zmq_pub_port:
            log_rec.message("Updated ZMQ pub port")
            log_rec.details(f"{monerod.zmq_pub_port()} > {new_monerod.zmq_pub_port()}")
            self.depl_db.insert_one(log_rec)
            monerod.zmq_pub_port(new_monerod.zmq_pub_port())
            update, update_config = True, True
        # ZMQ RPC Port
        if monerod.zmq_rpc_port != new_monerod.zmq_rpc_port:
            log_rec.message("Updated ZMQ RPC port")
            log_rec.details(f"{monerod.zmq_rpc_port()} > {new_monerod.zmq_rpc_port()}")
            self.depl_db.insert_one(log_rec)
            monerod.zmq_rpc_port(new_monerod.zmq_rpc_port())
            update, update_config = True, True
        # Log Level
        if monerod.log_level != new_monerod.log_level:
            log_rec.message("Updated log level")
            log_rec.details(f"{monerod.log_level()} > {new_monerod.log_level()}")
            self.depl_db.insert_one(log_rec)
            monerod.log_level(new_monerod.log_level())
            update, update_config = True, True
        # Max Log Files
        if monerod.max_log_files != new_monerod.max_log_files:
            log_rec.message("Updated max log files")
            log_rec.details(
                f"{monerod.max_log_files()} > {new_monerod.max_log_files()}"
            )
            self.depl_db.insert_one(log_rec)
            monerod.max_log_files(new_monerod.max_log_files())
            update, update_config = True, True
        # Max Log Size
        if monerod.max_log_size != new_monerod.max_log_size:
            log_rec.message("Updated max log size")
            log_rec.details(f"{monerod.max_log_size()} > {new_monerod.max_log_size()}")
            self.depl_db.insert_one(log_rec)
            monerod.max_log_size(new_monerod.max_log_size())
            update, update_config = True, True
        # Priority Node 1 hostname
        if monerod.priority_node_1 != new_monerod.priority_node_1:
            log_rec.message("Updated priority node 1")
            log_rec.details(
                f"{monerod.priority_node_1()} > {new_monerod.priority_node_1()}"
            )
            self.depl_db.insert_one(log_rec)
            monerod.priority_node_1(new_monerod.priority_node_1())
            update, update_config = True, True
        # Priority Port 1
        if monerod.priority_port_1 != new_monerod.priority_port_1:
            log_rec.message("Updated priority port 1")
            log_rec.details(
                f"{monerod.priority_port_1()} > {new_monerod.priority_port_1()}"
            )
            self.depl_db.insert_one(log_rec)
            monerod.priority_port_1(new_monerod.priority_port_1())
            update, update_config = True, True
        # Priority Node 2 hostname
        if monerod.priority_node_2 != new_monerod.priority_node_2:
            log_rec.message("Updated priority node 2")
            log_rec.details(
                f"{monerod.priority_node_2()} > {new_monerod.priority_node_2()}"
            )
            self.depl_db.insert_one(log_rec)
            monerod.priority_node_2(new_monerod.priority_node_2())
            update, update_config = True, True
        # Priority Port 2
        if monerod.priority_port_2 != new_monerod.priority_port_2:
            log_rec.message("Updated priority port 2")
            log_rec.details(
                f"{monerod.priority_port_2()} > {new_monerod.priority_port_2()}"
            )
            self.depl_db.insert_one(log_rec)
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
        # TUI log entry
        log_rec = TUILogLine(
            elem_type=DElem.MONEROD_REMOTE,
            instance=monerod.instance(),
            op=DField.UPDATE,
            status=DStatus.COMPLETE,
        )
        ## Field-by-field comparison
        # IP Address
        if monerod.ip_addr != new_monerod.ip_addr:
            log_rec.message("Updated IP/hostname")
            log_rec.details(f"{monerod.ip_addr()} > {new_monerod.ip_addr()}")
            self.depl_db.insert_one(log_rec)
            monerod.ip_addr(new_monerod.ip_addr())
            update = True
        # RPC Bind Port
        if monerod.rpc_bind_port != new_monerod.rpc_bind_port:
            log_rec.message("Updated RPC bind port")
            log_rec.details(
                f"{monerod.rpc_bind_port()} > {new_monerod.rpc_bind_port()}"
            )
            self.depl_db.insert_one(log_rec)
            monerod.rpc_bind_port(new_monerod.rpc_bind_port())
            update = True
        # ZMQ Pub Port
        if monerod.zmq_pub_port != new_monerod.zmq_pub_port:
            log_rec.message("Updated ZMQ pub port")
            log_rec.details(f"{monerod.zmq_pub_port()} > {new_monerod.zmq_pub_port()}")
            self.depl_db.insert_one(log_rec)
            monerod.zmq_pub_port(new_monerod.zmq_pub_port())
            update = True
        # Update the database
        if update:
            monerod = self.depl_db.update_one(monerod)

    def update_p2pool_deployment(self, new_p2pool):
        # Flags indicating what needs to be done at the end of the function
        update, update_config, restart = False, False, False
        # Resolve which P2Pool type we're updating
        if new_p2pool.elem_type() == DElem.P2POOL:
            p2pool = self.get_deployment(DElem.P2POOL, new_p2pool.instance())
        else:
            p2pool = self.get_deployment(DElem.INT_P2POOL, new_p2pool.instance())
        # This shouldn't happen, but let's trap it in case it does.
        if not p2pool:
            raise ValueError(
                f"DeplMgr:update_p2pool_deployment(): "
                f"No p2pool found for {new_p2pool.id()}"
            )
        # Base TUI log entry
        log_rec = TUILogLine(
            elem_type=new_p2pool.elem_type(),
            instance=p2pool.instance(),
            op=DField.UPDATE,
            status=DStatus.COMPLETE,
        )
        ## Field-by-field comparison
        # Enable/disable
        if p2pool.enabled() != new_p2pool.enabled():
            if new_p2pool.enabled():
                log_rec.message("Enabled P2Pool")
            else:
                log_rec.message("Disabled P2Pool")
            log_rec.details(f"{p2pool.enabled()} > {new_p2pool.enabled()}")
            self.depl_db.insert_one(log_rec)
            p2pool.enabled(new_p2pool.enabled())
            update = True
        # In Peers
        if p2pool.in_peers != new_p2pool.in_peers:
            log_rec.message("Updated max incoming peers")
            log_rec.details(f"{p2pool.in_peers()} > {new_p2pool.in_peers()}")
            self.depl_db.insert_one(log_rec)
            p2pool.in_peers(new_p2pool.in_peers())
            update_config, update, restart = True, True, True
        # Out Peers
        if p2pool.out_peers != new_p2pool.out_peers:
            log_rec.message("Updated max outbound peers")
            log_rec.details(f"{p2pool.out_peers()} > {new_p2pool.out_peers()}")
            self.depl_db.insert_one(log_rec)
            p2pool.out_peers(new_p2pool.out_peers())
            update_config, update, restart = True, True, True
        # P2P Bind Port
        if p2pool.p2p_port != new_p2pool.p2p_port:
            log_rec.message("Updated P2P port")
            log_rec.details(f"{p2pool.p2p_port()} > {new_p2pool.p2p_port()}")
            self.depl_db.insert_one(log_rec)
            p2pool.p2p_port(new_p2pool.p2p_port())
            update_config, update, restart = True, True, True
        # Stratum port
        if p2pool.stratum_port != new_p2pool.stratum_port:
            log_rec.message("Updated stratum port")
            log_rec.details(f"{p2pool.stratum_port()} > {new_p2pool.stratum_port()}")
            self.depl_db.insert_one(log_rec)
            p2pool.stratum_port(new_p2pool.stratum_port())
            update_config, update, restart = True, True, True
        # Log level
        if p2pool.log_level != new_p2pool.log_level:
            log_rec.message("Updated log level")
            log_rec.details(f"{p2pool.log_level()} > {new_p2pool.log_level()}")
            self.depl_db.insert_one(log_rec)
            p2pool.log_level(new_p2pool.log_level())
            update_config, update, restart = True, True, True
        # Upstream Monerod
        if p2pool.parent != new_p2pool.parent:
            if new_p2pool.parent() == DField.DISABLE:
                log_rec.message("Unset upstream MoneroD")
                old_monerod = self.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=p2pool.parent()
                )
                if not old_monerod:
                    old_monerod = self.get_deployment_by_id(
                        elem_type=DElem.MONEROD_REMOTE, id=p2pool.parent()
                    )
                old_instance = old_monerod.instance()
                log_rec.details(f"{old_instance} > DISABLE")
                self.depl_db.insert_one(log_rec)
                p2pool.parent(DField.DISABLE)
                update = True
            elif p2pool.parent() == DField.DISABLE:
                log_rec.message("Set upstream MoneroD")
                new_monerod = self.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=new_p2pool.parent()
                )
                if not new_monerod:
                    new_monerod = self.get_deployment_by_id(
                        elem_type=DElem.MONEROD_REMOTE, id=new_p2pool.parent()
                    )
                new_instance = new_monerod.instance()
                log_rec.details(f"DISABLE > {new_instance}")
                self.depl_db.insert_one(log_rec)
                p2pool.parent(new_p2pool.parent())
                update, update_config = True, True
            else:
                log_rec.message("Updated upstream MoneroD")
                old_monerod = self.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=p2pool.parent()
                )
                if not old_monerod:
                    old_monerod = self.get_deployment_by_id(
                        elem_type=DElem.MONEROD_REMOTE, id=p2pool.parent()
                    )
                old_instance = old_monerod.instance()
                new_monerod = self.get_deployment_by_id(
                    elem_type=DElem.MONEROD, id=new_p2pool.parent()
                )
                if not new_monerod:
                    new_monerod = self.get_deployment_by_id(
                        elem_type=DElem.MONEROD_REMOTE, id=new_p2pool.parent()
                    )
                new_instance = new_monerod.instance()
                log_rec.details(f"{old_instance} > {new_instance}")
                self.depl_db.insert_one(log_rec)
                p2pool.parent(new_p2pool.parent())
                p2pool.monerod = new_monerod
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
        if not p2pool:
            raise ValueError(
                f"DeplMgr:update_p2pool_remote_deployment(): "
                f"Nothing found for {new_p2pool.id()}"
            )
        ## Field-by-field comparison
        # IP Address
        if p2pool.ip_addr != new_p2pool.ip_addr:
            msg = f"Updated IP/hostname: {p2pool.ip_addr()} > {new_p2pool.ip_addr()}"
            p2pool.ip_addr(new_p2pool.ip_addr())
            p2pool.msg(DLabel.P2POOL, DStatus.GOOD, msg)
            update = True
        # Stratum Port
        if p2pool.stratum_port != new_p2pool.stratum_port:
            msg = (
                f"Updated stratum port: {p2pool.stratum_port()} > "
                f"{new_p2pool.stratum_port()}"
            )
            p2pool.stratum_port(new_p2pool.stratum_port())
            p2pool.msg(DLabel.P2POOL, DStatus.GOOD, msg)
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
            log_rec = TUILogLine(
                elem_type=DLabel.VENDOR_DIR,
                instance=DElem.DB4E,
                op=DField.UPDATE,
                status=DStatus.COMPLETE,
            )
            try:
                os.rename(new_dir, backup_vendor_dir)
                log_rec.message(f"Found existing directory {new_dir}")
                log_rec.details(f"Backed up as {backup_vendor_dir}")
                self.depl_db.insert_one(log_rec)
            except (PermissionError, OSError) as e:
                update_flag = False
                log_rec.message(
                    f"Unable to backup ({new_dir}) as ({backup_vendor_dir})"
                )
                log_rec.details(f"{e}")
                self.depl_db.insert_one(log_rec)

        # No need to move if old_dir is empty (first-time initialization)
        if not old_dir:
            log_rec = TUILogLine(
                elem_type=DLabel.VENDOR_DIR,
                instance=DElem.DB4E,
                op=DField.UPDATE,
                status=DStatus.COMPLETE,
                message=f"New deployment directory",
                details=f"{new_dir}",
            )
            self.depl_db.insert_one(log_rec)
            db4e.vendor_dir(new_dir)
            ## Do we need to actually create the directory here?
            return db4e, update_flag

        # Move the vendor_dir to the new location
        log_rec = TUILogLine(
            elem_type=DLabel.VENDOR_DIR,
            instance=DElem.DB4E,
            op=DField.UPDATE,
            status=DStatus.COMPLETE,
        )
        try:
            os.rename(old_dir, new_dir)
            log_rec.message(f"Moved vendor dir")
            log_rec.details(f"{old_dir} > {new_dir}")
        except (PermissionError, OSError) as e:
            log_rec.message(f"Move error")
            log_rec.details(f"{e}")
            update_flag = False
        return db4e, update_flag

    def update_xmrig_deployment(self, new_xmrig: XMRig) -> XMRig:
        update = False
        update_config = False

        xmrig = self.get_deployment(DElem.XMRIG, new_xmrig.instance())
        log_rec = TUILogLine(
            elem_type=DElem.XMRIG,
            instance=new_xmrig.instance(),
            op=DField.UPDATE,
            status=DStatus.COMPLETE,
        )
        if not xmrig:
            raise ValueError(
                f"DeplMgr:update_xmrig_deployment(): "
                f"Nothing found for {new_xmrig.id()}"
            )

        if xmrig.enabled() != new_xmrig.enabled():
            # This is an enable/disable operation
            if xmrig.enabled():
                if xmrig.enabled():
                    log_rec.message("Disabled XMRig")
                else:
                    log_rec.message("Enabled XMRig")
                xmrig.enabled(False)
            else:
                xmrig.enabled(True)
            update = True

        ## Field-by-field comparison

        # Num Threads
        if xmrig.num_threads != new_xmrig.num_threads:
            log_rec.message(f"Updated number of threads")
            log_rec.details(f"{xmrig.num_threads()} > {new_xmrig.num_threads()}")
            self.depl_db.insert_one(log_rec)
            xmrig.num_threads(new_xmrig.num_threads())
            update, update_config = True, True
        # Parent ID
        if xmrig.parent != new_xmrig.parent:

            # New XMRig's upstream P2Pool is unset
            if new_xmrig.parent() == DField.DISABLE:
                new_parent_instance = "Not set"
                xmrig.parent(DField.DISABLE)
                update_config = False
            # New XMRig has a valid upstream P2Pool instance
            else:
                xmrig.p2pool = self.get_deployment_by_id(
                    elem_type=DElem.P2POOL, id=new_xmrig.parent()
                )
                if not xmrig.p2pool:
                    xmrig.p2pool = self.get_deployment_by_id(
                        elem_type=DElem.P2POOL_REMOTE, id=new_xmrig.parent()
                    )
                new_parent_instance = xmrig.p2pool.instance()
                xmrig.parent(new_xmrig.parent())
                update_config = True

            # Current/old XMRig's upstream P2Pool is unset
            if xmrig.parent() == DField.DISABLE:
                parent_instance = "Not set"
            # Current/old XMRig's upstream P2Pool instance is valid
            else:
                parent = self.get_deployment_by_id(xmrig.parent())
                parent_instance = parent.instance()

            log_rec.message(f"Updated upstream P2Pool")
            log_rec.details(f"{parent_instance} > {new_parent_instance}")
            self.depl_db.insert_one(log_rec)
            update = True

        # Regenerate config if required
        if update_config:
            vendor_dir = self.bs_mgr.get_dir(DDir.VENDOR)
            tmpl_file = self.bs_mgr.get_template(DElem.XMRIG)
            xmrig.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)

        if update:
            xmrig.version(DDef.XMRIG_VERSION)
            self.depl_db.update_one(xmrig)
