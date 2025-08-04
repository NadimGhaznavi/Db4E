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

from textual.containers import Container
from db4e.Modules.ConfigMgr import Config, ConfigMgr
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.Helper import (
    gen_radio_map, get_component_value, get_effective_identity,
    is_valid_ip_or_hostname, result_row, set_component_value,
    update_component_values)
from db4e.Constants.Labels import (
    DB4E_LABEL, MONEROD_LABEL, MONEROD_REMOTE_LABEL, P2POOL_LABEL,
    USER_WALLET_LABEL, VENDOR_DIR_LABEL, XMRIG_LABEL
)
from db4e.Constants.Fields import (
    COMPONENT_FIELD, CONFIG_FIELD, DB4E_FIELD, ELEMENT_TYPE_FIELD, ERROR_FIELD,
    FORM_DATA_FIELD, GOOD_FIELD, GROUP_FIELD, ID_FIELD, INSTALL_DIR_FIELD,
    INSTANCE_FIELD, IP_ADDR_FIELD, MONEROD_FIELD, MONEROD_REMOTE_FIELD,
    NUM_THREADS_FIELD, ORIG_INSTANCE_FIELD, PARENT_ID_FIELD, P2POOL_FIELD,
    P2POOL_REMOTE_FIELD, RPC_BIND_PORT_FIELD, STRATUM_PORT_FIELD, USER_FIELD,
    USER_WALLET_FIELD, VENDOR_DIR_FIELD, WARN_FIELD, XMRIG_FIELD,
    ZMQ_PUB_PORT_FIELD, HEALTH_MSGS_FIELD, DEPLOYMENT_MGR_FIELD, COMPONENTS_FIELD,
    FIELD_FIELD, VALUE_FIELD, RADIO_MAP_FIELD
)
from db4e.Constants.Defaults import (
    DEPLOYMENT_COL_DEFAULT
)
                                     
