"""
db4e/Modules/HealthCache.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import json, hashlib
import threading, time
from copy import deepcopy

from db4e.Modules.DbCache import DbCache
from db4e.Modules.HealthMgr import HealthMgr
from db4e.Modules.JobQueue import JobQueue
from db4e.Modules.DeplClient import DeplClient
from db4e.Modules.Db4E import Db4E
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig
from db4e.Modules.XMRigRemote import XMRigRemote


from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DDebug import DDebug

DDebug.FUNCTION = False

REFRESH_INTERVAL = 5

class HealthCache:


    def __init__(self, depl_client: DeplClient):
        self.depl_client = depl_client
        self.health_mgr = HealthMgr()

        self.db4e = None
        self.monerods, self.p2pools, self.xmrigs, self.xmrigs_remote = [], [], [], []
        self.monerods_map, self.p2pools_map, self.xmrigs_map, self.xmrigs_remote_map = \
            {}, {}, {}, {}
        self.id_map = {}

        self.refresh_now = {
            DElem.DB4E: True,
            DElem.MONEROD: True,
            DElem.P2POOL: True,
            DElem.XMRIG: True,
            DElem.XMRIG_REMOTE: True,
        }
        self.refresh_db4e()
        self.refresh_monerods()
        self.refresh_p2pools()
        self.refresh_xmrigs()
        self.refresh_xmrigs_remote()

        self._thread = threading.Thread(target=self.bg_refresh, daemon=True)
        self._thread.start()

    
    def bg_refresh(self):
        while True:
            self.refresh_now[DElem.MONEROD] = True
            time.sleep(REFRESH_INTERVAL)
            self.refresh_now[DElem.P2POOL] = True
            time.sleep(REFRESH_INTERVAL)
            self.refresh_now[DElem.XMRIG] = True
            time.sleep(REFRESH_INTERVAL)
            self.refresh_now[DElem.XMRIG_REMOTE] = True
            time.sleep(REFRESH_INTERVAL)


    def check(self, elem):
        # Db4E        
        if type(elem) == Db4E:
            db4e = self.depl_client.get_db4e()
            self.health_mgr.check(db4e)
            self.db4e = db4e
            return deepcopy(self.db4e)
        
        # MoneroD and Remote MoneroD
        elif type(elem) == MoneroD or type(elem) == MoneroDRemote:
            try:
                return deepcopy(self.monerods_map[elem.instance()][DField.INSTANCE])
            except KeyError:
                print(f"HealthCache:check(): [remote]monerod key error: {elem}")
                return None
            
        # P2Pool
        elif type(elem) == P2Pool: 
            try:
                return deepcopy(self.p2pools_map[elem.instance()][DField.INSTANCE])
            except KeyError:
                print(f"HealthCache:check(): P2Pool key error: {elem}")
                return None
            
        # Remote P2Pool
        elif type(elem) == P2PoolRemote:
            try:
                return deepcopy(self.p2pools_map[elem.instance()])
            except KeyError:
                print(f"HealthCache:check(): P2PoolRemote key error: {elem}")
                return None

        # XMRig
        elif type(elem) == XMRig:
            try:
                return deepcopy(self.xmrigs_map[elem.instance()][DField.INSTANCE])
                    
            except KeyError:
                print(f"HealthCache:check(): XMRig key error: {elem}")
                return None
        
        # Remote XMRig
        elif type(elem) == XMRigRemote:
            try:
                return deepcopy(self.xmrigs_remote_map[elem.instance()])
            except KeyError:
                print(f"HealthCache:check(): XMRigRemote key error: {elem}")
                return None
            
        else:
            raise ValueError(f"Unsupported element type: {type(elem)}")


    def force_refresh(self, elem_type: str):
        self.refresh_now[elem_type] = True


    def refresh_elements(self, element_type: str, get_elements_fn, 
                         target_list_name: str, target_map_name: str):
        """
        Generic refresh for an element type (monerod, p2pool, xmrig, ...).

        Args:
            element_type: Name of the type (for clarity/logging).
            get_elements_fn: Callable returning a list of element objects.
            target_list_name: Attribute name for the list (e.g. 'monerods').
            target_map_name: Attribute name for the map (e.g. 'monerods_map').
        """
        if element_type == DElem.DB4E:
            db4e = get_elements_fn()
            self.db4e = self.health_mgr.check(db4e)
            self.refresh_now[DElem.DB4E] = False
            return
                
        elements = get_elements_fn()

        new_map = {}
        new_list = []

        old_map = getattr(self, target_map_name, {})
        force_refresh = self.refresh_now[element_type]

        for elem in elements:
            #print(f"HealthCache:refresh_elements(): {elem}")
            instance = elem.instance()
            new_hash = self.hash_unit(elem)
            if instance in old_map:
                old_entry = old_map[instance]
                if old_entry[DField.HASH] != new_hash or force_refresh:
                    elem = self.health_mgr.check(elem)

                else:
                    elem = old_entry[DField.INSTANCE]
                    
            else:                    
                elem = self.health_mgr.check(elem)

            new_map[instance] = {
                DField.HASH: new_hash,
                DField.INSTANCE: elem,
            }

            new_list.append(elem)
            self.id_map[elem.id()] = elem

        setattr(self, target_list_name, new_list)
        setattr(self, target_map_name, new_map)

        #print(f"{element_type}\n{get_elements_fn}\n{target_list_name}\n{target_map_name}\nList: {new_list}")
        self.refresh_now[element_type] = False


    def get_deployment(self, elem_type, instance):
        if elem_type == DElem.MONEROD:
            return deepcopy(self.monerods_map[instance][DField.INSTANCE])
        
        elif elem_type == DElem.P2POOL:
            p2pool = self.p2pools_map.get(instance)[DField.INSTANCE]
            return deepcopy(p2pool)
        

        
        elif elem_type == DElem.XMRIG:
            xmrig = self.xmrigs_map.get(instance)[DField.INSTANCE]
            return deepcopy(xmrig)
            
        else:
            raise ValueError(f"Unsupported element type: {elem_type}")

        
    def get_monerods(self) -> list:
        self.refresh_monerods()
        return deepcopy(self.monerods)


    def get_p2pools(self) -> list:
        self.refresh_p2pools()
        return deepcopy(self.p2pools)


    def get_xmrigs_remote(self) -> list:
        self.refresh_xmrigs_remote()
        return deepcopy(self.xmrigs_remote)


    def get_xmrigs(self) -> list:
        self.refresh_xmrigs()
        return deepcopy(self.xmrigs)
    

    def hash_unit(self, unit) -> str:
        serialized = json.dumps(unit.to_rec(), sort_keys=True, default=str)
        return hashlib.blake2b(serialized.encode(), digest_size=16).hexdigest()


    def hash_units(self, units) -> str:
        dict_list = []
        for unit in units:
            dict_list.append(unit.to_rec())
        serialized = json.dumps(dict_list, sort_keys=True, default=str)
        return hashlib.blake2b(serialized.encode(), digest_size=16).hexdigest()


    def refresh_db4e(self):
        self.refresh_elements(DElem.DB4E, self.depl_client.get_db4e, DElem.DB4E, DElem.DB4E)


    def refresh_id(self, object_id):
        elem = self.depl_client.get_deployment_by_id(object_id)
        print(f"HealthCache:refresh_id(): ERROR: {elem} not in cache")
        

    def UNUSED_refresh_instance(self, elem_type, instance):
        # MoneroD and Remote MoneroD
        if elem_type == DElem.MONEROD or elem_type == DElem.MONEROD_REMOTE:
            monerod = self.depl_client.get_deployment(elem_type, instance)
            self.health_mgr.check(monerod)
            self.monerods_map[monerod.instance()] = monerod
            self.id_map[monerod.id()] = monerod

        # P2Pool
        elif elem_type == DElem.P2POOL:
            p2pool = self.depl_client.get_deployment(elem_type, instance)
            p2pool.monerod = self.depl_client.get_deployment_by_id(p2pool.parent())
            self.health_mgr.check(p2pool)
            self.p2pools_map[p2pool.instance()] = p2pool
            self.id_map[p2pool.id()] = p2pool

        # Remote P2Pool
        elif elem_type == DElem.P2POOL_REMOTE:
            p2pool = self.depl_client.get_deployment(elem_type, instance)
            self.health_mgr.check(p2pool)
            self.p2pools_map[p2pool.instance()] = p2pool
            self.id_map[p2pool.id()] = p2pool

        # XMRig
        elif elem_type == DElem.XMRIG:
            xmrig = self.depl_client.get_deployment(elem_type, instance)
            #xmrig.p2pool = self.depl_client.get_deployment_by_id(xmrig.parent())
            #if xmrig.p2pool == DElem.P2POOL:
            #    xmrig.p2pool.monerod = self.depl_client.get_deployment_by_id(xmrig.p2pool.parent())
            self.health_mgr.check(xmrig)
            self.xmrigs_map[xmrig.instance()] = xmrig
            self.id_map[xmrig.id()] = xmrig

        # Remote XMRig
        elif elem_type == DElem.XMRIG_REMOTE:
            xmrig = self.depl_client.get_deployment(elem_type, instance)
            self.health_mgr.check(xmrig)
            self.xmrigs_remote_map[xmrig.instance()] = xmrig
            self.id_map[xmrig.id()] = xmrig


    def refresh_monerods(self):
        self.refresh_elements(
            DElem.MONEROD, self.depl_client.get_monerods, 
            DField.MONERODS, DField.MONERODS_MAP)


    def refresh_p2pools(self):
        self.refresh_elements(
            DElem.P2POOL, self.depl_client.get_p2pools, 
            DField.P2POOLS, DField.P2POOLS_MAP)


    def refresh_xmrigs_remote(self):
        self.refresh_elements(
            DElem.XMRIG_REMOTE, self.depl_client.get_xmrigs_remote, 
            DField.XMRIGS_REMOTE, DField.XMRIGS_REMOTE_MAP)


    def refresh_xmrigs(self):
        self.refresh_elements(
            DElem.XMRIG, self.depl_client.get_xmrigs, 
            DField.XMRIGS, DField.XMRIGS_MAP)



