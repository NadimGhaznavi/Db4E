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

from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DDebug import DDebug

DDebug.FUNCTION = False

MONERODS = DField.MONERODS
P2POOLS = DField.P2POOLS
XMRIGS = DField.XMRIGS

MONERODS_MAP = DField.MONERODS_MAP
P2POOLS_MAP = DField.P2POOLS_MAP
XMRIGS_MAP = DField.XMRIGS_MAP

REFRESH_INTERVAL = 5

class HealthCache:


    def __init__(self, depl_client: DeplClient):
        self.depl_client = depl_client
        self.health_mgr = HealthMgr()

        self.db4e = None
        self.monerods, self.p2pools, self.xmrigs = [], [], []
        self.monerods_map, self.p2pools_map, self.xmrigs_map = {}, {}, {}

        self.refresh_now = {
            DElem.DB4E: True,
            DElem.MONEROD: True,
            DElem.P2POOL: True,
            DElem.XMRIG: True,
        }
        self.refresh_db4e()
        self.refresh_monerods()
        self.refresh_p2pools()
        self.refresh_xmrigs()

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


    def check(self, elem):
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:check(): {elem}")
        """
        if type(elem) == MoneroD or type(elem) == MoneroDRemote:
            try:
                return self.monerods_map[elem.instance()]
            except KeyError:
                return self.force_refresh(DElem.MONEROD, elem.instance())
        elif type(elem) == P2Pool or type(elem) == P2PoolRemote:
            try:
                return self.p2pools_map[elem.instance()]
            except KeyError:
                return self.force_refresh(DElem.P2POOL, elem.instance())
        elif type(elem) == XMRig:
            try:
                return self.xmrigs_map[elem.instance()]
            except KeyError:
                return self.force_refresh(DElem.XMRIG, elem.instance())
        """
        
        if type(elem) == Db4E:
            db4e = self.depl_client.get_db4e()
            self.health_mgr.check(db4e)
            self.db4e = db4e
            return self.db4e
        elif type(elem) == MoneroD or type(elem) == MoneroDRemote:
            try:
                return self.monerods_map[elem.instance()][DField.INSTANCE]
            except KeyError:
                return None
        elif type(elem) == P2Pool or type(elem) == P2PoolRemote:
            try:
                return self.p2pools_map[elem.instance()][DField.INSTANCE]
            except KeyError:
                return None
        elif type(elem) == XMRig:
            try:
                return self.xmrigs_map[elem.instance()][DField.INSTANCE]
            except KeyError:
                return None
        else:
            raise ValueError(f"Unsupported element type: {type(elem)}")


    def force_refresh(self, elem_type: str, instance=None):
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:force_refresh(): {elem_type}, {instance}")
        if instance:
            elem = self.depl_client.get_deployment(elem_type, instance)
            elem = self.health_mgr.check(elem)
            if type(elem) == MoneroD or type(elem) == MoneroDRemote:
                self.monerods_map[elem.instance()] = elem
                return elem
            elif type(elem) == P2Pool or type(elem) == P2PoolRemote:
                self.p2pools_map[elem.instance()] = elem
                return elem
            elif type(elem) == XMRig:
                self.xmrigs_map[elem.instance()] = elem
                return elem
            return elem
        else:
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
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:refresh_elements(): {element_type}")

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
            #print(f"HealthCache:refresh_elements(): {element_type}: {new_list}")


        setattr(self, target_list_name, new_list)
        setattr(self, target_map_name, new_map)

        self.refresh_now[element_type] = False


    def get_deployment(self, elem_type, instance):
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:get_deployment(): {elem_type}, {instance}")
        if elem_type == DElem.MONEROD:
            return self.monerods_map.get(instance)[DField.INSTANCE]
        elif elem_type == DElem.P2POOL:
            return self.p2pools_map.get(instance)[DField.INSTANCE]
        elif elem_type == DElem.XMRIG:
            return self.xmrigs_map.get(instance)[DField.INSTANCE]
        else:
            raise ValueError(f"Unsupported element type: {elem_type}")

        
    def get_monerods(self) -> list:
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:get_monerods():")
        self.refresh_monerods()
        return self.monerods


    def get_p2pools(self) -> list:
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:get_p2pools():")
        self.refresh_p2pools()
        return self.p2pools


    def get_xmrigs(self) -> list:
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:get_xmrigs():")
        self.refresh_xmrigs()
        return self.xmrigs
    

    def hash_unit(self, unit) -> str:
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:hash_unit(): {unit}")
        serialized = json.dumps(unit.to_rec(), sort_keys=True, default=str)
        return hashlib.blake2b(serialized.encode(), digest_size=16).hexdigest()


    def hash_units(self, units) -> str:
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:hash_units(): {units}")
        dict_list = []
        for unit in units:
            dict_list.append(unit.to_rec())
        serialized = json.dumps(dict_list, sort_keys=True, default=str)
        return hashlib.blake2b(serialized.encode(), digest_size=16).hexdigest()


    def refresh_db4e(self):
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:refresh_db4e():")
        self.refresh_elements(DElem.DB4E, self.depl_client.get_db4e, DElem.DB4E, DElem.DB4E)

    def refresh_monerods(self):
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:refresh_monerods():")
        self.refresh_elements(DElem.MONEROD, self.depl_client.get_monerods, MONERODS, MONERODS_MAP)


    def refresh_p2pools(self):
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:refresh_p2pools():")
        self.refresh_elements(DElem.P2POOL, self.depl_client.get_p2pools, P2POOLS, P2POOLS_MAP)


    def refresh_xmrigs(self):
        if DDebug.FUNCTION:
            print(f"DEBUG HealthCache:refresh_xmrigs():")
        self.refresh_elements(DElem.XMRIG, self.depl_client.get_xmrigs, XMRIGS, XMRIGS_MAP)




