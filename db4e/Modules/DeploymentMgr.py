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
    result_row, is_valid_ip_or_hostname, get_component_value, set_component_value,
    gen_radio_set)
from db4e.Constants.Fields import *
from db4e.Constants.Labels import (
    DB4E_LABEL, INSTANCE_LABEL, IP_ADDR_LABEL, MONEROD_LABEL, MONEROD_REMOTE_LABEL,
    NUM_THREADS_LABEL, P2POOL_LABEL, RPC_BIND_PORT_LABEL,
    STRATUM_PORT_LABEL, USER_WALLET_LABEL, VENDOR_DIR_LABEL, XMRIG_LABEL,
    ZMQ_PUB_PORT_LABEL,
)
from db4e.Constants.Fields import (
    ACTIVE_FIELD, COMPONENT_FIELD, CONFIG_FIELD, DB4E_FIELD, DEPLOYMENT_TYPE_FIELD,
    ERROR_FIELD, FORM_DATA_FIELD, GOOD_FIELD, GROUP_FIELD, ID_FIELD, INSTALL_DIR_FIELD,
    INSTANCE_FIELD, IP_ADDR_FIELD, MONEROD_FIELD, MONEROD_REMOTE_FIELD, NUM_THREADS_FIELD,
    ORIG_INSTANCE_FIELD, P2POOL_FIELD, P2POOL_REMOTE_FIELD, PARENT_ID_FIELD, PYTHON_FIELD,
    REMOTE_FIELD, RESULTS_FIELD, RPC_BIND_PORT_FIELD, STATUS_FIELD, STRATUM_PORT_FIELD,
    TEMPLATE_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD, UPDATED_FIELD, USER_FIELD,
    USER_WALLET_FIELD, VENDOR_DIR_FIELD, VERSION_FIELD, WARN_FIELD, XMRIG_FIELD,
    ZMQ_PUB_PORT_FIELD, ELEMENT_TYPE_FIELD
)
from db4e.Constants.Defaults import (
    BIN_DIR_DEFAULT, DEPLOYMENT_COL_DEFAULT, PYTHON_DEFAULT, TEMPLATES_DIR_DEFAULT,
)
                                     
