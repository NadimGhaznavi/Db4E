"""
db4e/Modules/OpsMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.Db4E import Db4E
from db4e.Modules.DeplClient import DeplClient
from db4e.Modules.HealthMgr import HealthMgr
from db4e.Modules.HealthCache import HealthCache
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.XMRig import XMRig
from db4e.Modules.DbMgr import DbMgr
from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DDef import DDef
from db4e.Constants.DPane import DPane





class OpsMgr:


    def __init__(self, depl_client: DeplClient, health_cache: HealthCache):
        self.depl_client = depl_client
        self.health_cache = health_cache
        self.depl_col = DDef.DEPLOYMENT_COL


    def add_deployment(self, form_data: dict):
        #print(f"OpsMgr:add_deployment(): {elem_type}")
        elem = form_data[DField.ELEMENT]
        #print(f"OpsMgr:add_deployment(): {elem.to_rec()}")
        
        # TODO Make sure the remote monerod and monerod records don't share an instance name.
        # TODO Same for p2pool.
        elem = self.depl_client.add_deployment(elem)
        self.health_cache.check(elem)
        return elem
 
   
    def get_deployment(self, elem_type, instance=None):
        if type(elem_type) == dict:
            if DField.INSTANCE in elem_type:
                instance = elem_type[DField.INSTANCE]
            elem_type = elem_type[DField.ELEMENT_TYPE]

        elem = self.depl_client.get_deployment(elem_type=elem_type, instance=instance)
        checked_elem = self.health_cache.check(elem)
        if checked_elem:
            # Return the elem with health check messages
            return checked_elem
        
        # The item isn't in the HealthMgr cache yet, return it with no health check messages
        return elem


    def get_monerods(self) -> list:
        return self.health_cache.get_monerods()


    def get_p2pools(self) -> list:
        return self.health_cache.get_p2pools()


    def get_xmrigs(self) -> list:
        return self.health_cache.get_xmrigs()


    def get_new(self, form_data: dict):
        elem = self.depl_client.get_new(form_data[DField.ELEMENT_TYPE])
        return elem
    

    def get_tui_log(self, job_list: list):
        return self.depl_client.job_queue.get_jobs() 


    def log_viewer(self, form_data: dict):
        elem_type = form_data[DField.ELEMENT_TYPE]
        instance = form_data[DField.INSTANCE]
        elem = self.depl_client.get_deployment(
            elem_type=elem_type, instance=instance)
        return elem


    def plot(self, plot_metadata: dict):
        return plot_metadata


    def set_donations(self, form_data: dict):
        return DPane.DONATIONS


    def update_deployment(self, data: dict):
        print(f"OpsMgr:update_deployment(): {data}")

        elem = data[DField.ELEMENT]
        self.depl_client.update_deployment(elem)
        self.health_cache.check(elem)
        return elem
        