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

from db4e.Modules.ConfigMgr import Config
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.Helper import result_row
from db4e.Constants.Labels import DB4E_LABEL, DEPLOYMENT_DIR_LABEL, MONERO_WALLET_LABEL
from db4e.Constants.Fields import (
    DB4E_FIELD, DOC_TYPE_FIELD, COMPONENT_FIELD, DEPLOYMENT_FIELD, ERROR_FIELD, 
    FORM_DATA_FIELD, GOOD_FIELD, GROUP_FIELD, INSTALL_DIR_FIELD, TO_MODULE_FIELD, 
    TO_METHOD_FIELD, UPDATED_FIELD, 
    USER_FIELD, USER_WALLET_FIELD, VENDOR_DIR_FIELD, VERSION_FIELD, WARN_FIELD)

# The Mongo collection that houses the deployment records
DEPL_COL = 'depl'

class DeploymentMgr:
    
    def __init__(self, config: Config):
        self.ini = config
        self.db = DbMgr(config)
        self.col_name = DEPL_COL
        self.db4e_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def add_deployment(self, rec):
        rec[DOC_TYPE_FIELD] = DEPLOYMENT_FIELD
        rec[UPDATED_FIELD] = datetime.now(timezone.utc)
        if rec[COMPONENT_FIELD] == DB4E_FIELD:
            rec[USER_FIELD] = getpass.getuser()
            rec[INSTALL_DIR_FIELD] = self.db4e_dir
        else:
            rec[VERSION_FIELD] = self.ini.config[rec[COMPONENT_FIELD]][VERSION_FIELD]
        self.db.insert_one(self.col_name, rec)

    def is_initialized(self):
        rec = self.db.find_one(self.col_name, {DOC_TYPE_FIELD: DEPLOYMENT_FIELD, COMPONENT_FIELD: DB4E_FIELD})
        if rec:
            return True
        else:
            return False

    def get_deployment(self, component):
        #print(f"DeploymentMgr:get_deployment(): {component}")
        # Ask the db for the component record
        db_rec = self.db.find_one(self.col_name, {DOC_TYPE_FIELD: DEPLOYMENT_FIELD, COMPONENT_FIELD: component})
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
            print(f"DeploymentMgr:get_deployment(): {component} > {db_rec} > {rec}")
            return rec
        # No record for this deployment exists

        # Check if this is the first time the app has been run
        rec = self.db.find_one(self.col_name, {DOC_TYPE_FIELD: DEPLOYMENT_FIELD, COMPONENT_FIELD: DB4E_FIELD })
        if not rec:
            return False
        
    def get_deployment_by_instance(self, component, instance):
        if instance == DB4E_LABEL:
            return self.get_deployment(DB4E_FIELD)

    def get_new_rec(self, rec_type):
        return self.db.get_new_rec(rec_type)

    def update_deployment(self, update_data):
        print(f"DeploymentMgr:update_deployment(): {update_data}")
        results = []
        if update_data[COMPONENT_FIELD] == DB4E_FIELD:
            filter = {DOC_TYPE_FIELD: DEPLOYMENT_FIELD, COMPONENT_FIELD: DB4E_FIELD}
            if FORM_DATA_FIELD in update_data:
                del update_data[FORM_DATA_FIELD]
                del update_data[TO_MODULE_FIELD]
                del update_data[TO_METHOD_FIELD]
                db4e_rec = self.get_deployment(DB4E_FIELD)
                if update_data[USER_WALLET_FIELD] != db4e_rec[USER_WALLET_FIELD]:
                    self.db.update_one(self.col_name, filter, update_data)
                    results.append(result_row(
                        MONERO_WALLET_LABEL, GOOD_FIELD, 
                        f"Updated {MONERO_WALLET_LABEL} in {DB4E_LABEL} deployment record"))
                if update_data[VENDOR_DIR_FIELD] != db4e_rec[VENDOR_DIR_FIELD]:
                    results += self.update_vendor_dir(
                        update_data[VENDOR_DIR_FIELD], 
                        db4e_rec[VENDOR_DIR_FIELD],
                        results=results)
                    self.db.update_one(self.col_name, filter, update_data)
                    results.append(result_row(
                        DEPLOYMENT_DIR_LABEL, GOOD_FIELD, 
                        f"Updated {DEPLOYMENT_DIR_LABEL} in {DB4E_LABEL} deployment record"))
                return results
            else:
                self.db.update_one(self.col_name, filter, update_data)
      
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
