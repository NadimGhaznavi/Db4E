"""
db4e/Modules/OpsMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConfigMgr import Config
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.HealthMgr import HealthMgr
from db4e.Modules.Helper import result_row, gen_radio_map
from db4e.Constants.Fields import (
    ACTIVE_FIELD, COMPONENT_FIELD, DB4E_FIELD, DISABLE_FIELD, ERROR_FIELD, 
    HEALTH_MSG_FIELD, INSTANCE_FIELD, MONEROD_FIELD, MONEROD_REMOTE_FIELD, 
    PARENT_ID_FIELD, PARENT_INSTANCE_FIELD, P2POOL_FIELD, P2POOL_INSTANCE, 
    PENDING_FIELD, RADIO_MAP_FIELD, REMOTE_FIELD, STATUS_FIELD, WARN_FIELD, 
    XMRIG_FIELD)
from db4e.Constants.Labels import (DB4E_LABEL, OPS_MGR_LABEL)
from db4e.Constants.Defaults import (DEPLOYMENT_COL_DEFAULT, OPS_COL_DEFAULT)

class Status:
    ACTIVE = ACTIVE_FIELD
    DISABLED = DISABLE_FIELD
    ERROR = ERROR_FIELD
    WARNING = WARN_FIELD
    PENDING = PENDING_FIELD

class OpsMgr:

    def __init__(self, config: Config):
        self.ini = config
        self.db = DbMgr(config)
        self.depl_mgr = DeploymentMgr(config=config)
        self.health_mgr = HealthMgr()
        self.depl_col = DEPLOYMENT_COL_DEFAULT

    def add_deployment(self, rec: dict):
        print(f"OpsMgr:add_deployment(): {rec}")
        results = []
        parent_rec = None
        component = rec[COMPONENT_FIELD]

        existing_rec = self.depl_mgr.get_deployment(
            component=rec[COMPONENT_FIELD], instance=rec[INSTANCE_FIELD])
        print(f"OpsMgr:add_deployment(): checking for: {component}/{rec[INSTANCE_FIELD]}")
        if existing_rec:
            results.append(result_row(
                OPS_MGR_LABEL, ERROR_FIELD,
                f"A deployment record with that instance name already exists"
            ))
            return self.set_status(rec=rec, status=ERROR_FIELD, results=results)
    
        rec, results = self.depl_mgr.add_deployment(rec)
        status, health_results = self.health_mgr.check(
            component=component, rec=rec, parent_rec=parent_rec)
        results += health_results
        return self.set_status(rec=rec, status=status, results=results)

    def get_deployment(self, component, instance=None):
        rec = self.depl_mgr.get_deployment(component=component, instance=instance)
        if not rec:
            return None
        parent_rec = None
        if component == XMRIG_FIELD or component == P2POOL_FIELD and not rec[REMOTE_FIELD]:
            parent_rec = self.depl_mgr.get_deployment_by_id(id=rec[PARENT_ID_FIELD])
            rec[PARENT_INSTANCE_FIELD] = parent_rec.get(INSTANCE_FIELD, "") if parent_rec else ""
            rec[RADIO_MAP_FIELD] = gen_radio_map(rec=rec, ops_mgr=self)
        status, results = self.health_mgr.check(
            component=component, rec=rec, parent_rec=parent_rec)
        return self.set_status(rec=rec, status=status, results=results)

    def get_deployments(self) -> list[dict]:
        deployments = self.depl_mgr.get_deployments()  # ← now returns full recs
        for rec in deployments:
            component = rec[COMPONENT_FIELD]
            parent_rec = None
            if component in (XMRIG_FIELD, P2POOL_FIELD) and PARENT_ID_FIELD in rec:
                parent_rec = self.depl_mgr.get_deployment_by_id(id=rec[PARENT_ID_FIELD])
                rec[PARENT_INSTANCE_FIELD] = parent_rec.get(INSTANCE_FIELD, "") if parent_rec else ""
            status, results = self.health_mgr.check(
                component=component, rec=rec, parent_rec=parent_rec)
            self.set_status(rec=rec, status=status, results=results)
        return deployments


    def get_new_rec(self, rec_request: str) -> dict:
        #rec = self.db.get_new_rec(rec_type=rec_request[COMPONENT_FIELD])
        #status, results = self.health_mgr.check(component=rec[COMPONENT_FIELD], rec=rec)
        if rec_request[COMPONENT_FIELD] == XMRIG_FIELD:
            return self.get_new_xmrig_rec(rec_request)
        elif rec_request[COMPONENT_FIELD] == MONEROD_FIELD and rec_request[REMOTE_FIELD]:
            return self.get_new_remote_monerod_rec(rec_request)

    def get_new_xmrig_rec(self, rec: dict) -> dict:
        rec = self.db.get_new_rec(XMRIG_FIELD)
        rec[STATUS_FIELD] = PENDING_FIELD
        rec[REMOTE_FIELD] = False
        rec[RADIO_MAP_FIELD] = gen_radio_map(rec=rec, ops_mgr=self)

        parent_id = rec.get(PARENT_ID_FIELD, "")
        p2pool_rec = self.depl_mgr.get_deployment_by_id(parent_id)
        rec[P2POOL_INSTANCE] = p2pool_rec.get(INSTANCE_FIELD, "") if p2pool_rec else ""
        return rec

    def get_new_remote_monerod_rec(self, rec: dict) -> dict:
        rec = self.db.get_new_rec(MONEROD_REMOTE_FIELD)
        rec[STATUS_FIELD] = PENDING_FIELD
        rec[REMOTE_FIELD] = True
        status, results = self.health_mgr.check(
                component=rec[COMPONENT_FIELD], rec=rec)
        return self.set_status(rec=rec, status=status, results=results)
    
    def set_status(self, rec, status=None, results=None):
        #print(f"OpsMgr:set_status(): rec: {rec}, status: {status}, results: {results}")
        # If no status is explicitly given, infer from results
        if status is None and results:
            if any(row[STATUS_FIELD] == ERROR_FIELD for row in results):
                status = Status.ERROR
            else:
                status = Status.ACTIVE
        rec[STATUS_FIELD] = status
        if results is not None:
            rec[HEALTH_MSG_FIELD] = results
        if INSTANCE_FIELD in rec:
            self.db.update_one(self.depl_col, 
                            {COMPONENT_FIELD: rec[COMPONENT_FIELD],
                                INSTANCE_FIELD: rec[INSTANCE_FIELD]}, rec)
        else:
            self.db.update_one(self.depl_col, {COMPONENT_FIELD: rec[COMPONENT_FIELD]}, rec)
            return rec
    

    def update_deployment(self, updata_data):
        rec, results = self.depl_mgr.update_deployment(update_data=updata_data)

        parent_results = []
        component = rec[COMPONENT_FIELD]
        parent_rec = None

        if component == XMRIG_FIELD:
            parent_rec = self.depl_mgr.get_deployment_by_id(id=rec[PARENT_ID_FIELD])

        elif component == P2POOL_FIELD and not updata_data[REMOTE_FIELD]:
            parent_rec = self.depl_mgr.get_deployment_by_id(id=rec[PARENT_ID_FIELD])

        status, health_results = self.health_mgr.check(
            component=component, rec=rec, parent_rec=parent_rec)
        results += health_results
        return self.set_status(rec=rec, status=status, results=results)        