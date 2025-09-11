"""
db4e/Modules/OpsMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
import os

from db4e.Modules import (
    Db4E, DbMgr, DeploymentMgr, HealthMgr, HealthCache, XMRig, P2Pool)
from db4e.Constants import DElem, DField, DDef



class OpsMgr:


    def __init__(self):
        self.db = DbMgr()
        self.depl_mgr = DeploymentMgr()
        self.health_mgr = HealthMgr()
        self.health_cache = HealthCache(health_mgr=self.health_mgr, depl_mgr=self.depl_mgr)
        self.depl_col = DDef.DEPLOYMENT_COL


    def add_deployment(self, form_data: dict):
        #print(f"OpsMgr:add_deployment(): {elem_type}")
        elem = form_data[DField.ELEMENT]
        #print(f"OpsMgr:add_deployment(): {elem.to_rec()}")
        
        # TODO Make sure the remote monerod and monerod records don't share an instance name.
        # TODO Same for p2pool.
        elem = self.depl_mgr.add_deployment(elem)
        self.health_mgr.check(elem)
        return elem
 
   
    def get_deployment(self, elem_type, instance=None):
        if type(elem_type) == dict:
            if DField.INSTANCE in elem_type:
                instance = elem_type[DField.INSTANCE]
            elem_type = elem_type[DField.ELEMENT_TYPE]

        elem = self.depl_mgr.get_deployment(elem_type=elem_type, instance=instance)

        if not elem:
            if elem_type == DElem.MONEROD:
                elem = self.depl_mgr.get_deployment(
                    elem_type=DElem.MONEROD_REMOTE, instance=instance)
                elem_type = DElem.MONEROD_REMOTE
            elif elem_type == DElem.P2POOL:
                elem = self.depl_mgr.get_deployment(
                    elem_type=DElem.P2POOL_REMOTE, instance=instance)
                elem_type = DElem.P2POOL_REMOTE
        
        if type(elem) == Db4E:
            elem.instance_map(self.depl_mgr.get_deployment_ids_and_instances(DElem.MONEROD))
        elif type(elem) == XMRig:
            elem.instance_map(self.depl_mgr.get_deployment_ids_and_instances(DElem.P2POOL))
        elif type(elem) == P2Pool:
            elem.instance_map(self.depl_mgr.get_deployment_ids_and_instances(DElem.MONEROD))

        elem = self.health_mgr.check(elem)
        return elem


    def get_monerods(self) -> list:
        return self.health_cache.get_monerods()


    def get_p2pools(self) -> list:
        return self.health_cache.get_p2pools()


    def get_xmrigs(self) -> list:
        return self.health_cache.get_xmrigs()


    def get_new(self, form_data: dict):
        elem = self.depl_mgr.get_new(form_data[DField.ELEMENT_TYPE])
        if type(elem) == XMRig:
            elem.instance_map(self.depl_mgr.get_deployment_ids_and_instances(DElem.P2POOL))
        elif type(elem) == P2Pool:
            elem.instance_map(self.depl_mgr.get_deployment_ids_and_instances(DElem.MONEROD))
        return elem
    

    def get_tui_log(self, job_list: list):
        return self.depl_mgr.job_queue.get_jobs()


    def log_viewer(self, form_data: dict):
        elem_type = form_data[DField.ELEMENT_TYPE]
        instance = form_data[DField.INSTANCE_FIELD]
        elem = self.depl_mgr.get_deployment(
            elem_type=elem_type, instance=instance)
        return elem


    def plot(self, plot_metadata: dict):
        return plot_metadata


    def update_deployment(self, data: dict):
        print(f"OpsMgr:update_deployment(): {data}")

        elem = data[DField.ELEMENT]
        self.depl_mgr.update_deployment(elem)
        self.health_mgr.check(elem)
        return elem
        