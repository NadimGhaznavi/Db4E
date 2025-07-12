"""
db4e/Modules/DeploymentManager.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

import os, shutil
from datetime import datetime, timezone
import getpass

from textual.containers import Container

from db4e.Modules.ConfigMgr import Config
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.Helper import result_row
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Labels import (
    DB4E_LABEL, DEPLOYMENT_MGR_LABEL, DEPLOYMENT_DIR_LABEL, INSTANCE_LABEL, 
    IP_ADDR_LABEL, MONERO_WALLET_LABEL,  MONEROD_LABEL, MONEROD_REMOTE_LABEL, 
    P2POOL_LABEL, P2POOL_REMOTE_LABEL, RPC_BIND_PORT_LABEL, STRATUM_PORT_LABEL, 
    ZMQ_PUB_PORT_LABEL)
from db4e.Constants.Fields import (
    DB4E_FIELD, DOC_TYPE_FIELD, COMPONENT_FIELD, DEPLOYMENT_FIELD, 
    DEPLOYMENT_TYPE_FIELD, ERROR_FIELD, FORM_DATA_FIELD, GOOD_FIELD, 
    GROUP_FIELD, INSTALL_DIR_FIELD, INSTANCE_FIELD, IP_ADDR_FIELD, 
    MONEROD_FIELD, MONEROD_REMOTE_FIELD, ORIG_INSTANCE_FIELD, 
    P2POOL_FIELD, P2POOL_REMOTE_FIELD, REMOTE_FIELD, RPC_BIND_PORT_FIELD, 
    STRATUM_PORT_FIELD, TO_MODULE_FIELD, TO_METHOD_FIELD, 
    UPDATED_FIELD, USER_FIELD, USER_WALLET_FIELD, VENDOR_DIR_FIELD, 
    VERSION_FIELD, WARN_FIELD, ZMQ_PUB_PORT_FIELD)
from db4e.Constants.Defaults import DEPLOYMENT_COL_DEFAULT


class DeploymentMgr(Container):
    
    def __init__(self, config: Config):
        super().__init__()
        self.ini = config
        self.db = DbMgr(config)
        self.col_name = DEPLOYMENT_COL_DEFAULT
        self.db4e_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def add_remote_monerod_deployment(self, rec):
        results = []
        fatal_error = False
        # Check that the user actually filled out the form
        if not rec[INSTANCE_FIELD]:
            results.append(result_row(
                INSTANCE_LABEL, ERROR_FIELD,
                f"Missing required field: {INSTANCE_LABEL}"
            ))
            fatal_error = True
        if not rec[IP_ADDR_FIELD]:
            results.append(result_row(
                IP_ADDR_LABEL, ERROR_FIELD,
                f"Missing required field: {IP_ADDR_LABEL}"
            ))
            fatal_error = True
        if not rec[RPC_BIND_PORT_FIELD]:
            results.append(result_row(
                RPC_BIND_PORT_LABEL, ERROR_FIELD,
                f"Missing required field: {RPC_BIND_PORT_LABEL}"
            ))
            fatal_error = True
        if not rec[ZMQ_PUB_PORT_FIELD]:
            results.append(result_row(
                ZMQ_PUB_PORT_LABEL, ERROR_FIELD,
                f"Missing required field: {ZMQ_PUB_PORT_LABEL}"
            ))
            fatal_error = True
        component_label = MONEROD_REMOTE_LABEL
        instance = rec[INSTANCE_FIELD]
        if fatal_error:
            return (rec, component_label, instance, fatal_error)
        db_rec = self.get_new_rec({COMPONENT_FIELD: MONEROD_REMOTE_FIELD})
        db_rec[UPDATED_FIELD] = rec[UPDATED_FIELD]
        db_rec[INSTANCE_FIELD] = rec[INSTANCE_FIELD]
        db_rec[IP_ADDR_FIELD] = rec[IP_ADDR_FIELD]
        db_rec[RPC_BIND_PORT_FIELD] = rec[RPC_BIND_PORT_FIELD]
        db_rec[ZMQ_PUB_PORT_FIELD] = rec[ZMQ_PUB_PORT_FIELD]
        db_rec[VERSION_FIELD] = self.ini.config[rec[COMPONENT_FIELD]][VERSION_FIELD]
        rec = db_rec
        return (rec, component_label, instance, results, fatal_error)

    def add_remote_p2pool_deployment(self, rec):
        results = []
        fatal_error = False
        # Check that the user actually filled out the form
        if not rec[INSTANCE_FIELD]:
            results.append(result_row(
                INSTANCE_LABEL, ERROR_FIELD,
                f"Missing required field: {INSTANCE_LABEL}"
            ))
            fatal_error = True
        if not rec[IP_ADDR_FIELD]:
            results.append(result_row(
                IP_ADDR_LABEL, ERROR_FIELD,
                f"Missing required field: {IP_ADDR_LABEL}"
            ))
            fatal_error = True
        if not rec[STRATUM_PORT_FIELD]:
            results.append(result_row(
                STRATUM_PORT_LABEL, ERROR_FIELD,
                f"Missing required field: {STRATUM_PORT_LABEL}"
            ))
            fatal_error = True
        component_label = P2POOL_REMOTE_LABEL
        instance = rec[INSTANCE_FIELD]
        if fatal_error:
            return (rec, component_label, instance, results, fatal_error)
        db_rec = self.get_new_rec({COMPONENT_FIELD: P2POOL_REMOTE_FIELD})
        db_rec[UPDATED_FIELD] = rec[UPDATED_FIELD]
        db_rec[INSTANCE_FIELD] = rec[INSTANCE_FIELD]
        db_rec[IP_ADDR_FIELD] = rec[IP_ADDR_FIELD]
        db_rec[STRATUM_PORT_FIELD] = rec[STRATUM_PORT_FIELD]
        db_rec[VERSION_FIELD] = self.ini.config[rec[COMPONENT_FIELD]][VERSION_FIELD]
        rec = db_rec
        return (rec, component_label, instance, results, fatal_error)

    def add_deployment(self, rec):
        #print(f"DeploymentMgr:add_deployment(): {rec}")
        results = []
        fatal_error = False
        rec[DOC_TYPE_FIELD] = DEPLOYMENT_FIELD
        rec[UPDATED_FIELD] = datetime.now(timezone.utc)

        # Add a Monero daemon deployment
        if rec[COMPONENT_FIELD] == MONEROD_FIELD:
            if rec[REMOTE_FIELD]: # Remote deployment
                (rec, component_label, instance, results,
                fatal_error) = self.add_remote_monerod_deployment(rec)
                if fatal_error:
                    return results
            else: # Local deployment
                results.append(result_row(
                    MONEROD_REMOTE_LABEL, WARN_FIELD,
                    f"🚧 {MONEROD_REMOTE_FIELD} deployment coming soon 🚧"
                ))
                return results
        
        # Add a P2Pool deployment
        elif rec[COMPONENT_FIELD] == P2POOL_FIELD:
            if rec[REMOTE_FIELD]: # Remote deployment
                (rec, component_label, instance, results,
                fatal_error) = self.add_remote_p2pool_deployment(rec)
                if fatal_error:
                    return results
            else: # Local deployment
                results.append(result_row(
                    P2POOL_LABEL, WARN_FIELD,
                    f"🚧 {P2POOL_LABEL} deployment coming soon 🚧"
                ))
                return results

        self.db.insert_one(self.col_name, rec)
        if instance:
            results_message = f"Added new {component_label} deployment record ({instance})"
        else:
            results_message = f"Added new {component_label} deployment record"
        results.append(result_row(
            DB4E_LABEL, GOOD_FIELD, results_message))
        return results
        #self.post_message(RefreshNavPane(self))

    def del_deployment(self, rec_data):
        component = rec_data[COMPONENT_FIELD]
        instance = rec_data[INSTANCE_FIELD]
        self.db.delete_one(
            self.col_name, {COMPONENT_FIELD: component, INSTANCE_FIELD: instance})
        return [(result_row(DB4E_LABEL, GOOD_FIELD, "Deleted deployment record"))]

    def is_initialized(self):
        rec = self.db.find_one(self.col_name, {COMPONENT_FIELD: DB4E_FIELD})
        if rec:
            print("DeploymentMgr:is_initialized(): True")
            return True
        else:
            print("DeploymentMgr:is_initialized(): False")
            return False

    def get_deployment(self, component):
        #print(f"DeploymentMgr:get_deployment(): {component}")
        # Ask the db for the component record
        db_rec = self.db.find_one(self.col_name, {COMPONENT_FIELD: component})
        # rec is a cursor object.
        if db_rec:
            rec = {}
            component = db_rec[COMPONENT_FIELD]
            if component == DB4E_FIELD:
                rec[COMPONENT_FIELD] = component
                rec[GROUP_FIELD] = db_rec[GROUP_FIELD]
                rec[INSTALL_DIR_FIELD] = db_rec[INSTALL_DIR_FIELD]
                rec[USER_FIELD] = db_rec[USER_FIELD]
                rec[USER_WALLET_FIELD] = db_rec[USER_WALLET_FIELD]
                rec[VENDOR_DIR_FIELD] = db_rec[VENDOR_DIR_FIELD]
            #print(f"DeploymentMgr:get_deployment(): {component} > {db_rec} > {rec}")
            return rec
        return None
        # No record for this deployment exists
        
    def get_deployment_by_instance(self, component, instance):
        #print(f"DeploymentMgr:get_deployment_by_instance(): {component}/{instance}")
        if instance == DB4E_LABEL:
            return self.get_deployment(DB4E_FIELD)
        elif component == MONEROD_FIELD:
            return self.db.find_one(
                col_name=self.col_name, 
                filter={COMPONENT_FIELD: MONEROD_FIELD, INSTANCE_FIELD: instance})
        elif component == P2POOL_FIELD:
            return self.db.find_one(
                col_name=self.col_name,
                filter={COMPONENT_FIELD: P2POOL_FIELD, INSTANCE_FIELD: instance})

    def get_deployment_instances(self, component):
        db_recs = self.db.find_many(
            self.col_name, {COMPONENT_FIELD: component})
        instance_list = []
        for db_rec in db_recs:
            instance_list.append(db_rec[INSTANCE_FIELD])
        instance_list.sort()
        return instance_list
        
    def get_new_rec(self, rec_data):
        component = rec_data.get(COMPONENT_FIELD)
        is_remote = rec_data.get(REMOTE_FIELD, False)
        key_map = {
            (MONEROD_FIELD, True): MONEROD_REMOTE_FIELD,
            (MONEROD_FIELD, False): MONEROD_FIELD,
            (P2POOL_FIELD, True): P2POOL_REMOTE_FIELD,
            (P2POOL_FIELD, False): P2POOL_FIELD,
        }
        record_key = key_map.get((component, is_remote), component)
        return self.db.get_new_rec(record_key)

    def new_deployment(self, form_data):
        #print(f"DeploymentMgr:new_deployment(): {form_data}")
        if form_data[DEPLOYMENT_TYPE_FIELD] == "new_monerod_type_monerod":
            return {'type': 'local'}
        elif form_data[DEPLOYMENT_TYPE_FIELD] == "new_monerod_type_remote_monerod":
            return self.get_new_rec(MONEROD_REMOTE_FIELD)

    def update_db4e_deployment(self, update_data):
        results = []
        update_flag = False
        filter = {DOC_TYPE_FIELD: DEPLOYMENT_FIELD, COMPONENT_FIELD: DB4E_FIELD}
        if FORM_DATA_FIELD in update_data:
            del update_data[FORM_DATA_FIELD]
            del update_data[TO_MODULE_FIELD]
            del update_data[TO_METHOD_FIELD]
            db4e_rec = self.get_deployment(DB4E_FIELD)
            if not update_data[USER_WALLET_FIELD]:
                results.append(result_row(
                    MONERO_WALLET_LABEL, ERROR_FIELD,
                    f"Missing {MONERO_WALLET_LABEL}"
                ))
            elif update_data[USER_WALLET_FIELD] != db4e_rec[USER_WALLET_FIELD]:
                update_flag = True
                results.append(result_row(
                    MONERO_WALLET_LABEL, GOOD_FIELD, 
                    f"Updated {MONERO_WALLET_LABEL} in {DB4E_LABEL} deployment record"))
            if not update_data[VENDOR_DIR_FIELD]:
                results.append(result_row(
                    DEPLOYMENT_DIR_LABEL, ERROR_FIELD,
                    f"Missing {DEPLOYMENT_DIR_LABEL}"
                ))
            elif update_data[VENDOR_DIR_FIELD] != db4e_rec[VENDOR_DIR_FIELD]:
                update_flag = True
                results.append(result_row(
                    DEPLOYMENT_DIR_LABEL, GOOD_FIELD, 
                    f"Updated {DEPLOYMENT_DIR_LABEL} in {DB4E_LABEL} deployment record"))
            if update_flag:
                self.db.update_one(
                    col_name=self.col_name, filter=filter, new_values=update_data)
            else:
                results.append(result_row(
                    DB4E_LABEL, WARN_FIELD,
                    "Nothing to update"
                ))
            return results
        else:
            self.db.update_one(self.col_name, filter, update_data)

    def update_deployment(self, update_data):
        if update_data[COMPONENT_FIELD] == DB4E_FIELD:
            return self.update_db4e_deployment(update_data=update_data)
        elif update_data[COMPONENT_FIELD] == MONEROD_FIELD:
            return self.update_monerod_deployment(update_data=update_data)
        elif update_data[COMPONENT_FIELD] == P2POOL_FIELD:
            return self.update_p2pool_deployment(update_data=update_data)
        else:
            results = []
            results.append(result_row(
                DEPLOYMENT_MGR_LABEL, ERROR_FIELD,
                f"{DEPLOYMENT_MGR_LABEL}:update_deployment(): No handler for component ({update_data[COMPONENT_FIELD]})"
            ))
            return results

    def update_monerod_deployment(self, update_data):
        results = []
        update_flag = False
        if FORM_DATA_FIELD in update_data:
            del update_data[FORM_DATA_FIELD]
            del update_data[TO_MODULE_FIELD]
            del update_data[TO_METHOD_FIELD]
            orig_instance = update_data[ORIG_INSTANCE_FIELD]
            monerod_rec = self.get_deployment_by_instance(
                MONEROD_FIELD, update_data[ORIG_INSTANCE_FIELD])
            print(f"DeploymentMgr:update_monerod_deployment() {monerod_rec}")
            if update_data[INSTANCE_FIELD] != monerod_rec[INSTANCE_FIELD]:
                update_flag = True
                results.append(result_row(
                    INSTANCE_LABEL, GOOD_FIELD,
                    f"Updated {INSTANCE_LABEL} in {MONEROD_LABEL} deployment record"))
            if update_data[IP_ADDR_FIELD] != monerod_rec[IP_ADDR_FIELD]:
                update_flag = True
                results.append(result_row(
                    IP_ADDR_LABEL, GOOD_FIELD,
                    f"Updated {IP_ADDR_LABEL} in {MONEROD_LABEL} deployment record"))
            if update_data[RPC_BIND_PORT_FIELD] != monerod_rec[RPC_BIND_PORT_FIELD]:
                update_flag = True
                results.append(result_row(
                    RPC_BIND_PORT_LABEL, GOOD_FIELD,
                    f"Updated {RPC_BIND_PORT_LABEL} in {MONEROD_LABEL} deployment record"))
            if update_data[ZMQ_PUB_PORT_FIELD] != monerod_rec[ZMQ_PUB_PORT_FIELD]:
                update_flag = True
                results.append(result_row(
                    ZMQ_PUB_PORT_LABEL, GOOD_FIELD,
                    f"Updated {ZMQ_PUB_PORT_LABEL} in {MONEROD_LABEL} deployment record"))
            if update_flag:
                self.db.update_one(
                    filter={COMPONENT_FIELD: MONEROD_FIELD, INSTANCE_FIELD: orig_instance},
                    col_name=self.col_name, new_values=update_data)
            else:
                results.append(result_row(
                    MONEROD_LABEL, WARN_FIELD,
                    "Nothing to update"
                ))
                return results
            return results
      
    def update_p2pool_deployment(self, update_data):
        results = []
        update_flag = False
        if FORM_DATA_FIELD in update_data:
            del update_data[FORM_DATA_FIELD]
            del update_data[TO_MODULE_FIELD]
            del update_data[TO_METHOD_FIELD]
            orig_instance = update_data[ORIG_INSTANCE_FIELD]
            p2pool_rec = self.get_deployment_by_instance(
                P2POOL_FIELD, update_data[ORIG_INSTANCE_FIELD])
            #print(f"DeploymentMgr:update_p2pool_deployment() {p2pool_rec}")
            if update_data[INSTANCE_FIELD] != p2pool_rec[INSTANCE_FIELD]:
                update_flag = True
                results.append(result_row(
                    INSTANCE_LABEL, GOOD_FIELD,
                    f"Updated {INSTANCE_LABEL} in {P2POOL_LABEL} deployment record"))
            if update_data[IP_ADDR_FIELD] != p2pool_rec[IP_ADDR_FIELD]:
                update_flag = True
                results.append(result_row(
                    IP_ADDR_LABEL, GOOD_FIELD,
                    f"Updated {IP_ADDR_LABEL} in {P2POOL_LABEL} deployment record"))
            if update_data[STRATUM_PORT_FIELD] != p2pool_rec[STRATUM_PORT_FIELD]:
                update_flag = True
                results.append(result_row(
                    STRATUM_PORT_LABEL, GOOD_FIELD,
                    f"Updated {STRATUM_PORT_LABEL} in {P2POOL_LABEL} deployment record"))
            if update_flag:
                self.db.update_one(
                    filter={COMPONENT_FIELD: P2POOL_FIELD, INSTANCE_FIELD: orig_instance},
                    col_name=self.col_name, new_values=update_data)
            else:
                results.append(result_row(
                    P2POOL_LABEL, WARN_FIELD,
                    "Nothing to update"
                ))
                return results
            return results
      
    def update_vendor_dir(self, new_dir: str, old_dir: str, results: list):
        if os.path.exists(new_dir):
            # The new vendor dir exists, make a backup
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
            backup_vendor_dir = new_dir + '.' + timestamp
            try:
                os.rename(new_dir, backup_vendor_dir)
                results.append(result_row(
                    DEPLOYMENT_DIR_LABEL, WARN_FIELD, 
                    f'Found existing directory ({new_dir}), backed it up as ({backup_vendor_dir})'))
            except PermissionError as e:
                results.append(result_row(
                    DEPLOYMENT_DIR_LABEL, ERROR_FIELD, 
                    f'Unable to backup ({new_dir}) as ({backup_vendor_dir}), aborting deployment directory update:\n{e}'))
        # Move the vendor_dir to the new location
        try:
            shutil.move(old_dir, new_dir)
            results.append(result_row(
                DEPLOYMENT_DIR_LABEL, GOOD_FIELD, 
                f'Moved old deployment directory ({old_dir}) to ({new_dir})'))
        except (PermissionError, FileNotFoundError) as e:
            results.append(result_row(
                DEPLOYMENT_DIR_LABEL, ERROR_FIELD, 
                f'Failed to move ({old_dir}) to ({new_dir})\n{e}'))
        return results