class DeploymentMgr(Container):
    
    def __init__(self, config: Config):
        super().__init__()
        self.ini = config
        self.conf_mgr = ConfigMgr(app_version='UNUSED')
        self.db = DbMgr(config)
        self.col_name = DEPLOYMENT_COL_DEFAULT
        self.db4e_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def add_deployment(self, rec):
        print(f"DeploymentMgr:add_deployment(): {rec}")
        results = []
        fatal_error = False
        elem_type = rec[ELEMENT_TYPE_FIELD]

        # Add the Db4E Core deployment
        if elem_type == DB4E_FIELD:
            return self.add_db4e_deployment(rec)

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

    def add_db4e_deployment(self, rec):
        self.db.insert_one(self.col_name, rec)
        return rec

    def add_monerod_deployment(self, rec):
        print(f"DeploymentMgr:add_remote_monerod_deployment(): {rec}")
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
            self.db.insert_one(self.col_name, rec)
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
            self.db.insert_one(self.col_name, rec)
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

        if update:
            self.db.insert_one(self.col_name, rec)
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
        print(f"DeploymentMgr:del_deployment(): {rec_data}")
        elem_type = rec_data[ELEMENT_TYPE_FIELD]
        instance = rec_data[INSTANCE_FIELD]

        self.db.delete_one(
            col_name=self.col_name,
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
            rec[RADIO_MAP_FIELD] = gen_radio_set(rec=rec, depl_mgr=self)
            rec[P2POOL_INSTANCE] = ""
        return rec

        
 
    def get_deployment(self, elem_type, instance=None):
        #print(f"DeploymentMgr:get_deployment(): {component}/{instance}")
        if elem_type == DB4E_FIELD or elem_type == DB4E_LABEL:
            db_rec = self.db.find_one(self.col_name, {ELEMENT_TYPE_FIELD: DB4E_FIELD})
            # rec is a cursor object.
            if db_rec:
                return db_rec
            else:
                return {}
        else:
            rec = self.db.find_one(
                col_name = self.col_name, 

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
            print(f"DeploymentMgr:get_deployment(): elem_type: {elem_type}, instance: {instance}, found: {rec}")

            if not rec:
                return {}
            return rec

        # No record for this deployment exists

    def get_deployment_by_id(self, id):
        return self.db.find_one(col_name=self.col_name, filter={'_id': id})

    def get_deployment_ids_and_instances(self, elem_type):
        db_recs = self.db.find_many(
            self.col_name, {ELEMENT_TYPE_FIELD: elem_type})
        result_list = []
        for db_rec in db_recs:
            print(f"DeploymentMgr:get_deployment_ids_and_instances(): {db_rec}")
            instance = get_component_value(db_rec, INSTANCE_FIELD)
            result_list.append((instance, db_rec[ID_FIELD]))
        result_list.sort()
        return result_list or []

    def get_deployments(self, component=None) -> list[dict]:
        query = {}
        if component is not None:
            query[COMPONENT_FIELD] = component
        results = self.db.find_many(self.col_name, query)
        #print(f"DeploymentMgr:get_deployments(): {results}")
        return results
        
    def is_initialized(self):
        rec = self.db.find_one(self.col_name, {ELEMENT_TYPE_FIELD: DB4E_FIELD})
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
        component = rec[COMPONENT_FIELD]
        if component == DB4E_FIELD:
            return self.update_db4e_deployment(rec=rec)
        elif component == MONEROD_FIELD:
            return self.update_monerod_deployment(rec=rec)
        elif component == P2POOL_FIELD:
            return self.update_p2pool_deployment(rec=rec)
        elif component == XMRIG_FIELD:
            return self.update_xmrig_deployment(rec=rec)

    def update_db4e_deployment(self, rec):
        results = []
        update_flag = False
        filter = {ELEMENT_TYPE_FIELD: DB4E_FIELD}
        orig_rec = self.get_deployment(DB4E_FIELD)

        if FORM_DATA_FIELD in rec:
            # Remove frontend-only fields
            rec.pop(FORM_DATA_FIELD, None)
            rec.pop(TO_MODULE_FIELD, None)
            rec.pop(TO_METHOD_FIELD, None)

            ## Track field changes
            
            # Updating user wallet
            if rec[USER_WALLET_FIELD] != orig_rec[USER_WALLET_FIELD]:
                update_flag = True
                results.append(result_row(
                    f"[bold]{USER_WALLET_LABEL}[/]", GOOD_FIELD,
                    f"Updated {USER_WALLET_LABEL} ({orig_rec[USER_WALLET_FIELD][6:]}... > " \
                    f"{rec[USER_WALLET_FIELD][6:]}...) in {DB4E_LABEL} deployment record"
                ))

            # Updating vendor dir
            if rec[VENDOR_DIR_FIELD] != orig_rec[VENDOR_DIR_FIELD]:
                update_flag = True
                if not rec[VENDOR_DIR_FIELD]:
                    update_flag, results = self.create_vendor_dir(
                        new_dir=rec[VENDOR_DIR_FIELD],
                        results=results
                    )

                else:
                    update_flag, results = self.update_vendor_dir(
                        new_dir=rec[VENDOR_DIR_FIELD],
                        old_dir=orig_rec[VENDOR_DIR_FIELD],
                        results=results)

            rec[HEALTH_MSGS_FIELD] += results
            if update_flag:
                self.db.update_one(self.col_name, filter, rec)
            else:
                results.append(result_row(
                    DB4E_LABEL, WARN_FIELD,
                    "Nothing to update"
                ))
            print(f"DeploymentMgr:update_db4e_deployment(): results: {results}")
            return rec
        
        else:
            # If no FORM_DATA_FIELD, treat as direct DB update (system-side, not user form)
            self.db.update_one(self.col_name, filter, rec)
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
        print(f"DeploymentMgr:update_monerod_remote_deployment(): {data}")
        results = []
        update = False

        if FORM_DATA_FIELD in data:
            form_data = data

            db_rec = self.get_deployment(MONEROD_REMOTE_FIELD, form_data[ORIG_INSTANCE_FIELD])
            #print(f"DeploymentMgr:update_monerod_remote_deployment(): db_rec: {db_rec}")

            ## Field-by-field comparison

            # Instance
            form_orig_instance = form_data[ORIG_INSTANCE_FIELD]
            form_instance = form_data[INSTANCE_FIELD]
            #print(f"DeploymentMgr:update_monerod_remote_deployment(): {form_orig_instance}/{form_instance}")
            if form_instance != form_orig_instance:
                db_rec = set_component_value(db_rec, INSTANCE_FIELD, form_instance)            
                update = True

            # IP Address
            form_ip_addr = form_data[IP_ADDR_FIELD]
            db_ip_addr = get_component_value(db_rec, IP_ADDR_FIELD)
            if form_ip_addr != db_ip_addr:
                db_rec = set_component_value(db_rec, IP_ADDR_FIELD, form_ip_addr)
                update = True

            # RPC Bind Port
            form_rpc_bind_port = form_data[RPC_BIND_PORT_FIELD]
            db_rpc_bind_port = get_component_value(db_rec, RPC_BIND_PORT_FIELD)
            if form_rpc_bind_port != db_rpc_bind_port:
                db_rec = set_component_value(db_rec, RPC_BIND_PORT_FIELD, form_rpc_bind_port)
                update = True

            # ZMQ Pub Port
            form_zmq_pub_port = form_data[ZMQ_PUB_PORT_FIELD]
            db_zmq_pub_port = get_component_value(db_rec, ZMQ_PUB_PORT_FIELD)
            if form_zmq_pub_port != db_zmq_pub_port:
                db_rec = set_component_value(db_rec, ZMQ_PUB_PORT_FIELD, form_zmq_pub_port)
                update = True

            if update:
                self.db.update_one(
                    col_name=self.col_name,
                    filter = {
                        ELEMENT_TYPE_FIELD: MONEROD_REMOTE_FIELD,
                        COMPONENTS_FIELD: {
                            "$elemMatch": {
                                FIELD_FIELD: INSTANCE_FIELD,
                                VALUE_FIELD: form_orig_instance,
                            }
                        }
                    },
                    new_values=db_rec,
                )
            else:
                results.append(result_row(
                    MONEROD_LABEL, WARN_FIELD,
                    f"{form_instance} – Nothing to update"
                ))
            return db_rec

      
    def update_p2pool_deployment(self, data):
        pass

    def update_p2pool_remote_deployment(self, data):
        results = []
        update = False

        if FORM_DATA_FIELD in data:
            form_data = data
            db_rec = self.get_deployment(P2POOL_REMOTE_FIELD, form_data[ORIG_INSTANCE_FIELD])

            ## Field-by-field comparison            
            # Instance
            form_orig_instance = form_data[ORIG_INSTANCE_FIELD]
            form_instance = form_data[INSTANCE_FIELD]
            if form_instance != form_orig_instance:
                db_rec = set_component_value(db_rec, INSTANCE_FIELD, form_instance)
                update = True

            # IP Address
            form_ip_addr = form_data[IP_ADDR_FIELD]
            db_ip_addr = get_component_value(db_rec, IP_ADDR_FIELD)
            if form_ip_addr != db_ip_addr:
                db_rec = set_component_value(db_rec, IP_ADDR_FIELD, form_ip_addr)
                update = True

            # Stratum Port
            form_stratum_port = form_data[STRATUM_PORT_FIELD]
            db_stratum_port = get_component_value(db_rec, STRATUM_PORT_FIELD)
            if form_stratum_port != db_stratum_port:
                db_rec = set_component_value(db_rec, STRATUM_PORT_FIELD, form_stratum_port)
                update = True

            if update:
                self.db.update_one(
                    col_name=self.col_name,
                    filter = {
                        ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                        COMPONENTS_FIELD: {
                            "$elemMatch": {
                                FIELD_FIELD: INSTANCE_FIELD,
                                VALUE_FIELD: form_orig_instance,
                            }
                        }
                    },
                    new_values=db_rec,
                )
            else:
                results.append(result_row(
                    P2POOL_LABEL, WARN_FIELD,
                    f"{form_instance} – Nothing to update"
                ))
            return db_rec

    def update_vendor_dir(self, new_dir: str, old_dir: str, results: list):
        print(f"DeploymentMgr:update_vendor_dir(): {old_dir} > {new_dir}")
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

        print(f"DeploymentMgr:update_vendor_dir(): results: {results}")
        return (update_flag, results)

    def update_xmrig_deployment(self, rec):
        results = []
        update_flag = False
        update_config_flag = False

        # Strip frontend metadata
        rec.pop(TO_MODULE_FIELD, None)
        rec.pop(TO_METHOD_FIELD, None)

        # Required field
        orig_instance = rec[ORIG_INSTANCE_FIELD]
        orig_rec = self.get_deployment(XMRIG_FIELD, orig_instance)

        # Compare + apply updates
        if rec[INSTANCE_FIELD] != orig_rec[INSTANCE_FIELD]:
            update_flag = True
            update_config_flag = True
            results.append(result_row(
                INSTANCE_LABEL, GOOD_FIELD,
                f"Updated {INSTANCE_LABEL} in {XMRIG_LABEL} deployment record"
            ))

        if rec[NUM_THREADS_FIELD] != orig_rec[NUM_THREADS_FIELD]:
            update_flag = True
            update_config_flag = True
            results.append(result_row(
                NUM_THREADS_LABEL, GOOD_FIELD,
                f"Updated {NUM_THREADS_LABEL} in {XMRIG_LABEL} deployment record"
            ))

        if rec[PARENT_ID_FIELD] != orig_rec[PARENT_ID_FIELD]:
            update_flag = True
            update_config_flag = True
            results.append(result_row(
                P2POOL_LABEL, GOOD_FIELD,
                f"Updated {P2POOL_LABEL} in {XMRIG_LABEL} deployment record"
            ))
            rec[PARENT_ID_FIELD] = rec[PARENT_ID_FIELD]

        # Regenerate config if required
        if update_config_flag:
            results = self.conf_mgr.del_config(
                config_file=rec[CONFIG_FIELD], results=results)
            results, conf_file = self.conf_mgr.gen_xmrig_config(
                rec=rec, depl_mgr=self, results=results)
            rec[CONFIG_FIELD] = conf_file

        rec[HEALTH_MSGS_FIELD] += results
        rec.pop(ORIG_INSTANCE_FIELD)

        if update_flag:
            self.db.update_one(
                col_name=self.col_name,
                filter={COMPONENT_FIELD: XMRIG_FIELD, INSTANCE_FIELD: orig_instance},
                new_values=rec
            )
        else:
            rec[HEALTH_MSGS_FIELD] += result_row(
                XMRIG_LABEL, WARN_FIELD,
                f"{orig_instance} – Nothing to update"
            )
        return rec
      
