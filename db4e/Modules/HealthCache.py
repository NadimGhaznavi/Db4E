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
from db4e.Modules.InternalP2Pool import InternalP2Pool
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

REFRESH_INTERVAL = 1

class HealthCache:


    def __init__(self, depl_client: DeplClient):
        self.depl_client = depl_client
        self.health_mgr = HealthMgr()

        self.db4es_map = {}
        self.monerods_map, self.monerods_remote_map = {}, {}
        self.p2pools_map, self.p2pools_remote_map, self.int_p2pools_map = {}, {}, {}
        self.xmrigs_map, self.xmrigs_remote_map = {}, {}
        self.id_map = {}

        self.refresh_now = {
            DElem.DB4E: True,
            DElem.MONEROD: True,
            DElem.MONEROD_REMOTE: True,
            DElem.P2POOL: True,
            DElem.P2POOL_REMOTE: True,
            DElem.INT_P2POOL: True,
            DElem.XMRIG: True,
            DElem.XMRIG_REMOTE: True,
        }
        self.refresh_db4es()
        self.refresh_monerods()
        self.refresh_monerods_remote()
        self.refresh_p2pools()
        self.refresh_p2pools_remote()
        self.refresh_int_p2pools()
        self.refresh_xmrigs()
        self.refresh_xmrigs_remote()

        self._thread = threading.Thread(target=self.bg_refresh, daemon=True)
        self._thread.start()

    
    def bg_refresh(self):
        while True:
            self.refresh_now[DElem.DB4E] = True
            time.sleep(REFRESH_INTERVAL)
            self.refresh_now[DElem.MONEROD] = True
            time.sleep(REFRESH_INTERVAL)
            self.refresh_now[DElem.MONEROD_REMOTE] = True
            time.sleep(REFRESH_INTERVAL)
            self.refresh_now[DElem.P2POOL] = True
            time.sleep(REFRESH_INTERVAL)
            self.refresh_now[DElem.P2POOL_REMOTE] = True
            time.sleep(REFRESH_INTERVAL)
            self.refresh_now[DElem.INT_P2POOL] = True
            time.sleep(REFRESH_INTERVAL)
            self.refresh_now[DElem.XMRIG] = True
            time.sleep(REFRESH_INTERVAL)
            self.refresh_now[DElem.XMRIG_REMOTE] = True
            time.sleep(REFRESH_INTERVAL)


    def check(self, elem):
        # Db4E        
        if type(elem) == Db4E:
            try:
                return deepcopy(self.db4es_map[DField.INSTANCE][DField.INSTANCE])
            except KeyError:
                print(f"HealthCache:check(): Db4E key error: {elem}")
                return None
        
        # Monero
        elif type(elem) == MoneroD:
            try:
                return deepcopy(self.monerods_map[elem.instance()][DField.INSTANCE])
            except KeyError:
                print(f"HealthCache:check(): Monero key error: {elem}")
                return None

        # Remote Monero
        elif type(elem) == MoneroDRemote:
            try:
                return deepcopy(self.monerods_remote_map[elem.instance()][DField.INSTANCE])
            except KeyError:
                print(f"HealthCache:check(): Remote Monero key error: {elem}")

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
                return deepcopy(self.p2pools_remote_map[elem.instance()][DField.INSTANCE])
            except KeyError:
                print(f"HealthCache:check(): Remote P2Pool key error: {elem}")
                return None

        # Internal P2Pool
        elif type(elem) == InternalP2Pool:
            try:
                return deepcopy(self.int_p2pools_map[elem.instance()][DField.INSTANCE])
            except KeyError:
                print(f"HealthCache:check(): InternalP2Pool key error: {elem}")
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


    def refresh_elements(
            self, element_type: str, get_elements_fn: str, target_map_name: str):
        """
        Generic refresh for an element type (monerod, p2pool, xmrig, ...).

        Args:
            element_type: Name of the type (for clarity/logging).
            get_elements_fn: Callable returning a list of element objects.
            target_list_name: Attribute name for the list (e.g. 'monerods').
            target_map_name: Attribute name for the map (e.g. 'monerods_map').
        """
        elements = get_elements_fn()
        new_map = {}
        old_map = getattr(self, target_map_name, {})

        force_refresh = self.refresh_now[element_type]

        for elem in elements:
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

            self.id_map[elem.id()] = elem

        setattr(self, target_map_name, new_map)

        self.refresh_now[element_type] = False
        #print(f"HealthCache:refresh_elements(): int_p2pools_map: {self.int_p2pools_map}")


    def get_deployment(self, elem_type, instance):
        if elem_type == DElem.DB4E:
            if instance not in self.db4es_map:
                self.refresh_db4es()
            return deepcopy(self.db4es_map[instance][DField.INSTANCE])
        
        elif elem_type == DElem.MONEROD:
            return deepcopy(self.monerods_map.get(instance)[DField.INSTANCE])
        
        elif elem_type == DElem.MONEROD_REMOTE:
            return deepcopy(self.monerods_remote_map.get(instance)[DField.INSTANCE])
        
        elif elem_type == DElem.P2POOL:
            return deepcopy(self.p2pools_map.get(instance)[DField.INSTANCE])
        
        elif elem_type == DElem.P2POOL_REMOTE:
            return deepcopy(self.p2pools_remote_map.get(instance)[DField.INSTANCE])
        
        elif elem_type == DElem.INT_P2POOL:
            return deepcopy(self.int_p2pools_map.get(instance)[DField.INSTANCE])
        
        elif elem_type == DElem.XMRIG:
            return deepcopy (self.xmrigs_map.get(instance)[DField.INSTANCE])

        elif elem_type == DElem.XMRIG_REMOTE:
            return deepcopy(self.xmrigs_remote_map.get(instance)[DField.INSTANCE])
            
        else:
            raise ValueError(f"Unsupported element type: {elem_type}")


    def get_db4es(self) -> Db4E:
        self.refresh_db4es()
        elem_list = []
        for elem in self.db4es_map.values():
            elem_list.append(deepcopy(elem[DField.INSTANCE]))
        return elem_list
    

    def get_monerods(self) -> list:
        self.refresh_monerods()
        elem_list = []
        for elem in self.monerods_map.values():
            elem_list.append(deepcopy(elem[DField.INSTANCE]))
        return elem_list


    def get_monerods_remote(self) -> list:
        self.refresh_monerods_remote()
        elem_list = []
        for elem in self.monerods_remote_map.values():
            elem_list.append(deepcopy(elem[DField.INSTANCE]))
        return elem_list


    def get_p2pools(self) -> list:
        self.refresh_p2pools()
        elem_list = []
        for elem in self.p2pools_map.values():
            elem_list.append(deepcopy(elem[DField.INSTANCE]))
        return elem_list


    def get_p2pools_remote(self) -> list:
        self.refresh_p2pools_remote()
        elem_list = []
        for elem in self.p2pools_remote_map.values():
            elem_list.append(deepcopy(elem[DField.INSTANCE]))
        return elem_list


    def get_int_p2pools(self) -> list:
        self.refresh_int_p2pools()
        elem_list = []
        for elem in self.int_p2pools_map.values():
            elem_list.append(deepcopy(elem[DField.INSTANCE]))
        return elem_list


    def get_xmrigs(self) -> list:
        self.refresh_xmrigs()
        elem_list = []
        for elem in self.xmrigs_map.values():
            elem_list.append(deepcopy(elem[DField.INSTANCE]))
        return elem_list


    def get_xmrigs_remote(self) -> list:
        self.refresh_xmrigs_remote()
        elem_list = []
        for elem in self.xmrigs_remote_map.values():
            elem_list.append(deepcopy(elem[DField.INSTANCE]))
        return elem_list


    def hash_unit(self, unit) -> str:
        serialized = json.dumps(unit.to_rec(), sort_keys=True, default=str)
        return hashlib.blake2b(serialized.encode(), digest_size=16).hexdigest()


    def hash_units(self, units) -> str:
        dict_list = []
        for unit in units:
            dict_list.append(unit.to_rec())
        serialized = json.dumps(dict_list, sort_keys=True, default=str)
        return hashlib.blake2b(serialized.encode(), digest_size=16).hexdigest()


    def refresh_db4es(self):
        self.refresh_elements(
            DElem.DB4E, self.depl_client.get_db4es, DField.DB4E_MAP)


    def refresh_monerods(self):
        self.refresh_elements(
            DElem.MONEROD, self.depl_client.get_monerods, DField.MONERODS_MAP)


    def refresh_monerods_remote(self):
        self.refresh_elements(
            DElem.MONEROD_REMOTE, self.depl_client.get_monerods_remote, 
            DField.MONERODS_REMOTE_MAP)


    def refresh_p2pools(self):
        self.refresh_elements(
            DElem.P2POOL, self.depl_client.get_p2pools, DField.P2POOLS_MAP)


    def refresh_p2pools_remote(self):
        self.refresh_elements(
            DElem.P2POOL_REMOTE, self.depl_client.get_p2pools_remote, 
            DField.P2POOLS_REMOTE_MAP)


    def refresh_int_p2pools(self):
        self.refresh_elements(
            DElem.INT_P2POOL, self.depl_client.get_int_p2pools, DField.INT_P2POOLS_MAP)


    def refresh_xmrigs(self):
        self.refresh_elements(
            DElem.XMRIG, self.depl_client.get_xmrigs, DField.XMRIGS_MAP)


    def refresh_xmrigs_remote(self):
        self.refresh_elements(
            DElem.XMRIG_REMOTE, self.depl_client.get_xmrigs_remote, 
            DField.XMRIGS_REMOTE_MAP)





