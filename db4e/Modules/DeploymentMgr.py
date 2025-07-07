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
from db4e.Constants.Labels import DEPLOYMENT_DIR_LABEL, MONERO_WALLET_LABEL
from db4e.Constants.Fields import (
    DB4E_FIELD, DOC_TYPE_FIELD, COMPONENT_FIELD, DEPLOYMENT_FIELD, ERROR_FIELD, 
    GOOD_FIELD, GROUP_FIELD, INSTALL_DIR_FIELD, UPDATED_FIELD, 
    USER_FIELD, USER_WALLET_FIELD, VENDOR_DIR_FIELD, VERSION_FIELD, WARN_FIELD)

# The Mongo collection that houses the deployment records
DEPL_COL = 'depl'

class DeploymentMgr:
    
    def __init__(self, config: Config):
        self.ini = config
        self.db = DbMgr(config)
        self.col_name = DEPL_COL

    def add_deployment(self, rec):
        rec[DOC_TYPE_FIELD] = DEPLOYMENT_FIELD
        rec[UPDATED_FIELD] = datetime.now(timezone.utc)
        # Get the COMPONENT_FIELD version from the static YAML config file
        if rec[COMPONENT_FIELD] == DB4E_FIELD:
            rec[USER_FIELD] = getpass.getuser()
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
        # Ask the db for the component record
        db_rec = self.db.find_one(self.col_name, {DOC_TYPE_FIELD: DEPLOYMENT_FIELD, COMPONENT_FIELD: component})
        # rec is a cursor object.
        if db_rec:
            rec = {}
            component = db_rec[COMPONENT_FIELD]
            if component == DB4E_FIELD:
                rec[GROUP_FIELD] = db_rec[GROUP_FIELD]
                rec[INSTALL_DIR_FIELD] = db_rec[INSTALL_DIR_FIELD]
                rec[USER_FIELD] = db_rec[USER_WALLET_FIELD]
                rec[USER_WALLET_FIELD] = db_rec[USER_WALLET_FIELD]
                rec[VENDOR_DIR_FIELD] = db_rec[VENDOR_DIR_FIELD]
            return rec
        # No record for this deployment exists

        # Check if this is the first time the app has been run
        rec = self.db.find_one(self.col_name, {DOC_TYPE_FIELD: DEPLOYMENT_FIELD, COMPONENT_FIELD: DB4E_FIELD })
        if not rec:
            return False
        
    def get_deployment_by_instance(self, component, instance):
        if instance == 'db4e core':
            return self.get_deployment(DB4E_FIELD)
      
    def update_deployment(self, update_data):
        # Track the progress of this request
        results = []
        update_flag = True
        component = update_data[COMPONENT_FIELD]
        if component == DB4E_FIELD:
            if 'to_module' in update_data:
                updated_rec, results, update_flag = self.update_vendor_dir(update_data)
            else:
                # This request is coming from the InstallMgr, which has a complete
                # db4e Mongo record update.
                updated_rec = update_data

        # Get the DbMgr to update Mongo
        if update_flag:
            filter = {DOC_TYPE_FIELD: DEPLOYMENT_FIELD, COMPONENT_FIELD: DB4E_FIELD}
            self.db.update_one(self.col_name, filter, updated_rec)
        return results
      
    def update_vendor_dir(self, update_data):
        update_flag = True
        results = []
        # This request is coming from the Db4E form
        updated_user_wallet = update_data[USER_WALLET_FIELD]
        updated_vendor_dir = update_data[VENDOR_DIR_FIELD]
        db_rec = self.get_deployment(DB4E_FIELD)
        db_user_wallet = db_rec[USER_WALLET_FIELD]
        db_vendor_dir = db_rec[VENDOR_DIR_FIELD]
        if updated_user_wallet == db_user_wallet and updated_vendor_dir == db_vendor_dir:
            update_flag = False # User clicked update without changing the data
        else:
            # Update the user_wallet in Mongo, even if they didn't change it
            db_rec[USER_WALLET_FIELD] = updated_user_wallet
            results.append(result_row(MONERO_WALLET_LABEL, GOOD_FIELD, 'Updated Monero wallet'))
            if not updated_vendor_dir == db_vendor_dir:
                # User chose a new deployment directory (vendor_dir)
                if os.path.exists(updated_vendor_dir):
                    # The new vendor dir exists, make a backup
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
                    backup_vendor_dir = updated_vendor_dir + '.' + timestamp
                    try:
                        os.rename(updated_vendor_dir, backup_vendor_dir)
                        results.append(result_row(DEPLOYMENT_DIR_LABEL, WARN_FIELD, f'Found existing directory ({updated_vendor_dir}), backed it up as ({backup_vendor_dir})'))
                    except PermissionError as e:
                        results.append(result_row(DEPLOYMENT_DIR_LABEL, ERROR_FIELD, f'Unable to backup ({updated_vendor_dir}) as ({backup_vendor_dir}), aborting deployment directory update:\n{e}'))
            # Move the vendor_dir to the new location
            try:
                shutil.move(db_vendor_dir, updated_vendor_dir)
                db_rec[VENDOR_DIR_FIELD] = updated_vendor_dir
                results.append(result_row(DEPLOYMENT_DIR_LABEL, GOOD_FIELD, f'Moved old deployment directory ({db_vendor_dir}) to ({updated_vendor_dir})'))
            except (PermissionError, FileNotFoundError) as e:
                results.append(result_row(DEPLOYMENT_DIR_LABEL, ERROR_FIELD, f'Failed to move ({db_vendor_dir}) to ({updated_vendor_dir})\n{e}'))
        return (db_rec, results, update_flag)