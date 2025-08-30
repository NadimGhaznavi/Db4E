"""
db4e/Modules/OpsMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
import os

from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.HealthMgr import HealthMgr
from db4e.Modules.HealthCache import HealthCache
from db4e.Modules.XMRig import XMRig
from db4e.Modules.P2Pool import P2Pool

from db4e.Constants.Fields import (
    INSTANCE_FIELD, MONEROD_REMOTE_FIELD, PARENT_ID_FIELD, PARENT_INSTANCE_FIELD, 
    P2POOL_FIELD, ELEMENT_FIELD, ELEMENT_TYPE_FIELD, MONEROD_FIELD, P2POOL_REMOTE_FIELD)
from db4e.Constants.Defaults import (DEPLOYMENT_COL_DEFAULT)

class OpsMgr:


    def __init__(self):
        self.db = DbMgr()
        self.depl_mgr = DeploymentMgr()
        self.health_mgr = HealthMgr()
        self.health_cache = HealthCache(health_mgr=self.health_mgr, depl_mgr=self.depl_mgr)
        self.depl_col = DEPLOYMENT_COL_DEFAULT


    def add_deployment(self, form_data: dict):
        #print(f"OpsMgr:add_deployment(): {elem_type}")
        elem = form_data[ELEMENT_FIELD]
        #print(f"OpsMgr:add_deployment(): {elem.to_rec()}")
        
        # TODO Make sure the remote monerod and monerod records don't share an instance name.
        # TODO Same for p2pool.
        elem = self.depl_mgr.add_deployment(elem)
        self.health_mgr.check(elem)
        return elem
 
   
    def get_deployment(self, elem_type, instance=None):
        #print(f"OpsMgr:get_deployment(): {elem_type}/{instance}")
        if type(elem_type) == dict:
            if INSTANCE_FIELD in elem_type:
                instance = elem_type[INSTANCE_FIELD]
            elem_type = elem_type[ELEMENT_TYPE_FIELD]

        elem = self.depl_mgr.get_deployment(elem_type=elem_type, instance=instance)
        print(f"OpsMgr:get_deployment(): {elem}")

        if not elem:
            if elem_type == MONEROD_FIELD:
                elem = self.depl_mgr.get_deployment(
                    elem_type=MONEROD_REMOTE_FIELD, instance=instance)
                elem_type = MONEROD_REMOTE_FIELD
            elif elem_type == P2POOL_FIELD:
                elem = self.depl_mgr.get_deployment(
                    elem_type=P2POOL_REMOTE_FIELD, instance=instance)
                elem_type = P2POOL_REMOTE_FIELD        
        
        if type(elem) == XMRig:
            elem.instance_map(self.depl_mgr.get_deployment_ids_and_instances(P2POOL_FIELD))
        elif type(elem) == P2Pool:
            elem.instance_map(self.depl_mgr.get_deployment_ids_and_instances(MONEROD_FIELD))

        elem = self.health_mgr.check(elem)
        return elem


    def get_monerods(self) -> list:
        return self.health_cache.get_monerods()


    def get_p2pools(self) -> list:
        return self.health_cache.get_p2pools()


    def get_xmrigs(self) -> list:
        return self.health_cache.get_xmrigs()


    def get_new(self, form_data: dict):
        elem = self.depl_mgr.get_new(form_data[ELEMENT_TYPE_FIELD])
        if type(elem) == XMRig:
            elem.instance_map(self.depl_mgr.get_deployment_ids_and_instances(P2POOL_FIELD))
        elif type(elem) == P2Pool:
            elem.instance_map(self.depl_mgr.get_deployment_ids_and_instances(MONEROD_FIELD))
        return elem
    

    def get_tui_log(self, job_list: list):
        return self.depl_mgr.job_queue.get_jobs()


    def update_deployment(self, data: dict):
        print(f"OpsMgr:update_deployment(): {data}")

        elem = data[ELEMENT_FIELD]
        self.depl_mgr.update_deployment(elem)
        self.health_mgr.check(elem)
        return elem
        