class DeploymentMgr(Container):
    
    def __init__(self, config: Config):
        super().__init__()
        self.ini = config
        self.conf_mgr = ConfigMgr(app_version='UNUSED')
        self.db = DbMgr(config)
        self.depl_col = DEPLOYMENT_COL_DEFAULT
        self.db4e_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.init_db()


    def add_deployment(self, rec):
        #print(f"DeploymentMgr:add_deployment(): {rec}")
        elem_type = rec[ELEMENT_TYPE_FIELD]

        # Add the Db4E Core deployment
        if elem_type == DB4E_FIELD:
            return self.insert_one(rec)

        # Add a Monero daemon deployment
        elif elem_type == MONEROD_REMOTE_FIELD:
            return self.add_remote_monerod_deployment(rec)
            
        # Add a P2Pool deployment
        elif elem_type == P2POOL_REMOTE_FIELD:
            return self.add_remote_p2pool_deployment(rec)
            
        # Add a XMRig deployment
        elif elem_type == XMRIG_FIELD:
            return self.add_xmrig_deployment(rec)

        # Catchall
        else:
            raise ValueError(f"DeploymentMgr:add_deployment(): No handler for {elem_type}")


    def add_monerod_deployment(self, rec):
        #print(f"DeploymentMgr:add_remote_monerod_deployment(): {rec}")
        results = []
        results.append(result_row(
            MONEROD_REMOTE_LABEL, WARN_FIELD,
            f"🚧 {MONEROD_REMOTE_FIELD} deployment coming soon 🚧"
        ))
        rec[HEALTH_MSGS_FIELD] += results


    def add_remote_monerod_deployment(self, rec):
        #print(f"DeploymentMgr:add_remote_monerod_deployment(): {rec}")
        update = True
        instance = get_component_value(rec, INSTANCE_FIELD)
        ip_addr = get_component_value(rec, IP_ADDR_FIELD)
        rpc_bind_port = get_component_value(rec, RPC_BIND_PORT_FIELD)
        zmq_pub_port = get_component_value(rec, ZMQ_PUB_PORT_FIELD)

        # Check that the user actually filled out the form
        if not instance:
            update = False

        if not ip_addr:
            update = False

        #elif not is_valid_ip_or_hostname(ip_addr):
        #    update = False

        if not rpc_bind_port:
            update = False

        if not zmq_pub_port:
            update = False

        if update:
            self.insert_one(rec)
        return rec

    def add_remote_p2pool_deployment(self, rec):
        update = True
        instance = get_component_value(rec, INSTANCE_FIELD)
        ip_addr = get_component_value(rec, IP_ADDR_FIELD)
        stratum_port = get_component_value(rec, STRATUM_PORT_FIELD)

        # Check that the user actually filled out the form
        if not instance:
            update = False

        if not ip_addr:
            update = False

        elif not is_valid_ip_or_hostname(ip_addr):
            update = False

        if not stratum_port:
            update = False

        if update:
            self.insert_one(rec)
        return rec        


    def add_xmrig_deployment(self, rec):
        update = True
        instance = get_component_value(rec, INSTANCE_FIELD)
        num_threads = get_component_value(rec, NUM_THREADS_FIELD)
        parent_id = get_component_value(rec, PARENT_ID_FIELD)
    
        # Check that the user filled out the form
        if not instance:
            update = False

        if not num_threads:
            update = False

        if not parent_id:
            update = False

        # MAke sure we don't inlcude the radio map
        if RADIO_MAP_FIELD in rec:
            rec.pop(RADIO_MAP_FIELD)

        # Generate a config file
        rec = self.conf_mgr.gen_xmrig_config(rec=rec, depl_mgr=self)

        if update:
            self.insert_one(rec)
        return rec


    def create_vendor_dir(self, new_dir: str, results: list):
        update_flag = True
        if os.path.exists(new_dir):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
            backup_vendor_dir = new_dir + '.' + timestamp
            try:
                os.rename(new_dir, backup_vendor_dir)
                results.append(result_row(
                    VENDOR_DIR_LABEL, WARN_FIELD, 
                    f"Found existing directory ({new_dir}), backed it up as ({backup_vendor_dir})"))
            except (PermissionError, OSError) as e:
                update_flag = False
                results.append(result_row(
                    VENDOR_DIR_LABEL, ERROR_FIELD, 
                    f"Unable to backup ({new_dir}) as ({backup_vendor_dir}), aborting deployment directory update:\n{e}"))
                return (update_flag, results)
            
        try:
            os.makedirs(new_dir)
            results.append(result_row(
                VENDOR_DIR_LABEL, GOOD_FIELD, 
                f"Created new {VENDOR_DIR_FIELD}: {new_dir}"))
        except (PermissionError, OSError) as e:
            results.append(result_row(
                VENDOR_DIR_LABEL, ERROR_FIELD, 
                f"Unable to create new {VENDOR_DIR_FIELD}: {new_dir}, aborting deployment directory update:\n{e}"))
            update_flag = False

        return (update_flag, results)


    def del_deployment(self, rec_data):
        elem_type = rec_data[ELEMENT_TYPE_FIELD]
        instance = rec_data[INSTANCE_FIELD]
        #print(f"DeploymentMgr:del_deployment(): {elem_type}/{instance}")

        self.db.delete_one(
            col_name=self.depl_col,
                filter = {
                    ELEMENT_TYPE_FIELD: elem_type,
                    COMPONENTS_FIELD: {
                        "$elemMatch": {
                            FIELD_FIELD: INSTANCE_FIELD,
                            VALUE_FIELD: instance
                        }
                    }
                }
        )
        rec = self.db.get_new_rec(elem_type)
        if elem_type == XMRIG_FIELD:
            rec[RADIO_MAP_FIELD] = gen_radio_map(rec=rec, depl_mgr=self)
        return rec
        
 
    def get_deployment(self, elem_type, instance=None):
        #print(f"DeploymentMgr:get_deployment(): {component}/{instance}")
        if elem_type == DB4E_FIELD or elem_type == DB4E_LABEL:
            rec = self.db.find_one(self.depl_col, {ELEMENT_TYPE_FIELD: DB4E_FIELD})
            # rec is a cursor object.
            if rec:
                return rec
            else:
                return {}
        else:
            rec = self.db.find_one(
                col_name = self.depl_col, 

                filter = {
                    ELEMENT_TYPE_FIELD: elem_type,
                    COMPONENTS_FIELD: {
                        "$elemMatch": {
                            FIELD_FIELD: INSTANCE_FIELD,
                            VALUE_FIELD: instance
                        }
                    }
                }
            )                
            #print(f"DeploymentMgr:get_deployment(): elem_type: {elem_type}, instance: {instance}, found: {rec}")

            if not rec:
                return {}
            return rec

        # No record for this deployment exists


    def get_deployment_by_id(self, id):
        return self.db.find_one(col_name=self.depl_col, filter={'_id': id})


    def get_deployment_ids_and_instances(self, elem_type):
        recs = self.db.find_many(
            self.depl_col, {ELEMENT_TYPE_FIELD: elem_type})
        result_list = []
        instance_list = []
        for rec in recs:            
            instance = get_component_value(rec, INSTANCE_FIELD)
            instance_list.append(instance)
            result_list.append((instance, rec[ID_FIELD]))
        result_list.sort()
        instance_list.sort()
        #print(f"DeploymentMgr:get_deployment_ids_and_instances(): {instance_list}")
        return result_list or []


    def get_deployments(self, component=None) -> list[dict]:
        query = {}
        if component is not None:
            query[COMPONENT_FIELD] = component
        results = self.db.find_many(self.depl_col, query)
        #print(f"DeploymentMgr:get_deployments(): {results}")
        return results
    

    def init_db(self):
        existing_rec = self.get_deployment(DB4E_FIELD)
        if existing_rec:
            return existing_rec
        
        rec = self.db.get_new_rec(DB4E_FIELD)
        # Use the effective UID/GID for the Db4E user/group
        effective_id = get_effective_identity()
        user = effective_id[USER_FIELD]
        group = effective_id[GROUP_FIELD]
        db4e_install_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        rec = update_component_values(rec, {
            USER_FIELD: user,
            GROUP_FIELD: group,
            INSTALL_DIR_FIELD: db4e_install_dir})
        self.insert_one(rec)
        return rec


    def insert_one(self, rec):
        ## Don't put the HEALTH_MSGS_FIELD (the status messages) into the DB
        # Pop off 
        if HEALTH_MSGS_FIELD in rec:
            status = rec.pop(HEALTH_MSGS_FIELD)
            self.db.insert_one(self.depl_col, rec)
            rec[HEALTH_MSGS_FIELD] = status
        return rec
        

    def is_initialized(self):
        rec = self.db.find_one(self.depl_col, {ELEMENT_TYPE_FIELD: DB4E_FIELD})
        if rec:
            vendor_dir = get_component_value(rec, VENDOR_DIR_FIELD)
            user_wallet = get_component_value(rec, USER_WALLET_FIELD)
            if vendor_dir and user_wallet:
                return True
            else:
                return False
        else:
            return False


    def update_deployment(self, rec):
        elem_type = rec[ELEMENT_TYPE_FIELD]
        if elem_type == DB4E_FIELD:
            return self.update_db4e_deployment(rec=rec)
        elif elem_type == MONEROD_FIELD:
            return self.update_monerod_deployment(rec=rec)
        elif elem_type == P2POOL_FIELD:
            return self.update_p2pool_deployment(rec=rec)
        elif elem_type == XMRIG_FIELD:
            return self.update_xmrig_deployment(rec=rec)


    def update_db4e_deployment(self, form_data):
        query = {ELEMENT_TYPE_FIELD: DB4E_FIELD}

        if FORM_DATA_FIELD in form_data:
            form_wallet = form_data[USER_WALLET_FIELD]
            form_vendor_dir = form_data[VENDOR_DIR_FIELD]
        else:
            form_wallet = get_component_value(form_data, USER_WALLET_FIELD)
            form_vendor_dir = get_component_value(form_data, VENDOR_DIR_FIELD)
        
        results = []
        update_flag = True
        rec = self.get_deployment(DB4E_FIELD)
        orig_user_wallet = get_component_value(rec, USER_WALLET_FIELD)
        orig_vendor_dir = get_component_value(rec, VENDOR_DIR_FIELD)

        #print(f"DeploymentMgr:update_db4e_deployment():")
        #print(f"  Old: {orig_user_wallet}/{orig_vendor_dir}")
        #print(f"  New: {form_wallet}/{form_vendor_dir}")

        if FORM_DATA_FIELD in form_data:

            ## Track field changes
            
            # Updating user wallet
            if orig_user_wallet != form_wallet:
                rec = set_component_value(rec, USER_WALLET_FIELD, form_wallet)
                self.update_one(query, rec)
                results.append(result_row(
                    USER_WALLET_LABEL, GOOD_FIELD, 
                    f"Set the Db4E user wallet: {form_wallet}"))

            # Updating vendor dir
            if orig_vendor_dir != form_vendor_dir:
                if not orig_vendor_dir:
                    update_flag, results = self.create_vendor_dir(
                        new_dir=form_vendor_dir,
                        results=results
                    )

                else:
                    update_flag, results = self.update_vendor_dir(
                        new_dir=form_vendor_dir,
                        old_dir=orig_vendor_dir,
                        results=results)

                rec = set_component_value(rec, VENDOR_DIR_FIELD, form_vendor_dir)

            #print(f"DeploymentMgr:update_db4e_deployment(): final rec: {rec}")
            if update_flag:
                self.update_one(query, rec)

            #print(f"DeploymentMgr:update_db4e_deployment():")
            return rec
        
        else:
            # If no FORM_DATA_FIELD, treat as direct DB update (system-side, not user form)
            self.update_one(query, rec)
            return rec


    def update_deployment(self, rec):
        #print(f"DeploymentMgr:update_deployment(): {rec}")
        elem_type = rec[ELEMENT_TYPE_FIELD]
        if elem_type == DB4E_FIELD:
            return self.update_db4e_deployment(rec)
        elif elem_type == MONEROD_FIELD:
            return self.update_monerod_deployment(rec)
        elif elem_type == MONEROD_REMOTE_FIELD:
            return self.update_monerod_remote_deployment(rec)
        elif elem_type == P2POOL_FIELD:
            return self.update_p2pool_deployment(rec)
        elif elem_type == P2POOL_REMOTE_FIELD:
            return self.update_p2pool_remote_deployment(rec)
        elif elem_type == XMRIG_FIELD:
            return self.update_xmrig_deployment(rec)
        else:
            raise ValueError(
                f"{DEPLOYMENT_MGR_FIELD}:update_deployment(): No handler for component " \
                f"({elem_type})")


    def update_monerod_deployment(self, rec):
        pass


    def update_monerod_remote_deployment(self, data):
        #print(f"DeploymentMgr:update_monerod_remote_deployment(): {data}")
        results = []
        update = False

        if FORM_DATA_FIELD in data:
            form_data = data

            rec = self.get_deployment(MONEROD_REMOTE_FIELD, form_data[ORIG_INSTANCE_FIELD])
            #print(f"DeploymentMgr:update_monerod_remote_deployment(): rec: {rec}")

            ## Field-by-field comparison

            # Instance
            form_orig_instance = form_data[ORIG_INSTANCE_FIELD]
            form_instance = form_data[INSTANCE_FIELD]
            #print(f"DeploymentMgr:update_monerod_remote_deployment(): {form_orig_instance}/{form_instance}")
            if form_instance != form_orig_instance:
                rec = set_component_value(rec, INSTANCE_FIELD, form_instance)            
                update = True

            # IP Address
            form_ip_addr = form_data[IP_ADDR_FIELD]
            db_ip_addr = get_component_value(rec, IP_ADDR_FIELD)
            if form_ip_addr != db_ip_addr:
                rec = set_component_value(rec, IP_ADDR_FIELD, form_ip_addr)
                update = True

            # RPC Bind Port
            form_rpc_bind_port = form_data[RPC_BIND_PORT_FIELD]
            db_rpc_bind_port = get_component_value(rec, RPC_BIND_PORT_FIELD)
            if form_rpc_bind_port != db_rpc_bind_port:
                rec = set_component_value(rec, RPC_BIND_PORT_FIELD, form_rpc_bind_port)
                update = True

            # ZMQ Pub Port
            form_zmq_pub_port = form_data[ZMQ_PUB_PORT_FIELD]
            db_zmq_pub_port = get_component_value(rec, ZMQ_PUB_PORT_FIELD)
            if form_zmq_pub_port != db_zmq_pub_port:
                rec = set_component_value(rec, ZMQ_PUB_PORT_FIELD, form_zmq_pub_port)
                update = True

            if update:
                query = {
                        ELEMENT_TYPE_FIELD: MONEROD_REMOTE_FIELD,
                        COMPONENTS_FIELD: {
                            "$elemMatch": {
                                FIELD_FIELD: INSTANCE_FIELD,
                                VALUE_FIELD: form_orig_instance,
                            }
                        }
                    }
                self.update_one(query, rec)
            else:
                results.append(result_row(
                    MONEROD_LABEL, WARN_FIELD,
                    f"{form_instance} – Nothing to update"
                ))
            return rec


    def update_one(self, query, rec):
        if HEALTH_MSGS_FIELD in rec:
            status = rec.pop(HEALTH_MSGS_FIELD)
            self.db.update_one(self.depl_col, query, rec)
            rec[HEALTH_MSGS_FIELD] = status
        else:
            self.db.update_one(self.depl_col, query, rec)

        return rec        

    def update_p2pool_deployment(self, data):
        pass


    def update_p2pool_remote_deployment(self, data):
        results = []
        update = False

        if FORM_DATA_FIELD in data:
            form_data = data
            rec = self.get_deployment(P2POOL_REMOTE_FIELD, form_data[ORIG_INSTANCE_FIELD])

            ## Field-by-field comparison            
            # Instance
            form_orig_instance = form_data[ORIG_INSTANCE_FIELD]
            form_instance = form_data[INSTANCE_FIELD]
            if form_instance != form_orig_instance:
                rec = set_component_value(rec, INSTANCE_FIELD, form_instance)
                update = True

            # IP Address
            form_ip_addr = form_data[IP_ADDR_FIELD]
            db_ip_addr = get_component_value(rec, IP_ADDR_FIELD)
            if form_ip_addr != db_ip_addr:
                rec = set_component_value(rec, IP_ADDR_FIELD, form_ip_addr)
                update = True

            # Stratum Port
            form_stratum_port = form_data[STRATUM_PORT_FIELD]
            db_stratum_port = get_component_value(rec, STRATUM_PORT_FIELD)
            if form_stratum_port != db_stratum_port:
                rec = set_component_value(rec, STRATUM_PORT_FIELD, form_stratum_port)
                update = True

            if update:
                query = {
                        ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                        COMPONENTS_FIELD: {
                            "$elemMatch": {
                                FIELD_FIELD: INSTANCE_FIELD,
                                VALUE_FIELD: form_orig_instance,
                            }
                        }
                    }
                self.update_one(query, rec)
                
            else:
                results.append(result_row(
                    P2POOL_LABEL, WARN_FIELD,
                    f"{form_instance} – Nothing to update"
                ))
            return rec


    def update_vendor_dir(self, new_dir: str, old_dir: str, results: list):
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
                results.append(result_row(
                    VENDOR_DIR_LABEL, WARN_FIELD, 
                    f'Found existing directory ({new_dir}), backed it up as ({backup_vendor_dir})'))
                return (update_flag, results)
            except (PermissionError, OSError) as e:
                update_flag = False
                results.append(result_row(
                    VENDOR_DIR_LABEL, ERROR_FIELD, 
                    f'Unable to backup ({new_dir}) as ({backup_vendor_dir}), aborting deployment directory update:\n{e}'))
                return (update_flag, results)

        # No need to move if old_dir is empty (first-time initialization)
        if not old_dir:
            results.append(result_row(
                VENDOR_DIR_LABEL, GOOD_FIELD,
                f"Created new {VENDOR_DIR_FIELD}: {new_dir}"))
            return (update_flag, results)
        
        # Move the vendor_dir to the new location
        try:
            os.rename(old_dir, new_dir)
            results.append(result_row(
                VENDOR_DIR_LABEL, GOOD_FIELD, 
                f'Moved vendor dir from ({old_dir}) to ({new_dir})'))
        except (PermissionError, OSError) as e:
            results.append(result_row(
                VENDOR_DIR_LABEL, ERROR_FIELD, 
                f'Unable to move vendor dir from ({old_dir}) to ({new_dir}), aborting deployment directory update:\n{e}'))
            update_flag = False

        #print(f"DeploymentMgr:update_vendor_dir(): results: {results}")
        return (update_flag, results)


    def update_xmrig_deployment(self, data):
        #print(f"DeploymentMgr:update_xmrig_deployment(): {data}")
        update = False
        update_config = False

        if FORM_DATA_FIELD in data:
            form_data = data
            rec = self.get_deployment(XMRIG_FIELD, form_data[ORIG_INSTANCE_FIELD])

            ## Field-by-field comparison
            # Instance
            form_orig_instance = form_data[ORIG_INSTANCE_FIELD]
            form_instance = form_data[INSTANCE_FIELD]
            if form_instance != form_orig_instance:
                update = True
                update_config = True
                rec = set_component_value(rec, INSTANCE_FIELD, form_instance)

            # Num Threads
            form_num_threads = form_data[NUM_THREADS_FIELD]
            db_num_threads = get_component_value(rec, NUM_THREADS_FIELD)
            if form_num_threads != db_num_threads:
                update = True
                update_config = True
                rec = set_component_value(rec, NUM_THREADS_FIELD, form_num_threads)

            # Parent ID
            form_parent_id = form_data[PARENT_ID_FIELD]
            db_parent_id = get_component_value(rec, PARENT_ID_FIELD)
            if form_parent_id != db_parent_id:
                update = True
                update_config = True
                rec = set_component_value(rec, PARENT_ID_FIELD, form_parent_id)

            # Regenerate config if required
            if update_config:
                config_file = get_component_value(rec, CONFIG_FIELD)
                if config_file:
                    self.conf_mgr.del_config(config_file=config_file)
                rec = self.conf_mgr.gen_xmrig_config(rec=rec, depl_mgr=self)

            if update:
                query = {
                        ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                        COMPONENTS_FIELD: {
                            "$elemMatch": {
                                FIELD_FIELD: INSTANCE_FIELD,
                                VALUE_FIELD: form_orig_instance,
                            }
                        }
                    }
                self.update_one(query, rec)
            return rec
        else:
            raise ValueError("DeploymentMgr:update_xmrig_deployment(): Missing FORM_DATA_FIELD")
