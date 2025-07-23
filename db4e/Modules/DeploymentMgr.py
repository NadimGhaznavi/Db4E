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
from db4e.Modules.Helper import result_row, is_valid_ip_or_hostname
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Fields import *
from db4e.Constants.Labels import (
    DB4E_LABEL, INSTANCE_LABEL, IP_ADDR_LABEL, MONEROD_LABEL, MONEROD_REMOTE_LABEL,
    NUM_THREADS_LABEL, P2POOL_LABEL, P2POOL_REMOTE_LABEL, RPC_BIND_PORT_LABEL,
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
    ZMQ_PUB_PORT_FIELD
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
        instance = None
        fatal_error = False
        # Add a Monero daemon deployment
        if rec[COMPONENT_FIELD] == MONEROD_FIELD:
            if rec[REMOTE_FIELD]: # Remote deployment
                (rec, component_label, instance, results,
                fatal_error) = self.add_remote_monerod_deployment(rec)
            else: # Local deployment
                results.append(result_row(
                    MONEROD_REMOTE_LABEL, WARN_FIELD,
                    f"🚧 {MONEROD_REMOTE_FIELD} deployment coming soon 🚧"
                ))
                return rec, results
            
        # Add a P2Pool deployment
        elif rec[COMPONENT_FIELD] == P2POOL_FIELD:
            if rec[REMOTE_FIELD]: # Remote deployment
                (rec, component_label, instance, results,
                fatal_error) = self.add_remote_p2pool_deployment(rec)
            else: # Local deployment
                results.append(result_row(
                    P2POOL_LABEL, WARN_FIELD,
                    f"🚧 {P2POOL_LABEL} deployment coming soon 🚧"
                ))
                return rec, results
            
        # Add a XMRig deployment
        elif rec[COMPONENT_FIELD] == XMRIG_FIELD:
            (rec, component_label, instance, results,
             fatal_error) = self.add_xmrig_deployment(rec)

        if not fatal_error:
            rec[UPDATED_FIELD] = datetime.now(timezone.utc)
            self.db.insert_one(self.col_name, rec)
            if instance:
                results_message = f"Added new deployment record ({instance})"
            else:
                results_message = f"Added new deployment record"
            results.append(result_row(
                DB4E_LABEL, GOOD_FIELD, results_message))

        return rec, results
    

    def add_remote_monerod_deployment(self, rec):
        print(f"DeploymentMgr:add_remote_monerod_deployment(): {rec}")
        results = []
        fatal_error = False
        # Check that the user actually filled out the form
        if not rec[INSTANCE_FIELD]:
            fatal_error = True
            results.append(result_row(
                INSTANCE_LABEL, ERROR_FIELD,
                f"Missing required field: {INSTANCE_LABEL}"
            ))

        if not rec[IP_ADDR_FIELD]:
            fatal_error = True
            results.append(result_row(
                IP_ADDR_LABEL, ERROR_FIELD,
                f"Missing required field: {IP_ADDR_LABEL}"
            ))

        elif not is_valid_ip_or_hostname(rec[IP_ADDR_FIELD]):
            fatal_error = True
            results.append(result_row(
                IP_ADDR_LABEL, ERROR_FIELD,
                f"Invalid {IP_ADDR_LABEL}: {rec[IP_ADDR_FIELD]}"
            ))

        if not rec[RPC_BIND_PORT_FIELD]:
            fatal_error = True
            results.append(result_row(
                RPC_BIND_PORT_LABEL, ERROR_FIELD,
                f"Missing required field: {RPC_BIND_PORT_LABEL}"
            ))

        if not rec[ZMQ_PUB_PORT_FIELD]:
            fatal_error = True
            results.append(result_row(
                ZMQ_PUB_PORT_LABEL, ERROR_FIELD,
                f"Missing required field: {ZMQ_PUB_PORT_LABEL}"
            ))
        component_label = MONEROD_REMOTE_LABEL
        instance = rec[INSTANCE_FIELD]

        if fatal_error:
            return (rec, component_label, instance, results, fatal_error)
        db_rec = self.db.get_new_rec(MONEROD_REMOTE_FIELD)
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
        elif not is_valid_ip_or_hostname(rec[IP_ADDR_FIELD]):
            results.append(result_row(
                IP_ADDR_LABEL, ERROR_FIELD,
                f"Invalid {IP_ADDR_LABEL}: {rec[IP_ADDR_FIELD]}"
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
        db_rec = self.db.get_new_rec(P2POOL_REMOTE_FIELD)
        db_rec[INSTANCE_FIELD] = rec[INSTANCE_FIELD]
        db_rec[IP_ADDR_FIELD] = rec[IP_ADDR_FIELD]
        db_rec[STRATUM_PORT_FIELD] = rec[STRATUM_PORT_FIELD]
        db_rec[VERSION_FIELD] = self.ini.config[rec[COMPONENT_FIELD]][VERSION_FIELD]
        rec = db_rec
        return (rec, component_label, instance, results, fatal_error)

    def add_xmrig_deployment(self, rec):
        print(f"DeploymentMgr:add_xmrig_deployment(): {rec}")
        results = []
        fatal_error = False
        # Check that the user filled out the form
        if not rec[INSTANCE_FIELD]:
            results.append(result_row(
                INSTANCE_LABEL, ERROR_FIELD,
                f"Missing required field: {INSTANCE_LABEL}"
            ))
            fatal_error = True
        if not rec[NUM_THREADS_FIELD]:
            results.append(result_row(
                NUM_THREADS_LABEL, ERROR_FIELD,
                f"Missing required field: {NUM_THREADS_LABEL}"
            ))
            fatal_error = True
        if not rec[P2POOL_ID_FIELD]:
            results.append(result_row(
                P2POOL_LABEL, ERROR_FIELD,
                f"Missing required field: {P2POOL_LABEL}"
            ))
            fatal_error = True
        component_label = XMRIG_LABEL
        instance = rec[INSTANCE_FIELD]
        if fatal_error:
            return (rec, component_label, instance, results, fatal_error)
        db_rec = self.db.get_new_rec(XMRIG_FIELD)
        db_rec[INSTANCE_FIELD] = rec[INSTANCE_FIELD]
        db_rec[NUM_THREADS_FIELD] = rec[NUM_THREADS_FIELD]
        db_rec[PARENT_ID_FIELD] = rec[PARENT_ID_FIELD]
        db_rec[VERSION_FIELD] = self.ini.config[rec[COMPONENT_FIELD]][VERSION_FIELD]
        rec = db_rec
        results, conf_file = self.conf_mgr.gen_xmrig_config(
            rec=rec, depl_mgr=self, results=results)
        rec[CONFIG_FIELD] = conf_file
        return (rec, component_label, instance, results, fatal_error)

    def del_deployment(self, rec_data):
        component = rec_data[COMPONENT_FIELD]
        instance = rec_data[INSTANCE_FIELD]

        self.db.delete_one(
            col_name=self.col_name,
            filter={COMPONENT_FIELD: component, INSTANCE_FIELD: instance}
        )
        cleared_rec = self.db.get_new_rec(component)
        return [
            result_row(
                label=component.upper(),
                status=GOOD_FIELD,
                msg=f"Deleted {component} deployment: {instance}"
            ),
            cleared_rec
        ]

    def get_deployment(self, component, instance=None):
        #print(f"DeploymentMgr:get_deployment(): {component}/{instance}")
        if component == DB4E_FIELD or component == DB4E_LABEL:
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

        else:
            return self.db.find_one(
                col_name=self.col_name, 
                filter={COMPONENT_FIELD: component, INSTANCE_FIELD: instance})

        # No record for this deployment exists

    def get_deployment_by_id(self, id):
        return self.db.find_one(col_name=self.col_name, filter={'_id': id})

    def get_deployment_ids_and_instances(self, component):
        db_recs = self.db.find_many(
            self.col_name, {COMPONENT_FIELD: component})
        result_list = []
        for db_rec in db_recs:
            result_list.append((db_rec[INSTANCE_FIELD], db_rec[ID_FIELD]))
        result_list.sort()
        return result_list or []

    def get_deployments(self, component=None) -> list[dict]:
        query = {}
        if component is not None:
            query[COMPONENT_FIELD] = component
        return self.db.find_many(self.col_name, query)
    
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
                os.path.join(os.path.dirname(__file__), '..', '..', DB4E_FIELD, TEMPLATES_DIR_DEFAULT)
            )
        
    def is_initialized(self):
        rec = self.db.find_one(self.col_name, {COMPONENT_FIELD: DB4E_FIELD})
        if rec:
            #print(f"DeploymentMgr:is_initialized(): True")
            return True
        else:
            #print(f"DeploymentMgr:is_initialized(): False")
            return False

    def new_deployment(self, form_data):
        #print(f"DeploymentMgr:new_deployment(): {form_data}")
        if form_data[DEPLOYMENT_TYPE_FIELD] == "new_monerod_type_monerod":
            return {'type': 'local'}
        elif form_data[DEPLOYMENT_TYPE_FIELD] == "new_monerod_type_remote_monerod":
            return self.db.get_new_rec(MONEROD_REMOTE_FIELD)

    def update_deployment(self, update_data):
        component = update_data[COMPONENT_FIELD]
        if component == DB4E_FIELD:
            return self.update_db4e_deployment(update_data=update_data)
        elif component == MONEROD_FIELD:
            return self.update_monerod_deployment(update_data=update_data)
        elif component == P2POOL_FIELD:
            return self.update_p2pool_deployment(update_data=update_data)
        elif component == XMRIG_FIELD:
            return self.update_xmrig_deployment(update_data=update_data)

    def update_db4e_deployment(self, update_data):
        results = []
        update_flag = False
        filter = {COMPONENT_FIELD: DB4E_FIELD}
        rec = self.get_deployment(DB4E_FIELD)

        if FORM_DATA_FIELD in update_data:
            # Remove frontend-only fields
            update_data.pop(FORM_DATA_FIELD, None)
            update_data.pop(TO_MODULE_FIELD, None)
            update_data.pop(TO_METHOD_FIELD, None)

            # Track field changes
            if not update_data.get(USER_WALLET_FIELD):
                results.append(result_row(
                    USER_WALLET_LABEL, ERROR_FIELD,
                    f"Missing {USER_WALLET_LABEL}"
                ))
            elif update_data[USER_WALLET_FIELD] != rec[USER_WALLET_FIELD]:
                update_flag = True
                results.append(result_row(
                    USER_WALLET_LABEL, GOOD_FIELD,
                    f"Updated {USER_WALLET_LABEL} in {DB4E_LABEL} deployment record"
                ))
                rec[USER_WALLET_FIELD] = update_data[USER_WALLET_FIELD]

            if not update_data.get(VENDOR_DIR_FIELD):
                results.append(result_row(
                    VENDOR_DIR_LABEL, ERROR_FIELD,
                    f"Missing {VENDOR_DIR_LABEL}"
                ))
            elif update_data[VENDOR_DIR_FIELD] != rec[VENDOR_DIR_FIELD]:
                update_flag = True
                update_flag, results = self.update_vendor_dir(
                    new_dir=update_data[VENDOR_DIR_FIELD],
                    old_dir=rec[VENDOR_DIR_FIELD],
                    results=results)
                rec[VENDOR_DIR_FIELD] = update_data[VENDOR_DIR_FIELD]

            if update_flag:
                self.db.update_one(self.col_name, filter, rec)
            else:
                results.append(result_row(
                    DB4E_LABEL, WARN_FIELD,
                    "Nothing to update"
                ))
            print(f"DeploymentMgr:update_db4e_deployment(): results: {results}")
            return rec, results
        
        else:
            # If no FORM_DATA_FIELD, treat as direct DB update (system-side, not user form)
            self.db.update_one(self.col_name, filter, update_data)
            return rec

    def update_deployment(self, update_data):
        #print(f"DeploymentMgr:update_deployment(): {update_data}")
        component = update_data[COMPONENT_FIELD]
        if component == DB4E_FIELD:
            return self.update_db4e_deployment(update_data)
        elif component == MONEROD_FIELD:
            return self.update_monerod_deployment(update_data)
        elif component == P2POOL_FIELD:
            return self.update_p2pool_deployment(update_data)
        elif component == XMRIG_FIELD:
            return self.update_xmrig_deployment(update_data)
        else:
            rec = update_data.copy()
            results = [result_row(
                DEPLOYMENT_MGR_FIELD, ERROR_FIELD,
                f"{DEPLOYMENT_MGR_FIELD}:update_deployment(): No handler for component " \
                f"({component})"
            )]
            return rec, results


    def update_monerod_deployment(self, update_data):
        results = []
        update_flag = False

        # Remove frontend routing metadata
        update_data.pop(TO_MODULE_FIELD, None)
        update_data.pop(TO_METHOD_FIELD, None)

        orig_instance = update_data[ORIG_INSTANCE_FIELD]
        rec = self.get_deployment(MONEROD_FIELD, orig_instance)

        # Field-by-field comparison
        if update_data[INSTANCE_FIELD] != rec[INSTANCE_FIELD]:
            update_flag = True
            results.append(result_row(
                INSTANCE_LABEL, GOOD_FIELD,
                f"Updated {INSTANCE_LABEL} in {MONEROD_LABEL} deployment record"
            ))
            rec[INSTANCE_FIELD] = update_data[INSTANCE_FIELD]

        if update_data[IP_ADDR_FIELD] != rec[IP_ADDR_FIELD]:
            update_flag = True
            results.append(result_row(
                IP_ADDR_LABEL, GOOD_FIELD,
                f"Updated {IP_ADDR_LABEL} in {MONEROD_LABEL} deployment record"
            ))
            rec[IP_ADDR_FIELD] = update_data[IP_ADDR_FIELD]

        if update_data[RPC_BIND_PORT_FIELD] != rec[RPC_BIND_PORT_FIELD]:
            update_flag = True
            results.append(result_row(
                RPC_BIND_PORT_LABEL, GOOD_FIELD,
                f"Updated {RPC_BIND_PORT_LABEL} in {MONEROD_LABEL} deployment record"
            ))
            rec[RPC_BIND_PORT_FIELD] = update_data[RPC_BIND_PORT_FIELD]

        if update_data[ZMQ_PUB_PORT_FIELD] != rec[ZMQ_PUB_PORT_FIELD]:
            update_flag = True
            results.append(result_row(
                ZMQ_PUB_PORT_LABEL, GOOD_FIELD,
                f"Updated {ZMQ_PUB_PORT_LABEL} in {MONEROD_LABEL} deployment record"
            ))
            rec[ZMQ_PUB_PORT_FIELD] = update_data[ZMQ_PUB_PORT_FIELD]

        # Done comparing, drop orig_instance from update
        update_data.pop(ORIG_INSTANCE_FIELD, None)

        if update_flag:
            self.db.update_one(
                col_name=self.col_name,
                filter={COMPONENT_FIELD: MONEROD_FIELD, INSTANCE_FIELD: orig_instance},
                new_values=rec,
            )
        else:
            results.append(result_row(
                MONEROD_LABEL, WARN_FIELD,
                f"{orig_instance} – Nothing to update"
            ))
        return rec, results

      
    def update_p2pool_deployment(self, update_data):
        results = []
        update_flag = False

        # Remove frontend metadata (optional)
        update_data.pop(FORM_DATA_FIELD, None)
        update_data.pop(TO_MODULE_FIELD, None)
        update_data.pop(TO_METHOD_FIELD, None)

        # Required field
        orig_instance = update_data[ORIG_INSTANCE_FIELD]
        rec = self.get_deployment(P2POOL_FIELD, orig_instance)

        # Compare fields and update in-place
        if update_data[INSTANCE_FIELD] != rec[INSTANCE_FIELD]:
            update_flag = True
            results.append(result_row(
                INSTANCE_LABEL, GOOD_FIELD,
                f"Updated {INSTANCE_LABEL} in {P2POOL_LABEL} deployment record"
            ))
            rec[INSTANCE_FIELD] = update_data[INSTANCE_FIELD]

        if update_data[IP_ADDR_FIELD] != rec[IP_ADDR_FIELD]:
            update_flag = True
            results.append(result_row(
                IP_ADDR_LABEL, GOOD_FIELD,
                f"Updated {IP_ADDR_LABEL} in {P2POOL_LABEL} deployment record"
            ))
            rec[IP_ADDR_FIELD] = update_data[IP_ADDR_FIELD]

        if update_data[STRATUM_PORT_FIELD] != rec[STRATUM_PORT_FIELD]:
            update_flag = True
            results.append(result_row(
                STRATUM_PORT_LABEL, GOOD_FIELD,
                f"Updated {STRATUM_PORT_LABEL} in {P2POOL_LABEL} deployment record"
            ))
            rec[STRATUM_PORT_FIELD] = update_data[STRATUM_PORT_FIELD]

        # Done comparing
        update_data.pop(ORIG_INSTANCE_FIELD)

        if update_flag:
            self.db.update_one(
                col_name=self.col_name,
                filter={COMPONENT_FIELD: P2POOL_FIELD, INSTANCE_FIELD: orig_instance},
                new_values=rec,
            )
        else:
            results.append(result_row(
                P2POOL_LABEL, WARN_FIELD,
                f"{orig_instance} – Nothing to update"
            ))
        return rec, results
      
    def update_vendor_dir(self, new_dir: str, old_dir: str, results: list):
        print(f"DeploymentMgr:update_vendor_dir(): {old_dir} > {new_dir}")
        update_flag = True

        if not old_dir or not new_dir:
            raise ValueError(f"update_vendor_dir(): Missing old or new directory")        

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

    def update_xmrig_deployment(self, update_data):
        results = []
        update_flag = False
        update_config_flag = False

        # Strip frontend metadata
        update_data.pop(TO_MODULE_FIELD, None)
        update_data.pop(TO_METHOD_FIELD, None)

        # Required field
        orig_instance = update_data[ORIG_INSTANCE_FIELD]
        rec = self.get_deployment(XMRIG_FIELD, orig_instance)

        # Compare + apply updates
        if update_data[INSTANCE_FIELD] != rec[INSTANCE_FIELD]:
            update_flag = True
            update_config_flag = True
            results.append(result_row(
                INSTANCE_LABEL, GOOD_FIELD,
                f"Updated {INSTANCE_LABEL} in {XMRIG_LABEL} deployment record"
            ))
            rec[INSTANCE_FIELD] = update_data[INSTANCE_FIELD]

        if update_data[NUM_THREADS_FIELD] != rec[NUM_THREADS_FIELD]:
            update_flag = True
            results.append(result_row(
                NUM_THREADS_LABEL, GOOD_FIELD,
                f"Updated {NUM_THREADS_LABEL} in {XMRIG_LABEL} deployment record"
            ))
            rec[NUM_THREADS_FIELD] = update_data[NUM_THREADS_FIELD]

        if update_data[PARENT_ID_FIELD] != rec[PARENT_ID_FIELD]:
            update_flag = True
            update_config_flag = True
            results.append(result_row(
                P2POOL_LABEL, GOOD_FIELD,
                f"Updated {P2POOL_LABEL} in {XMRIG_LABEL} deployment record"
            ))
            rec[PARENT_ID_FIELD] = update_data[PARENT_ID_FIELD]

        # Regenerate config if required
        if update_config_flag:
            results = self.conf_mgr.del_config(
                config_file=rec[CONFIG_FIELD], results=results)
            results, conf_file = self.conf_mgr.gen_xmrig_config(
                rec=rec, depl_mgr=self, results=results)
            rec[CONFIG_FIELD] = conf_file

        update_data.pop(ORIG_INSTANCE_FIELD)

        if update_flag:
            self.db.update_one(
                col_name=self.col_name,
                filter={COMPONENT_FIELD: XMRIG_FIELD, INSTANCE_FIELD: orig_instance},
                new_values=rec
            )
        else:
            results.append(result_row(
                XMRIG_LABEL, WARN_FIELD,
                f"{orig_instance} – Nothing to update"
            ))
        return rec, results
      
