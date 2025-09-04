"""
db4e/Modules/DeploymentManager.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import os
from datetime import datetime, timezone
import socket

from textual.containers import Container

from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.DbCache import DbCache
from db4e.Modules.JobQueue import JobQueue
from db4e.Modules.Job import Job
from db4e.Modules.Db4E import Db4E
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig

from db4e.Constants.Labels import (
    MONEROD_LABEL, P2POOL_LABEL, MONEROD_SHORT_LABEL, DB4E_LABEL,
    USER_WALLET_LABEL, VENDOR_DIR_LABEL, XMRIG_SHORT_LABEL, P2POOL_SHORT_LABEL)
from db4e.Constants.Fields import (
    PYTHON_FIELD, DB4E_FIELD, ERROR_FIELD, ELEMENT_TYPE_FIELD,
    TEMPLATE_FIELD, GOOD_FIELD, INSTALL_DIR_FIELD, NEW_FIELD,
    MONEROD_FIELD, MONEROD_REMOTE_FIELD, ELEMENT_FIELD,
    P2POOL_FIELD, P2POOL_REMOTE_FIELD, VENDOR_DIR_FIELD, WARN_FIELD, XMRIG_FIELD,
    DEPLOYMENT_MGR_FIELD, COMPONENTS_FIELD, FIELD_FIELD, VALUE_FIELD, INSTANCE_FIELD)
from db4e.Constants.Defaults import (
    BIN_DIR_DEFAULT, PYTHON_DEFAULT, TEMPLATES_DIR_DEFAULT,
    CONF_DIR_DEFAULT, API_DIR_DEFAULT, LOG_DIR_DEFAULT, RUN_DIR_DEFAULT, 
    BLOCKCHAIN_DIR_DEFAULT, XMRIG_VERSION_DEFAULT, MONEROD_VERSION_DEFAULT,
    P2POOL_VERSION_DEFAULT, MONEROD_CONFIG_DEFAULT, P2POOL_CONFIG_DEFAULT,
    XMRIG_CONFIG_DEFAULT)
from db4e.Constants.Jobs import RESTART_FIELD, OP_FIELD, UPDATE_FIELD


class DeploymentMgr(Container):
    

    def __init__(self):
        super().__init__()
        db = DbMgr()
        self.db_cache = DbCache(db=db)
        self.job_queue = JobQueue(db=db)
        self.db4e_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


    def add_deployment(self, elem):
        #print(f"DeploymentMgr:add_deployment(): {rec}")
        elem_class = type(elem)

        # Add the Db4E Core deployment
        if elem_class == Db4E:
            return self.insert_one(elem.to_rec())

        # Add a remote Monero daemon deployment
        elif elem_class == MoneroD:
            return self.add_monerod_deployment(elem)
            
        # Add a remote Monero daemon deployment
        elif elem_class == MoneroDRemote:
            return self.add_remote_monerod_deployment(elem)

        # A P2Pool deployment
        elif elem_class == P2Pool:
            return self.add_p2pool_deployment(elem)

        # Add a remote P2Pool deployment
        elif elem_class == P2PoolRemote:
            return self.add_remote_p2pool_deployment(elem)
            
        # Add a XMRig deployment
        elif elem_class == XMRig:
            return self.add_xmrig_deployment(elem)

        # Catchall
        else:
            raise ValueError(f"DeploymentMgr:add_deployment(): No handler for {elem_class}")


    def add_monerod_deployment(self, monerod: MoneroD) -> MoneroD:
        for aMonerod in self.get_monerods():
            if aMonerod.instance() == monerod.instance():
                msg = f"A deployment with the same name ({monerod.instance()}) already exists"
                monerod.add_msg(MONEROD_LABEL, WARN_FIELD, msg)
                return monerod

        update = True

        if not monerod.instance():
            update = False

        if not monerod.in_peers():
            update = False

        if not monerod.out_peers():
            update = False

        if not monerod.p2p_bind_port():
            update = False

        if not monerod.rpc_bind_port():
            update = False

        if not monerod.zmq_pub_port():
            update = False

        if not monerod.zmq_rpc_port():
            update = False

        if not monerod.log_level():
            update = False

        if not monerod.max_log_files():
            update = False

        if not monerod.max_log_size():
            update = False

        if not monerod.priority_node_1():
            update = False

        if not monerod.priority_port_1():
            update = False

        if not monerod.priority_node_2():
            update = False

        if not monerod.priority_port_2():
            update = False

        if update:
            monerod.ip_addr(socket.gethostname())
            vendor_dir = self.get_dir(VENDOR_DIR_FIELD)
            monerod_dir = self.get_dir(MONEROD_FIELD)
            tmpl_file = self.get_template(MONEROD_FIELD)
            monerod.data_dir(os.path.join(vendor_dir, BLOCKCHAIN_DIR_DEFAULT))
            monerod.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)
            monerod.log_file(
                os.path.join(vendor_dir, monerod_dir, monerod.instance(), 
                             LOG_DIR_DEFAULT, 'monerod.log'))
            self.insert_one(monerod)
            os.makedirs(os.path.join(vendor_dir, monerod_dir, monerod.instance(), 
                                   LOG_DIR_DEFAULT))
            os.makedirs(os.path.join(vendor_dir, monerod_dir, monerod.instance(), 
                                   RUN_DIR_DEFAULT))
            job = Job(op=NEW_FIELD, elem_type=MONEROD_FIELD, instance=monerod.instance())
            job.msg("Created new MoneroD deployment")
            self.job_queue.post_completed_job(job)
        
        return monerod


    def add_remote_monerod_deployment(self, monerod: MoneroDRemote):
        
        for aMonerod in self.get_monerods():
            if aMonerod.instance() == monerod.instance():
                msg = f"A deployment with the same name ({monerod.instance()}) already exists"
                monerod.add_msg(MONEROD_LABEL, WARN_FIELD, msg)
                return monerod
            
        update = True

        # Check that the user actually filled out the form
        if not monerod.instance():
            update = False

        if not monerod.ip_addr():
            update = False

        #elif not is_valid_ip_or_hostname(ip_addr):
        #    update = False

        if not monerod.rpc_bind_port():
            update = False

        if not monerod.zmq_pub_port():
            update = False

        if update:
            self.insert_one(monerod)
            job = Job(op=NEW_FIELD, elem_type=MONEROD_FIELD, instance=monerod.instance())
            job.msg("Created new remote MoneroD deployment")
            self.job_queue.post_completed_job(job)
        return monerod
    

    def add_p2pool_deployment(self, p2pool: P2Pool) -> P2Pool:
        for aP2Pool in self.get_p2pools():
            if aP2Pool.instance() == p2pool.instance():
                msg = f"A deployment with the same name ({p2pool.instance()}) already exists"
                p2pool.add_msg(P2POOL_LABEL, WARN_FIELD, msg)
                return p2pool

        update = True

        # Check that the user actually filled out the form
        if not p2pool.instance():
            update = False

        if not p2pool.in_peers():
            update = False

        if not p2pool.out_peers():
            update = False
    
        if not p2pool.p2p_bind_port():
            update = False

        if not p2pool.stratum_port():
            update = False

        if not p2pool.log_level():
            update = False

        if not p2pool.parent():
            update = False
        else:
            p2pool.monerod = self.get_deployment_by_id(p2pool.parent())

        if update:
            p2pool.ip_addr(socket.gethostname())
            vendor_dir = self.get_dir(VENDOR_DIR_FIELD)
            p2pool_dir = self.get_dir(P2POOL_FIELD)
            tmpl_file = self.get_template(P2POOL_FIELD)
            p2pool.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)
            p2pool.log_file(
                os.path.join(
                    vendor_dir, p2pool_dir, p2pool.instance(), 
                    LOG_DIR_DEFAULT, 'p2pool.log'))
            self.insert_one(p2pool)
            os.makedirs(os.path.join(vendor_dir, p2pool_dir, p2pool.instance(), 
                                     LOG_DIR_DEFAULT), exist_ok=True)
            os.makedirs(os.path.join(vendor_dir, p2pool_dir, p2pool.instance(), 
                                     RUN_DIR_DEFAULT), exist_ok=True)
            os.makedirs(os.path.join(vendor_dir, p2pool_dir, p2pool.instance(), 
                                     API_DIR_DEFAULT), exist_ok=True)
            job = Job(op=NEW_FIELD, elem_type=P2POOL_FIELD, instance=p2pool.instance())
            job.msg("Created new P2Pool deployment")
            self.job_queue.post_completed_job(job)
        return p2pool


    def add_remote_p2pool_deployment(self, p2pool: P2PoolRemote) -> P2PoolRemote:
        for aP2Pool in self.get_p2pools():
            if aP2Pool.instance() == p2pool.instance():
                msg = f"A deployment with the same name ({p2pool.instance()}) already exists"
                p2pool.add_msg(P2POOL_LABEL, WARN_FIELD, msg)
                return p2pool

        update = True

        # Check that the user actually filled out the form
        if not p2pool.instance():
            update = False

        if not p2pool.ip_addr():
            update = False

        #elif not is_valid_ip_or_hostname(p2pool.ip_addr.value):
        #    update = False

        if not p2pool.stratum_port():
            update = False

        print(f"DeploymentMgr:add_remote_p2pool_deployment(): {p2pool.to_rec()}")

        if update:
            self.insert_one(p2pool)
            job = Job(op=NEW_FIELD, elem_type=P2POOL_REMOTE_FIELD, instance=p2pool.instance())
            job.msg("Created new remote P2Pool deployment")
            self.job_queue.post_completed_job(job)
        return p2pool


    def add_xmrig_deployment(self, xmrig: XMRig) -> XMRig:
        for aXMRig in self.get_p2pools():
            if aXMRig.instance() == xmrig.instance():
                msg = f"A deployment with the same name ({xmrig.instance()}) already exists"
                xmrig.add_msg(P2POOL_LABEL, WARN_FIELD, msg)
                return xmrig
            
        update = True
    
        # Check that the user filled out the form
        if not xmrig.instance():
            update = False

        if not xmrig.num_threads():
            update = False

        if not xmrig.parent():
            update = False
        else:
            xmrig.p2pool = self.db_cache.get_deployment_by_id(xmrig.parent())
        
        print(f"DeploymentMgr:add_xmrig_deployment(): xmrig.parent: {xmrig.parent()}")
        print(f"DeploymentMgr:add_xmrig_deployment(): xmrig.p2pool: {xmrig.p2pool}")
            
        if update:
            vendor_dir = self.get_dir(VENDOR_DIR_FIELD)
            tmpl_file = self.get_template(XMRIG_FIELD)
            xmrig_dir = self.get_dir(XMRIG_FIELD)
            xmrig.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)
            xmrig.log_file(os.path.join(vendor_dir, xmrig_dir, LOG_DIR_DEFAULT, xmrig.instance() + '.log'))
            self.insert_one(xmrig)
            job = Job(op=NEW_FIELD, elem_type=XMRIG_FIELD, instance=xmrig.instance())
            job.msg("Created new XMRig deployment")
            self.job_queue.post_completed_job(job)
        return xmrig


    def create_vendor_dir(self, new_dir: str, db4e: Db4E):
        update_flag = True
        if os.path.exists(new_dir):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
            backup_vendor_dir = new_dir + '.' + timestamp
            try:
                os.rename(new_dir, backup_vendor_dir)
                db4e.msg(VENDOR_DIR_LABEL, WARN_FIELD, 
                    f"Found existing directory ({new_dir}), backed it up as ({backup_vendor_dir})")
            except (PermissionError, OSError) as e:
                update_flag = False
                db4e.msg(VENDOR_DIR_LABEL, ERROR_FIELD, 
                    f"Unable to backup ({new_dir}) as ({backup_vendor_dir}), aborting deployment directory update:\n{e}")
                return db4e, update_flag
            
        try:
            os.makedirs(new_dir)
            db4e.msg(VENDOR_DIR_LABEL, GOOD_FIELD, f"Created new {VENDOR_DIR_FIELD}: {new_dir}")
        except (PermissionError, OSError) as e:
            db4e.msg(VENDOR_DIR_LABEL, ERROR_FIELD, 
                f"Unable to create new {VENDOR_DIR_FIELD}: {new_dir}, aborting deployment directory update:\n{e}")
            update_flag = False

        return db4e, update_flag


    def del_deployment(self, elem):
        self.db_cache.delete_one(elem)


    def get_component_value(self, data, field_name):
        """
        Generic helper to get any component value by field name.
        
        Args:
            data (dict): Dictionary containing components with field/value pairs
            field_name (str): The field name to search for
            
        Returns:
            any or None: The component value, or None if not found
        """
        if not isinstance(data, dict) or 'components' not in data:
            return None
        
        components = data.get(COMPONENTS_FIELD, [])
        
        for component in components:
            if isinstance(component, dict) and component.get(FIELD_FIELD) == field_name:
                return component.get(VALUE_FIELD)
        
        return None


    def get_deployment(self, elem_type, instance=None):
        #print(f"DeploymentMgr:get_deployment(): {component}/{instance}")
        return self.db_cache.get_deployment(elem_type, instance)


    def get_deployment_by_id(self, id):
        return self.db_cache.get_deployment_by_id(id)


    def get_deployment_ids_and_instances(self, elem_type):
        return self.db_cache.get_deployment_ids_and_instances(elem_type)
    

    def get_deployments(self):
        return self.db_cache.get_deployments()


    def get_downstream(self, elem):
        return self.db_cache.get_downstream(elem)

    def get_template(self, elem_type):
        tmpl_dir = self.get_dir(TEMPLATE_FIELD)

        if elem_type == MONEROD_FIELD:
            monerod_dir = self.get_dir(MONEROD_FIELD)
            tmpl_file = os.path.join(tmpl_dir, monerod_dir, CONF_DIR_DEFAULT, MONEROD_CONFIG_DEFAULT)

        elif elem_type == P2POOL_FIELD:
            p2pool_dir = self.get_dir(P2POOL_FIELD)
            tmpl_file = os.path.join(tmpl_dir, p2pool_dir, CONF_DIR_DEFAULT, P2POOL_CONFIG_DEFAULT)

        elif elem_type == XMRIG_FIELD:
            xmrig_dir = self.get_dir(XMRIG_FIELD)
            tmpl_file = os.path.join(tmpl_dir, xmrig_dir, CONF_DIR_DEFAULT, XMRIG_CONFIG_DEFAULT)

        else:
            raise ValueError(f"DeploymentMgr:get_template(): No handler for {elem_type}")

        return tmpl_file


    def get_dir(self, aDir: str) -> str:

        if aDir == DB4E_FIELD:
            return os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
        
        elif aDir == PYTHON_FIELD:
            python = os.path.abspath(
                os.path.join(os.path.dirname(__file__),'..','..','..','..','..', 
                             BIN_DIR_DEFAULT, PYTHON_DEFAULT))
            return python
        
        elif aDir == INSTALL_DIR_FIELD:
            return os.path.abspath(
                os.path.join(os.path.dirname(__file__),'..','..','..','..','..'))
        
        elif aDir == TEMPLATE_FIELD:
            return os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..', DB4E_FIELD, TEMPLATES_DIR_DEFAULT))
        
        elif aDir == VENDOR_DIR_FIELD:
            db4e = self.db_cache.get_db4e()
            return db4e.vendor_dir()

        elif aDir == MONEROD_FIELD:
            return MONEROD_FIELD + '-' + MONEROD_VERSION_DEFAULT
        
        elif aDir == P2POOL_FIELD:
            return P2POOL_FIELD + '-' + P2POOL_VERSION_DEFAULT

        elif aDir == XMRIG_FIELD:
            return XMRIG_FIELD + '-' + XMRIG_VERSION_DEFAULT

        else:
            raise ValueError(f"OpsMgr:get_dir(): No handler for: {aDir}")


    def get_monerods(self):
        return self.db_cache.get_monerods()
    
    
    def get_new(self, elem_type):
        if elem_type == MONEROD_FIELD:
            return MoneroD()
        elif elem_type == MONEROD_REMOTE_FIELD:
            return MoneroDRemote()
        elif elem_type == P2POOL_FIELD:
            p2pool = P2Pool()
            db4e = self.db_cache.get_db4e()
            p2pool.user_wallet(db4e.user_wallet())
            return p2pool
        elif elem_type == P2POOL_REMOTE_FIELD:
            return P2PoolRemote()
        elif elem_type == XMRIG_FIELD:
            return XMRig()
        else:
            raise ValueError(f"DeploymentMgr:get_new(): No handler for {elem_type}")


    def get_p2pools(self):
        return self.db_cache.get_p2pools()
    
    
    def get_xmrigs(self):
        return self.db_cache.get_xmrigs()


    def insert_one(self, elem):
        ## Don't put the HEALTH_MSGS_FIELD (the status messages) into the DB
        # Pop off 
        return self.db_cache.insert_one(elem)
        

    def is_initialized(self):
        db4e = self.db_cache.get_db4e()
        if db4e:
            if db4e.vendor_dir() and db4e.user_wallet():
                return True
            else:
                return False
        else:
            return False


    def post_job(self, job_info):
        job = Job(op=job_info[OP_FIELD], elem_type=job_info[ELEMENT_TYPE_FIELD])
        elem = job_info[ELEMENT_FIELD]
        job.elem(elem)
        job.instance(elem.instance())
        self.job_queue.post_job(job)


    def update_deployment(self, elem):
        if type(elem) == Db4E:
            return self.update_db4e_deployment(db4e=elem)
        elif type(elem) == MoneroD:
            return self.update_monerod_deployment(monerod=elem)
        elif type(elem) == P2Pool:
            return self.update_p2pool_deployment(p2pool=elem)
        elif type(elem) == XMRig:
            return self.update_xmrig_deployment(xmrig=elem)


    def update_db4e_deployment(self, new_db4e: Db4E):
        update_flag = False

        # The current record, we'll update this and write it back in
        db4e = self.db_cache.get_db4e()

        # Updating user wallet
        if db4e.user_wallet != new_db4e.user_wallet:
            db4e.user_wallet(new_db4e.user_wallet())
            self.update_one(db4e)
            msg = f"Updated wallet: {db4e.user_wallet()[:6]}... > " \
                f"{new_db4e.user_wallet()[:6]}..."
            db4e.msg(USER_WALLET_LABEL, GOOD_FIELD, msg)
            update_flag = True

        # Updating vendor dir
        if db4e.vendor_dir != new_db4e.vendor_dir:
            if not db4e.vendor_dir():
                db4e, update_flag = self.create_vendor_dir(
                    new_dir=new_db4e.vendor_dir(),
                    db4e=db4e)

            else:
                db4e, update_flag = self.update_vendor_dir(
                    new_dir=new_db4e.vendor_dir(),
                    old_dir=db4e.vendor_dir(),
                    db4e=db4e)
            msg = f"Updated vendor dir: {db4e.vendor_dir()} > " \
                f"{new_db4e.vendor_dir()}"
            db4e.msg(VENDOR_DIR_LABEL, GOOD_FIELD, msg)
            db4e.vendor_dir(new_db4e.vendor_dir())
            update_flag = True

        if update_flag:
            self.db_cache.update_one(db4e)
        else:
            db4e.msg(DB4E_LABEL, WARN_FIELD, "Nothing to update")

        return db4e



    def update_deployment(self, elem):
        #print(f"DeploymentMgr:update_deployment(): {rec}")
        if type(elem) == Db4E:
            return self.update_db4e_deployment(elem)
        elif type(elem) == MoneroD:
            return self.update_monerod_deployment(elem)
        elif type(elem) == MoneroDRemote:
            return self.update_monerod_remote_deployment(elem)
        elif type(elem) == P2Pool:
            return self.update_p2pool_deployment(elem)
        elif type(elem) == P2PoolRemote:
            return self.update_p2pool_remote_deployment(elem)
        elif type(elem) == XMRig:
            return self.update_xmrig_deployment(elem)
        else:
            raise ValueError(
                f"{DEPLOYMENT_MGR_FIELD}:update_deployment(): No handler for component " \
                f"({elem})")


    def update_monerod_deployment(self, new_monerod: MoneroD):
        update = False
        update_config = False

        monerod = self.db_cache.get_deployment(MONEROD_FIELD, new_monerod.instance())
        if not monerod:
            raise ValueError(f"DeploymentMgr:update_monerod_deployment(): " \
                             f"No monerod found for {new_monerod}")
        
        if monerod.enabled() != new_monerod.enabled():
            # This is an enable/disable operation
            if monerod.enabled():
                monerod.disable()
            else:
                monerod.enable()
            update = True

        else:
            # This is an update op

            # In Peers
            if monerod.in_peers != new_monerod.in_peers:
                msg = f"Updated in peers: {monerod.in_peers()} > " \
                    f"{new_monerod.in_peers()}"
                monerod.in_peers(new_monerod.in_peers())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # Out Peers
            if monerod.out_peers != new_monerod.out_peers:
                msg = f"Updated out peers: {monerod.out_peers()} > " \
                    f"{new_monerod.out_peers()}"
                monerod.out_peers(new_monerod.out_peers())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # P2P Bind Port
            if monerod.p2p_bind_port != new_monerod.p2p_bind_port:
                msg = f"Updated P2P bind port: {monerod.p2p_bind_port()} > " \
                    f"{new_monerod.p2p_bind_port()}"
                monerod.p2p_bind_port(new_monerod.p2p_bind_port())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # RPC Bind Port
            if monerod.rpc_bind_port != new_monerod.rpc_bind_port:
                msg = f"Updated RPC bind port: {monerod.rpc_bind_port()} > " \
                    f"{new_monerod.rpc_bind_port()}"
                monerod.rpc_bind_port(new_monerod.rpc_bind_port())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # ZMQ Pub Port
            if monerod.zmq_pub_port != new_monerod.zmq_pub_port:
                msg = f"Updated ZMQ pub port: {monerod.zmq_pub_port()} > " \
                    f"{new_monerod.zmq_pub_port()}"
                monerod.zmq_pub_port(new_monerod.zmq_pub_port())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # ZMQ RPC Port
            if monerod.zmq_rpc_port != new_monerod.zmq_rpc_port:
                msg = f"Updated ZMQ RPC port: {monerod.zmq_rpc_port()} > " \
                    f"{new_monerod.zmq_rpc_port()}"
                monerod.zmq_rpc_port(new_monerod.zmq_rpc_port())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # Log Level
            if monerod.log_level != new_monerod.log_level:
                msg = f"Updated log level: {monerod.log_level()} > " \
                    f"{new_monerod.log_level()}"
                monerod.log_level(new_monerod.log_level())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # Max Log Files
            if monerod.max_log_files != new_monerod.max_log_files:
                msg = f"Updated max log files: {monerod.max_log_files()} > " \
                    f"{new_monerod.max_log_files()}"
                monerod.max_log_files(new_monerod.max_log_files())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # Max Log Size
            if monerod.max_log_size != new_monerod.max_log_size:
                msg = f"Updated max log size: {monerod.max_log_size()} > " \
                    f"{new_monerod.max_log_size()}"
                monerod.max_log_size(new_monerod.max_log_size())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True
            
            # Priority Node 1 hostname
            if monerod.priority_node_1 != new_monerod.priority_node_1:
                msg = f"Updated priority node 1: {monerod.priority_node_1()} > " \
                    f"{new_monerod.priority_node_1()}"
                monerod.priority_node_1(new_monerod.priority_node_1())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # Priority Port 1
            if monerod.priority_port_1 != new_monerod.priority_port_1:
                msg = f"Updated priority port 1: {monerod.priority_port_1()} > " \
                    f"{new_monerod.priority_port_1()}"
                monerod.priority_port_1(new_monerod.priority_port_1())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # Priority Node 2 hostname
            if monerod.priority_node_2 != new_monerod.priority_node_2:
                msg = f"Updated priority node 2: {monerod.priority_node_2()} > " \
                    f"{new_monerod.priority_node_2()}"
                monerod.priority_node_2(new_monerod.priority_node_2())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

            # Priority Port 2
            if monerod.priority_port_2 != new_monerod.priority_port_2:
                msg = f"Updated priority port 2: {monerod.priority_port_2()} > " \
                    f"{new_monerod.priority_port_2()}"
                monerod.priority_port_2(new_monerod.priority_port_2())
                monerod.msg(MONEROD_SHORT_LABEL, GOOD_FIELD, msg)
                update, update_config = True, True

        if update_config:
            vendor_dir = self.get_dir(VENDOR_DIR_FIELD)
            tmpl_file = self.get_template(MONEROD_FIELD)
            monerod.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)

        if update:
            self.update_one(monerod)
            job = Job(op=RESTART_FIELD, elem_type=MONEROD_FIELD,
                      elem=monerod,
                      instance=monerod.instance())
            self.job_queue.post_job(job)
        else:
            monerod.msg(MONEROD_SHORT_LABEL, WARN_FIELD, "Nothing to update")
            
        return monerod


    def update_monerod_remote_deployment(self, new_monerod: MoneroDRemote) -> MoneroDRemote:
        #print(f"DeploymentMgr:update_monerod_remote_deployment(): {new_monerod}")
        update = False
        monerod = self.db_cache.get_deployment(MONEROD_FIELD, new_monerod.instance())
        if not monerod:
            raise ValueError(f"DeploymentMgr:update_monerod_remote_deployment(): " \
                             f"No monerod found for {new_monerod.id()}")

        ## Field-by-field comparison
        # IP Address
        if monerod.ip_addr != new_monerod.ip_addr:
            msg = f"Updated IP/hostname: {monerod.ip_addr()} > " \
                f"{new_monerod.ip_addr()}"
            monerod.ip_addr(new_monerod.ip_addr())
            monerod.msg(MONEROD_LABEL, GOOD_FIELD, msg)
            update = True

        # RPC Bind Port
        if monerod.rpc_bind_port != new_monerod.rpc_bind_port:
            msg = f"Updated RPC bind port: {monerod.rpc_bind_port()} > " \
                f"{new_monerod.rpc_bind_port()}"
            monerod.rpc_bind_port(new_monerod.rpc_bind_port())
            monerod.msg(MONEROD_LABEL, GOOD_FIELD, msg)
            update = True

        # ZMQ Pub Port
        if monerod.zmq_pub_port != new_monerod.zmq_pub_port:
            msg = f"Updated ZMQ pub port: {monerod.zmq_pub_port()} > " \
                f"{new_monerod.zmq_pub_port()}"
            monerod.zmq_pub_port(new_monerod.zmq_pub_port())
            monerod.msg(MONEROD_LABEL, GOOD_FIELD, msg)
            update = True

        if update:
            monerod = self.db_cache.update_one(monerod)

        else:
            monerod.msg(MONEROD_LABEL, WARN_FIELD,
                f"{monerod.instance()} – Nothing to update")
            
        return monerod


    def update_one(self, elem):
        #print(f"DeploymentMgr:update_one(): {elem.to_rec()}")
        # Don't store status messages in the DB
        msgs = elem.pop_msgs()
        #print(f"DeploymentMgr:update_one(): {elem.to_rec()}")

        elem = self.db_cache.update_one(elem)

        elem.push_msgs(msgs)
        return elem
    

    def update_p2pool_deployment(self, new_p2pool: P2Pool) -> P2Pool:
        update = False
        update_config = False

        p2pool = self.db_cache.get_deployment(P2POOL_FIELD, new_p2pool.instance())
        if not p2pool:
            raise ValueError(f"DeploymentMgg:update_p2pool_deployment(): " \
                             f"Nothing found for {new_p2pool}")

        if p2pool.enabled() != new_p2pool.enabled():
            # This is an enable/disable operation
            if p2pool.enabled():
                p2pool.disable()
            else:
                p2pool.enable()
            update = True

        else:
            # This is an update op
            
            # In Peers
            if p2pool.in_peers != new_p2pool.in_peers:
                msg = f"Updated in peers: {p2pool.in_peers()} > " \
                    f"{new_p2pool.in_peers()}"
                p2pool.in_peers(new_p2pool.in_peers())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, msg)
                update_config = True
                update = True

            # Out Peers
            if p2pool.out_peers != new_p2pool.out_peers:
                msg = f"Updated out peers: {p2pool.out_peers()} > " \
                    f"{new_p2pool.out_peers()}"
                p2pool.out_peers(new_p2pool.out_peers())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, msg)
                update_config = True
                update = True

            # P2P Bind Port
            if p2pool.p2p_bind_port != new_p2pool.p2p_bind_port:
                msg = f"Updated P2P bind port: {p2pool.p2p_bind_port()} > " \
                    f"{new_p2pool.p2p_bind_port()}"
                p2pool.p2p_bind_port(new_p2pool.p2p_bind_port())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, msg)
                update_config = True
                update = True

            # Stratum port
            if p2pool.stratum_port != new_p2pool.stratum_port:
                msg = f"Updated stratum port: {p2pool.stratum_port()} > " \
                    f"{new_p2pool.stratum_port()}"
                p2pool.stratum_port(new_p2pool.stratum_port())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, msg)
                update_config = True
                update = True

            # Log level
            if p2pool.log_level != new_p2pool.log_level:
                msg = f"Updated log level: {p2pool.log_level()} > " \
                    f"{new_p2pool.log_level()}"
                p2pool.log_level(new_p2pool.log_level())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, msg)
                update_config = True
                update = True

            # Upstream P2Pool
            if p2pool.parent != new_p2pool.parent:
                parent = self.get_deployment_by_id(new_p2pool.parent())
                parent_instance = parent.instance()
                new_parent = self.get_deployment_by_id(p2pool.parent())
                msg = f"Updated upstream P2Pool: {parent_instance} > " \
                    f"{new_parent_instance}"
                p2pool.parent(new_p2pool.parent())
                new_parent_instance = new_parent.instance()
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, "Using new P2Pool deployment")
                update_config = True
                update = True

        if update_config:
            vendor_dir = self.get_dir(VENDOR_DIR_FIELD)
            tmpl_file = self.get_template(P2POOL_FIELD)
            p2pool.monerod = self.db_cache.get_deployment_by_id(p2pool.parent())
            p2pool.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)

        if update:
            self.update_one(p2pool)
            job = Job(op=RESTART_FIELD, elem_type=P2POOL_FIELD, 
                      elem=p2pool,
                      instance=p2pool.instance())
            self.job_queue.post_job(job)
        else:
            p2pool.msg(P2POOL_SHORT_LABEL, WARN_FIELD, "Nothing to update")

        return p2pool



    def update_p2pool_remote_deployment(self, new_p2pool: P2PoolRemote) -> P2PoolRemote:
        update = False

        p2pool = self.db_cache.get_deployment(P2POOL_REMOTE_FIELD, new_p2pool.instance())
        if not p2pool:
            raise ValueError(f"DeploymentMgg:update_p2pool_remote_deployment(): " \
                             f"Nothing found for {new_p2pool.id()}")

        ## Field-by-field comparison
        # IP Address
        if p2pool.ip_addr != new_p2pool.ip_addr:
            msg = f"Updated IP/hostname: {p2pool.ip_addr()} > " \
                f"{new_p2pool.ip_addr()}"
            p2pool.ip_addr(new_p2pool.ip_addr())
            p2pool.msg(P2POOL_LABEL, GOOD_FIELD, msg)
            update = True

        # Stratum Port
        if p2pool.stratum_port != new_p2pool.stratum_port:
            msg = f"Updated stratum port: {p2pool.stratum_port()} > " \
                f"{new_p2pool.stratum_port()}"
            p2pool.stratum_port(new_p2pool.stratum_port())
            p2pool.msg(P2POOL_LABEL, GOOD_FIELD, msg)
            update = True

        if update:
            self.update_one(p2pool)
            
        else:
            p2pool.msg(P2POOL_LABEL, WARN_FIELD, "Nothing to update")
        return p2pool


    def update_vendor_dir(self, new_dir: str, old_dir: str, db4e: Db4E) -> Db4E:
        #print(f"DeploymentMgr:update_vendor_dir(): {old_dir} > {new_dir}")
        update_flag = True

        if old_dir == new_dir:
            return

        if not new_dir:
            raise ValueError(f"update_vendor_dir(): Missing new directory")        

        # The target vendor dir exists, make a backup
        if os.path.exists(new_dir):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
            backup_vendor_dir = new_dir + '.' + timestamp
            try:
                os.rename(new_dir, backup_vendor_dir)
                db4e.msg(VENDOR_DIR_LABEL, WARN_FIELD, 
                    f'Found existing directory ({new_dir}), backed it up as ({backup_vendor_dir})')
                return db4e, update_flag
            except (PermissionError, OSError) as e:
                update_flag = False
                db4e.msg(VENDOR_DIR_LABEL, ERROR_FIELD, 
                    f"Unable to backup ({new_dir}) as ({backup_vendor_dir}), " \
                    f"aborting deployment directory update:\n{e}")
                return db4e, update_flag

        # No need to move if old_dir is empty (first-time initialization)
        if not old_dir:
            db4e.msg(VENDOR_DIR_LABEL, GOOD_FIELD,
                f"Crated new {VENDOR_DIR_FIELD}: {new_dir}")
            return db4e, update_flag
        
        # Move the vendor_dir to the new location
        try:
            os.rename(old_dir, new_dir)
            db4e.msg(VENDOR_DIR_LABEL, GOOD_FIELD, 
                f'Moved vendor dir from ({old_dir}) to ({new_dir})')
        except (PermissionError, OSError) as e:
            db4e.msg(VENDOR_DIR_LABEL, ERROR_FIELD, 
                f"Unable to move vendor dir from ({old_dir}) to ({new_dir}), " \
                f"aborting deployment directory update:\n{e}")
            update_flag = False

        #print(f"DeploymentMgr:update_vendor_dir(): results: {results}")
        return db4e, update_flag


    def update_xmrig_deployment(self, new_xmrig: XMRig) -> XMRig:
        update = False
        update_config = False

        xmrig = self.get_deployment(XMRIG_FIELD, new_xmrig.instance())
        print(f"DeploymentMgr:update_xmrig_deployment(): old enabled: {xmrig.enabled()}")
        if not xmrig:
            raise ValueError(f"DeploymentMgg:update_xmrig_deployment(): " \
                             f"Nothing found for {new_xmrig.id()}")

        if xmrig.enabled() != new_xmrig.enabled():
            # This is an enable/disable operation
            if xmrig.enabled():
                xmrig.disable()
            else:
                xmrig.enable()
            update = True

        else:
            # User clicked "update", do a field-by-field comparison
            job = Job(op=UPDATE_FIELD, elem_type=XMRIG_FIELD, instance=xmrig.instance())

            # Num Threads
            if xmrig.num_threads != new_xmrig.num_threads:
                msg = f"Updated number of threads: {xmrig.num_threads()} > " \
                    f"{new_xmrig.num_threads()}"
                xmrig.msg(XMRIG_SHORT_LABEL, GOOD_FIELD, msg) 
                xmrig.num_threads(new_xmrig.num_threads())
                update = True
                update_config = True

            # Parent ID
            if xmrig.parent != new_xmrig.parent:
                parent = self.get_deployment_by_id(new_xmrig.parent())
                parent_instance = parent.instance()
                new_parent = self.get_deployment_by_id(xmrig.parent())
                new_parent_instance = new_parent.instance()
                msg = f"Updated parent: {xmrig.parent()} > {new_xmrig.parent()}"
                xmrig.parent(new_xmrig.parent())
                msg = f"Updated parent: {parent_instance} > {new_parent_instance}"
                xmrig.msg(XMRIG_SHORT_LABEL, GOOD_FIELD, msg)
                update = True
                update_config = True

        # Regenerate config if required
        if update_config:
            vendor_dir = self.get_dir(VENDOR_DIR_FIELD)
            tmpl_file = self.get_template(XMRIG_FIELD)
            xmrig.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)

        if update:
            self.update_one(xmrig)
            job = Job(op=RESTART_FIELD, elem_type=XMRIG_FIELD, instance=xmrig.instance())
            job.msg("XMRig loaded new settings")
            self.job_queue.post_completed_job(job)

        return xmrig