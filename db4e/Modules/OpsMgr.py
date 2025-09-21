"""
db4e/Modules/OpsMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.Db4E import Db4E
from db4e.Modules.DbCache import DbCache
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


    def __init__(self, depl_client: DeplClient, health_cache: HealthCache, db_cache: DbCache):
        self.depl_client = depl_client
        self.health_cache = health_cache
        self.db_cache = db_cache
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

        if elem_type == DElem.XMRIG_REMOTE:
            return self.db_cache.get_xmrig_remote(instance=instance)


        elem = self.health_cache.get_deployment(elem_type=elem_type, instance=instance)
        if type(elem) == P2Pool:
            elem.instance_map(self.db_cache.get_deployment_ids_and_instances(DElem.MONEROD))
        elif type(elem) == XMRig:
            elem.instance_map(self.db_cache.get_deployment_ids_and_instances(DElem.P2POOL))
        
        return elem


    def get_monerods(self) -> list:
        return self.health_cache.get_monerods()


    def get_p2pools(self) -> list:
        return self.health_cache.get_p2pools()


    def get_xmrigs_remote(self) -> list:
        return self.health_cache.get_xmrigs_remote()


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
        