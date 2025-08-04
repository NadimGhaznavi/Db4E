"""
db4e/Modules/OpsMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
import os

from db4e.Modules.ConfigMgr import Config
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.HealthMgr import HealthMgr
from db4e.Modules.Helper import (
    result_row, gen_radio_map, get_component_value, set_component_value, 
    get_effective_identity, update_component_values)
from db4e.Constants.Fields import (
    DB4E_FIELD, ERROR_FIELD, HEALTH_MSGS_FIELD,
    INSTANCE_FIELD, MONEROD_REMOTE_FIELD, NUM_THREADS_FIELD,
    PARENT_ID_FIELD, PARENT_INSTANCE_FIELD, P2POOL_FIELD, P2POOL_INSTANCE, 
    RADIO_MAP_FIELD, REMOTE_FIELD, XMRIG_FIELD, PYTHON_FIELD,
    INSTALL_DIR_FIELD, TEMPLATE_FIELD, ELEMENT_TYPE_FIELD, STRATUM_PORT_FIELD,
    MONEROD_FIELD, P2POOL_REMOTE_FIELD, IP_ADDR_FIELD, RPC_BIND_PORT_FIELD,
    ZMQ_PUB_PORT_FIELD, USER_FIELD, GROUP_FIELD)
from db4e.Constants.Labels import (OPS_MGR_LABEL)
from db4e.Constants.Defaults import (
    DEPLOYMENT_COL_DEFAULT, BIN_DIR_DEFAULT, PYTHON_DEFAULT, 
    TEMPLATES_DIR_DEFAULT)

class OpsMgr:


    def __init__(self, config: Config):
        self.ini = config
        self.db = DbMgr(config)
        self.depl_mgr = DeploymentMgr(config=config)
        self.health_mgr = HealthMgr()
        self.depl_col = DEPLOYMENT_COL_DEFAULT


    def add_deployment(self, rec: dict):
        results = []
        parent_rec = None
        elem_type = rec[ELEMENT_TYPE_FIELD]
        instance = get_component_value(rec, INSTANCE_FIELD)
        #print(f"OpsMgr:add_deployment(): {elem_type}")
        existing_rec = self.depl_mgr.get_deployment(elem_type=elem_type, instance=instance)
        if existing_rec:
            results.append(result_row(
                OPS_MGR_LABEL, ERROR_FIELD,
                f"A deployment record with that instance name already exists"
            ))
            rec[HEALTH_MSGS_FIELD] = results
            return rec
        
        # TODO Make sure the remote monerod and monerod records don't share an instance name.
        # TODO Same for p2pool.

        if elem_type == DB4E_FIELD:
            raise ValueError(f"OpsMgr:add_deployment(): {elem_type} should already exist")

        elif elem_type == MONEROD_REMOTE_FIELD:
            db_rec = self.get_new_rec(MONEROD_REMOTE_FIELD)
            db_rec = set_component_value(db_rec, INSTANCE_FIELD, rec[INSTANCE_FIELD])
            db_rec = set_component_value(db_rec, IP_ADDR_FIELD, rec[IP_ADDR_FIELD])
            db_rec = set_component_value(db_rec, RPC_BIND_PORT_FIELD, rec[RPC_BIND_PORT_FIELD])
            db_rec = set_component_value(db_rec, ZMQ_PUB_PORT_FIELD, rec[ZMQ_PUB_PORT_FIELD])
            rec = self.depl_mgr.add_deployment(db_rec)
            rec = self.health_mgr.check(rec=rec, parent_rec=parent_rec)
            return rec
        
        elif elem_type == P2POOL_REMOTE_FIELD:
            db_rec = self.get_new_rec(P2POOL_REMOTE_FIELD)
            db_rec = set_component_value(db_rec, INSTANCE_FIELD, rec[INSTANCE_FIELD])
            db_rec = set_component_value(db_rec, IP_ADDR_FIELD, rec[IP_ADDR_FIELD])
            db_rec = set_component_value(db_rec, STRATUM_PORT_FIELD, rec[STRATUM_PORT_FIELD])
            rec = self.depl_mgr.add_deployment(db_rec)
            rec = self.health_mgr.check(rec=rec, parent_rec=parent_rec)
            return rec
        
        elif elem_type == XMRIG_FIELD:
            db_rec = self.get_new_rec(XMRIG_FIELD)
            db_rec = set_component_value(db_rec, INSTANCE_FIELD, rec[INSTANCE_FIELD])
            db_rec = set_component_value(db_rec, NUM_THREADS_FIELD, rec[NUM_THREADS_FIELD])
            if rec[PARENT_ID_FIELD]:
                db_rec = set_component_value(db_rec, PARENT_ID_FIELD, rec[PARENT_ID_FIELD])
                parent_rec = self.depl_mgr.get_deployment_by_id(id=rec[PARENT_ID_FIELD])
            rec = self.depl_mgr.add_deployment(db_rec)
            rec[RADIO_MAP_FIELD] = gen_radio_map(rec=rec, depl_mgr=self.depl_mgr)
            rec = self.health_mgr.check(rec=rec, parent_rec=parent_rec)
            return rec
        
   
    def get_deployment(self, elem_type, instance=None):
        #print(f"OpsMgr:get_deployment(): {elem_type}/{instance}")        
        if ELEMENT_TYPE_FIELD in elem_type:
            if INSTANCE_FIELD in elem_type:
                instance = elem_type[INSTANCE_FIELD]
            elem_type = elem_type[ELEMENT_TYPE_FIELD]

        rec = self.depl_mgr.get_deployment(elem_type=elem_type, instance=instance)

        if not rec:
            if elem_type == MONEROD_FIELD:
                rec = self.depl_mgr.get_deployment(
                    elem_type=MONEROD_REMOTE_FIELD, instance=instance)
                elem_type = MONEROD_REMOTE_FIELD
            elif elem_type == P2POOL_FIELD:
                rec = self.depl_mgr.get_deployment(
                    elem_type=P2POOL_REMOTE_FIELD, instance=instance)
                elem_type = P2POOL_REMOTE_FIELD        
        
        if not rec:
            return {}
        
        # XMRig and Local P2Pool deployments have upstream dependencies
        parent_rec = None
        remote = get_component_value(rec, REMOTE_FIELD)
        parent_id = get_component_value(rec, PARENT_ID_FIELD)
        instance = get_component_value(rec, INSTANCE_FIELD)

        if elem_type == XMRIG_FIELD or elem_type == P2POOL_FIELD and not remote:
            parent_rec = self.depl_mgr.get_deployment_by_id(id=parent_id)
            #print(f"OpsMgr:get_deployment(): parent_rec: {parent_rec}")
            if parent_rec:
                parent_instance = get_component_value(parent_rec, INSTANCE_FIELD)
                rec[PARENT_INSTANCE_FIELD] = parent_instance
            else:
                rec[PARENT_INSTANCE_FIELD] = ""
            rec[RADIO_MAP_FIELD] = gen_radio_map(rec=rec, depl_mgr=self.depl_mgr)
            rec = self.health_mgr.check(rec=rec, parent_rec=parent_rec)
        rec = self.health_mgr.check(rec=rec, parent_rec=parent_rec)
        #print(f"OpsMgr:get_deployment(): elem_type: {elem_type}")
        return rec


    def get_deployments(self) -> list[dict]:
        deployments = self.depl_mgr.get_deployments()  # ← now returns full recs
        for rec in deployments:
            parent_rec = None
            if PARENT_ID_FIELD in rec:
                parent_rec = self.depl_mgr.get_deployment_by_id(id=rec[PARENT_ID_FIELD])
                rec[PARENT_INSTANCE_FIELD] = parent_rec.get(INSTANCE_FIELD, "") if parent_rec else ""
            rec = self.health_mgr.check(rec=rec, parent_rec=parent_rec)
        return deployments


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
        
        else:
            raise ValueError(f"OpsMgr:get_dir(): No handler for: {aDir}")
        

    def get_new_rec(self, data: str) -> dict:
        #print(f"OpsMgr:get_new_rec(): data: {data}")

        # Db4E Core template
        if ELEMENT_TYPE_FIELD in data:
            elem_type = data[ELEMENT_TYPE_FIELD]
        else:
            elem_type = data

        if elem_type == XMRIG_FIELD:
            return self.get_new_xmrig_rec(data)
        
        elif elem_type == DB4E_FIELD:
            return self.get_new_db4e_rec(data)

        rec = self.db.get_new_rec(elem_type)
        return rec    

    def get_new_xmrig_rec(self, form_data: dict) -> dict:
        rec = self.db.get_new_rec(XMRIG_FIELD)
        rec[RADIO_MAP_FIELD] = gen_radio_map(rec=rec, depl_mgr=self.depl_mgr)
        #print(f"OpsMgr:get_new_xmrig_rec(): radio_map_field: {rec[RADIO_MAP_FIELD]}")
        return rec


    def is_depl_initialized(self) -> bool:
        return self.depl_mgr.is_initialized()


    def update_deployment(self, form_data):
        #print(f"OpsMgr:update_deployment(): update_data: {form_data}")
        elem_type = form_data[ELEMENT_TYPE_FIELD]

        if elem_type == XMRIG_FIELD:
            return self.update_xmrig_deployment(form_data)

        rec = self.depl_mgr.update_deployment(rec=form_data)

        if elem_type == DB4E_FIELD or elem_type == MONEROD_REMOTE_FIELD or \
            elem_type == P2POOL_REMOTE_FIELD:
            rec = self.health_mgr.check(rec=rec, parent_rec=None)



        return rec
        

    def update_xmrig_deployment(self, rec):
        #print(f"OpsMgr:update_xmrig_deployment(): rec: {rec}")
        rec = self.depl_mgr.update_deployment(rec=rec)
        rec[RADIO_MAP_FIELD] = gen_radio_map(rec=rec, depl_mgr=self.depl_mgr)
        parent_id = get_component_value(rec, PARENT_ID_FIELD)
        p2pool_rec = None
        if parent_id:
            p2pool_rec = self.depl_mgr.get_deployment_by_id(parent_id)
        rec = self.health_mgr.check(rec=rec, parent_rec=p2pool_rec)
        return rec
        