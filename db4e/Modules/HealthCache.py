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

from db4e.Modules.HealthMgr import HealthMgr
from db4e.Modules.DeplClient import DeplClient

from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField

MONERODS = "monerods"
P2POOLS = "p2pools"
XMRIGS = "xmrigs"
MONERODS_MAP = "monerods_map"
P2POOLS_MAP = "p2pools_map"
XMRIGS_MAP = "xmrigs_map"

class HealthCache:


    def __init__(self, health_mgr: HealthMgr, depl_client: DeplClient):
        self.health_mgr = health_mgr
        self.depl_client = depl_client

        self.monerods, self.p2pools, self.xmrigs = [], [], []
        self.monerods_map, self.p2pools_map, self.xmrigs_map = {}, {}, {}

        self.refresh_now = {
            DElem.MONEROD: True,
            DElem.P2POOL: True,
            DElem.XMRIG: True,
        }
        self.refresh_monerods()
        self.refresh_p2pools()
        self.refresh_xmrigs()

        self._thread = threading.Thread(target=self.bg_refresh, daemon=True)
        self._thread.start()

    
    def bg_refresh(self):
        while True:
            time.sleep(10)
            self.refresh_now[DElem.MONEROD] = True
            time.sleep(10)
            self.refresh_now[DElem.P2POOL] = True
            time.sleep(10)
            self.refresh_now[DElem.XMRIG] = True


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


        setattr(self, target_list_name, new_list)
        setattr(self, target_map_name, new_map)

        self.refresh_now[element_type] = False


    def get_deployment(self, elem_type, instance):
        if elem_type == DElem.MONEROD:
            return self.monerods_map.get(instance)
        elif elem_type == DElem.P2POOL:
            return self.p2pools_map.get(instance)
        elif elem_type == DElem.XMRIG:
            return self.xmrigs_map.get(instance)
        else:
            raise ValueError(f"Unsupported element type: {elem_type}")

        
    def get_monerods(self) -> list:
        self.refresh_monerods()
        return self.monerods


    def get_p2pools(self) -> list:
        self.refresh_p2pools()
        return self.p2pools


    def get_xmrigs(self) -> list:
        self.refresh_xmrigs()
        return self.xmrigs
    

    def hash_unit(self, unit) -> str:
        serialized = json.dumps(unit.to_rec(), sort_keys=True, default=str)
        return hashlib.blake2b(serialized.encode(), digest_size=16).hexdigest()


    def hash_units(self, units) -> str:
        dict_list = []
        for unit in units:
            dict_list.append(unit.to_rec())
        serialized = json.dumps(dict_list, sort_keys=True, default=str)
        return hashlib.blake2b(serialized.encode(), digest_size=16).hexdigest()


    def refresh_monerods(self):
        self.refresh_elements(DElem.MONEROD, self.depl_client.get_monerods, MONERODS, MONERODS_MAP)


    def refresh_p2pools(self):
        self.refresh_elements(DElem.P2POOL, self.depl_client.get_p2pools, P2POOLS, P2POOLS_MAP)


    def refresh_xmrigs(self):
        self.refresh_elements(DElem.XMRIG, self.depl_client.get_xmrigs, XMRIGS, XMRIGS_MAP)




