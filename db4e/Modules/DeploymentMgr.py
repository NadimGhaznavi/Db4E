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
    MONEROD_LABEL, MONEROD_REMOTE_LABEL, P2POOL_LABEL,
    USER_WALLET_LABEL, VENDOR_DIR_LABEL, XMRIG_SHORT_LABEL, P2POOL_SHORT_LABEL)
from db4e.Constants.Fields import (
    PYTHON_FIELD, DB4E_FIELD, ERROR_FIELD,
    TEMPLATE_FIELD, GOOD_FIELD, INSTALL_DIR_FIELD, NEW_FIELD,
    MONEROD_FIELD, MONEROD_REMOTE_FIELD,
    P2POOL_FIELD, P2POOL_REMOTE_FIELD, VENDOR_DIR_FIELD, WARN_FIELD, XMRIG_FIELD,
    DEPLOYMENT_MGR_FIELD, COMPONENTS_FIELD, FIELD_FIELD, VALUE_FIELD)
from db4e.Constants.Defaults import (
    BIN_DIR_DEFAULT, PYTHON_DEFAULT, TEMPLATES_DIR_DEFAULT,
    CONF_DIR_DEFAULT, API_DIR_DEFAULT, LOG_DIR_DEFAULT, RUN_DIR_DEFAULT)


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
        #print(f"DeploymentMgr:add_remote_monerod_deployment(): {rec}")
        monerod.msg(MONEROD_REMOTE_LABEL, WARN_FIELD,
            f"🚧 {MONEROD_REMOTE_FIELD} deployment coming soon 🚧")
        return monerod


    def add_remote_monerod_deployment(self, monerod: MoneroDRemote):
        #print(f"DeploymentMgr:add_remote_monerod_deployment(): {rec}")
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
            tmpl_dir = self.get_dir(TEMPLATE_FIELD)
            vendor_dir = self.get_dir(VENDOR_DIR_FIELD)
            p2pool_dir = P2POOL_FIELD + '-' + p2pool.version()
            tmpl_file = os.path.join(tmpl_dir, p2pool_dir, CONF_DIR_DEFAULT, 'p2pool.ini')
            p2pool.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)
            self.insert_one(p2pool)
            job = Job(op=NEW_FIELD, elem_type=P2POOL_FIELD, instance=p2pool.instance())
            os.makedirs(os.path.join(vendor_dir, p2pool_dir, p2pool.instance(), LOG_DIR_DEFAULT), exist_ok=True)
            os.makedirs(os.path.join(vendor_dir, p2pool_dir, p2pool.instance(), RUN_DIR_DEFAULT), exist_ok=True)
            os.makedirs(os.path.join(vendor_dir, p2pool_dir, p2pool.instance(), API_DIR_DEFAULT), exist_ok=True)
            job.msg("Created new P2Pool deployment")
            self.job_queue.post_completed_job(job)
        return p2pool


    def add_remote_p2pool_deployment(self, p2pool: P2PoolRemote) -> P2PoolRemote:
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
            tmpl_dir = self.get_dir(TEMPLATE_FIELD)
            vendor_dir = self.get_dir(VENDOR_DIR_FIELD)
            xmrig_dir = XMRIG_FIELD + '-' + xmrig.version()
            tmpl_file = os.path.join(tmpl_dir, xmrig_dir, CONF_DIR_DEFAULT, 'config.json')
            xmrig.gen_config(tmpl_file=tmpl_file, vendor_dir=vendor_dir)
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
        update_flag = True

        # The current record, we'll update this and write it back in
        db4e = self.db_cache.get_db4e()

        # Updating user wallet
        if db4e.user_wallet != new_db4e.user_wallet:
            db4e.user_wallet(new_db4e.user_wallet())
            self.update_one(db4e)
            db4e.msg(USER_WALLET_LABEL, GOOD_FIELD, f"Set the Db4E user wallet: {db4e.user_wallet()}")

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

            db4e.vendor_dir(new_db4e.vendor_dir())

        #print(f"DeploymentMgr:update_db4e_deployment(): final rec: {rec}")
        if update_flag:
            self.db_cache.update_one(db4e)

        #print(f"DeploymentMgr:update_db4e_deployment():")
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
            print(f"DeploymentMgr:update_deployment(): 2. {elem.enabled()}")
            return self.update_xmrig_deployment(elem)
        else:
            raise ValueError(
                f"{DEPLOYMENT_MGR_FIELD}:update_deployment(): No handler for component " \
                f"({elem})")


    def update_monerod_deployment(self, new_monerod: MoneroD):
        pass


    def update_monerod_remote_deployment(self, new_monerod: MoneroDRemote) -> MoneroDRemote:
        #print(f"DeploymentMgr:update_monerod_remote_deployment(): {new_monerod}")
        update = False
        monerod = self.db_cache.get_deployment(MONEROD_FIELD, new_monerod.instance())
        if not monerod:
            raise ValueError(f"DeploymentMgr:update_monerod_remote_deployment(): " \
                             f"No monerod found for {new_monerod.id()}")

        ## Field-by-field comparison
        # Instance
        if monerod.instance != new_monerod.instance:
            monerod.instance(new_monerod.instance())
            monerod.msg(MONEROD_LABEL, GOOD_FIELD, "Updated instance name")
            update = True

        # IP Address
        if monerod.ip_addr != new_monerod.ip_addr:
            monerod.ip_addr(new_monerod.ip_addr())
            monerod.msg(MONEROD_LABEL, GOOD_FIELD, "Updated IP/hostname")
            update = True

        # RPC Bind Port
        if monerod.rpc_bind_port != new_monerod.rpc_bind_port:
            monerod.rpc_bind_port(new_monerod.rpc_bind_port())
            monerod.msg(MONEROD_LABEL, GOOD_FIELD, "Updated RPC port")
            update = True

        # ZMQ Pub Port
        if monerod.zmq_pub_port != new_monerod.zmq_pub_port:
            monerod.zmq_pub_port(new_monerod.zmq_pub_port())
            monerod.msg(MONEROD_LABEL, GOOD_FIELD, "Updated ZMQ port")
            update = True

        if update:
            monerod = self.db_cache.update_one(monerod)

        else:
            monerod.msg(MONEROD_LABEL, WARN_FIELD,
                f"{monerod.instance()} – Nothing to update")
            
        return monerod


    def update_one(self, elem):
        print(f"DeploymentMgr:update_one(): {elem.to_rec()}")
        # Don't store status messages in the DB
        msgs = elem.pop_msgs()
        #print(f"DeploymentMgr:update_one(): {elem.to_rec()}")

        elem = self.db_cache.update_one(elem)

        elem.push_msgs(msgs)
        return elem
    

    def update_p2pool_deployment(self, new_p2pool: P2Pool) -> P2Pool:
        update = False

        p2pool = self.db_cache.get_deployment(P2POOL_FIELD, new_p2pool.instance())
        if not p2pool:
            raise ValueError(f"DeploymentMgg:update_p2pool_deployment(): " \
                             f"Nothing found for {new_p2pool.id()}")

        if p2pool.enabled() != new_p2pool.enabled():
            # This is an enable/disable operation
            if p2pool.enabled():
                p2pool.disable()
            else:
                p2pool.enable()
            update = True

        else:
            # User clicked "update", do a field-by-field comparison
            
            # Instance
            if p2pool.instance != new_p2pool.instance:
                p2pool.instance(new_p2pool.instance())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, "Updated instance name")
                update = True

            # In Peers
            if p2pool.in_peers != new_p2pool.in_peers:
                p2pool.in_peers(new_p2pool.in_peers())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, "Updated in peers")
                update = True

            # Out Peers
            if p2pool.out_peers != new_p2pool.out_peers:
                p2pool.out_peers(new_p2pool.out_peers())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, "Updated out peers")
                update = True

            # P2P Bind Port
            if p2pool.p2p_bind_port != new_p2pool.p2p_bind_port:
                p2pool.p2p_bind_port(new_p2pool.p2p_bind_port())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, "Updated P2P bind port")
                update = True

            # Stratum port
            if p2pool.stratum_port != new_p2pool.stratum_port:
                p2pool.stratum_port(new_p2pool.stratum_port())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, "Updated stratum port")
                update = True

            # Log level
            if p2pool.log_level != new_p2pool.log_level:
                p2pool.log_level(new_p2pool.log_level())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, "Updated log level")
                update = True

            # Upstream P2Pool
            if p2pool.parent != new_p2pool.parent:
                p2pool.parent(new_p2pool.parent())
                p2pool.msg(P2POOL_SHORT_LABEL, GOOD_FIELD, "Using new P2Pool deployment")
                update = True

        if update:
            self.update_one(p2pool)

        return p2pool



    def update_p2pool_remote_deployment(self, new_p2pool: P2PoolRemote) -> P2PoolRemote:
        update = False

        #print(f"DeploymentMgr:update_p2pool_remote_deployment(): {new_p2pool.to_rec()}")

        p2pool = self.db_cache.get_deployment(P2POOL_REMOTE_FIELD, new_p2pool.instance())
        if not p2pool:
            raise ValueError(f"DeploymentMgg:update_p2pool_remote_deployment(): " \
                             f"Nothing found for {new_p2pool.id()}")

        ## Field-by-field comparison
        # Instance
        if p2pool.instance != new_p2pool.instance:
            p2pool.instance(new_p2pool.instance())
            p2pool.msg(P2POOL_LABEL, GOOD_FIELD, "Updated instance name")
            update = True

        # IP Address
        if p2pool.ip_addr != new_p2pool.ip_addr:
            p2pool.ip_addr(new_p2pool.ip_addr())
            p2pool.msg(P2POOL_LABEL, GOOD_FIELD, "Updated IP/hostname")
            update = True

        # Stratum Port
        if p2pool.stratum_port != new_p2pool.stratum_port:
            p2pool.stratum_port(new_p2pool.stratum_port())
            p2pool.msg(P2POOL_LABEL, GOOD_FIELD,"Updated stratum port")
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
        print(f"DeploymentMgr:update_xmrig_deployment(): 3: {xmrig.enabled()}")
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

            # Instance
            if xmrig.instance != new_xmrig.instance:
                xmrig.instance(new_xmrig.instance())
                xmrig.msg(XMRIG_SHORT_LABEL, GOOD_FIELD, "Updated instance name")
                update = True
                update_config = True

            # Num Threads
            if xmrig.num_threads != new_xmrig.num_threads:
                xmrig.num_threads(new_xmrig.num_threads())
                xmrig.msg(XMRIG_SHORT_LABEL, GOOD_FIELD, "Updated number of threads") 
                update = True
                update_config = True

            # Parent ID
            print(f"{xmrig.parent()} == {new_xmrig.parent()}")
            if xmrig.parent != new_xmrig.parent:
                xmrig.parent(new_xmrig.parent())
                xmrig.msg(XMRIG_SHORT_LABEL, GOOD_FIELD, "Using new P2Pool deployment")
                update = True
                update_config = True

        # Regenerate config if required
        if update_config:
            pass
            # TODO, send message to server telling it to regenerate the config

        if update:
            self.update_one(xmrig)

        return xmrig