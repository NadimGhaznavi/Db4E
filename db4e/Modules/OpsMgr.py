"""
db4e/Modules/OpsMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from datetime import datetime, timedelta
from collections import defaultdict


from db4e.Modules.Db4E import Db4E
from db4e.Modules.DbCache import DbCache
from db4e.Modules.DeplClient import DeplClient
from db4e.Modules.HealthCache import HealthCache
from db4e.Modules.MiningDb import MiningDb
from db4e.Modules.MiningETL import MiningETL
from db4e.Modules.OpsDb import OpsETL
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.InternalP2Pool import InternalP2Pool
from db4e.Modules.XMRig import XMRig
from db4e.Modules.XMRigRemote import XMRigRemote

from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DDef import DDef
from db4e.Constants.DPane import DPane
from db4e.Constants.DMongo import DMongo



class OpsMgr:


    def __init__(
        self, depl_client: DeplClient, health_cache: HealthCache, 
        db_cache: DbCache, mining_db: MiningDb, ops_etl: OpsETL):

        self.depl_client = depl_client
        self.health_cache = health_cache
        self.db_cache = db_cache
        self.db = db_cache.db
        self.mining_db = mining_db
        self.mining_etl = MiningETL(self.mining_db)
        self.depl_col = DDef.DEPLOYMENT_COL
        self.ops_etl = ops_etl
        self.ops_db = ops_etl.ops_db



    def add_deployment(self, form_data: dict):
        elem = form_data[DField.ELEMENT]
        elem = self.depl_client.add_deployment(elem)
        self.health_cache.check(elem)
        return elem
    

    def hashrates(self, form_data: dict):
        elem = form_data[DField.ELEMENT]

        if type(elem) == P2Pool:
            elem.hashrate(self.mining_etl.get_pool_hashrate(instance=elem.instance()))
            elem.hashrates(self.mining_etl.get_pool_hashrates(instance=elem.instance()))

        if type(elem) == InternalP2Pool:
            elem.hashrate(self.mining_etl.get_chain_hashrate(instance=elem.instance()))
            elem.hashrates(self.mining_etl.get_chain_hashrates(instance=elem.instance()))
            elem.blocks_found(self.mining_etl.get_block_found_events(instance=elem.instance()))

        elif type(elem) == XMRig:
            elem.hashrates(self.mining_etl.get_miner_hashrates(elem.instance()))
            elem.hashrate(self.mining_etl.get_miner_hashrate(elem.instance()))
            elem.uptime(self.mining_etl.get_miner_uptime(elem.instance()))

        elif type(elem) == XMRigRemote:
            print(self.mining_etl.get_miner_hashrates(elem.instance()))
            elem.hashrates(self.mining_etl.get_miner_hashrates(elem.instance()))

        return elem
 
   
    def get_deployment(self, elem_type, instance=None):
        if type(elem_type) == dict:
            instance = elem_type[DField.INSTANCE]
            elem_type = elem_type[DField.ELEMENT_TYPE]

        elem = self.health_cache.get_deployment(elem_type=elem_type, instance=instance)

        if type(elem) == Db4E:
            elem.instance_map(self.db_cache.get_deployment_ids_and_instances(DElem.MONEROD))

        elif type(elem) == P2Pool or type(elem) == InternalP2Pool:
            elem.instance_map(self.db_cache.get_deployment_ids_and_instances(DElem.MONEROD))
            if elem.parent() != DField.DISABLE:
                elem.monerod = self.db_cache.get_deployment_by_id(elem.parent())

        elif type(elem) == XMRig:
            elem.instance_map(self.db_cache.get_deployment_ids_and_instances(DElem.P2POOL))
            if elem.parent() != DField.DISABLE:
                elem.p2pool = self.db_cache.get_deployment_by_id(elem.parent())

        elif type(elem) == XMRigRemote:
            # The Remote XMRig pane displays analytics
            return self.hashrates(form_data={DField.ELEMENT: elem})

        return elem

    ### Get deployments by type...
    
    def get_monerods(self) -> list:
        return self.health_cache.get_monerods()
    
    def get_monerods_remote(self) -> list:
        return self.health_cache.get_monerods_remote()

    def get_p2pools(self) -> list:
        return self.health_cache.get_p2pools()

    def get_p2pools_remote(self) -> list:
        return self.health_cache.get_p2pools_remote()

    def get_int_p2pools(self) -> list:
        return self.health_cache.get_int_p2pools()

    def get_xmrigs(self) -> list:
        return self.health_cache.get_xmrigs()

    def get_xmrigs_remote(self) -> list:
        return self.health_cache.get_xmrigs_remote()
    
    ### End of get deployments by type...


    def get_remote_xmrig_timestamp(self, xmrig: XMRigRemote):
        return self.mining_etl.get_remote_xmrig_timestamp(xmrig.instance())


    def get_uptime(self, form_data: dict):
        return self.ops_etl.get_ops_summary()


    def get_new(self, form_data: dict):
        elem = self.depl_client.get_new(form_data[DField.ELEMENT_TYPE])
        return elem
    

    def get_tui_log(self, job_list: list):
        return self.depl_client.job_queue.get_jobs()
    

    def get_runtime_log(self, event_list: list):
        return self.ops_db.get_ops_events()
    

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
    

        