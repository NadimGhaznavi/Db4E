"""
db4e/Modules/DbCache.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import threading, time
import json, hashlib
from copy import deepcopy

from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.Db4E import Db4E
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig
from db4e.Constants.Defaults import DEPLOYMENT_COL_DEFAULT
from db4e.Constants.Fields import (
    ELEMENT_TYPE_FIELD, DB4E_FIELD, MONEROD_FIELD, MONEROD_REMOTE_FIELD,
    P2POOL_FIELD, P2POOL_REMOTE_FIELD, XMRIG_FIELD, COMPONENTS_FIELD,
    FIELD_FIELD, VALUE_FIELD, INSTANCE_FIELD, OBJECT_ID_FIELD
)

MONERODS = "monerods"
P2POOLS = "p2pools"
XMRIGS = "xmrigs"
MONERODS_MAP = "monerods_map"
P2POOLS_MAP = "p2pools_map"
XMRIGS_MAP = "xmrigs_map"



class DbCache:
    

    def __init__(self, db: DbMgr):
        self.db = db
        self.depl_col = DEPLOYMENT_COL_DEFAULT

        self.db4e = None
        self.monerod_map, self.p2pool_map, self.xmrig_map = {}, {}, {}
        self.id_map = {}

        self._thread = threading.Thread(target=self.bg_build_cache, daemon=True)
        self._lock = threading.RLock()
        self._thread.start()

        self.build_cache()


    def bg_build_cache(self):
        while True:
            self.build_cache()
            time.sleep(2)


    def build_cache(self):
        with self._lock:
            recs = self.db.find_many(self.depl_col, {})
            #print(f"DbCache:build_cache(): # recs: {len(recs)}")

            seen_ids = set()

            for rec in recs:
                elem_type = rec[ELEMENT_TYPE_FIELD]
                obj_id = rec[OBJECT_ID_FIELD]
                seen_ids.add(obj_id)

                if obj_id in self.id_map:
                    # Update existing object in-place
                    elem = self.id_map[obj_id]
                    elem.from_rec(rec)   # you'd need to implement this
                    if elem_type == XMRIG_FIELD:
                        elem.p2pool = self.get_deployment_by_id(elem.parent())
                        self.p2pool_map[elem.p2pool.instance()] = elem.p2pool
                    elif elem_type == P2POOL_FIELD:
                        elem.monerod = self.get_deployment_by_id(elem.parent())
                        self.p2pool_map[elem.instance()] = elem
                    elif elem_type == P2POOL_REMOTE_FIELD:
                        self.p2pool_map[elem.instance()] = elem
                    elif elem_type == MONEROD_FIELD or elem_type == MONEROD_REMOTE_FIELD:
                        self.monerod_map[elem.instance()] = elem
    
                else:
                    # Create new object
                    if elem_type == DB4E_FIELD:
                        elem = Db4E(rec)
                        self.db4e = elem
                    elif elem_type == MONEROD_FIELD:
                        elem = MoneroD(rec)
                        self.monerod_map[elem.instance()] = elem
                    elif elem_type == MONEROD_REMOTE_FIELD:
                        elem = MoneroDRemote(rec)
                        self.monerod_map[elem.instance()] = elem
                    elif elem_type == P2POOL_FIELD:
                        elem = P2Pool(rec)
                        elem.monerod = self.get_deployment_by_id(elem.parent())
                        self.p2pool_map[elem.instance()] = elem
                    elif elem_type == P2POOL_REMOTE_FIELD:
                        elem = P2PoolRemote(rec)
                        self.p2pool_map[elem.instance()] = elem
                    elif elem_type == XMRIG_FIELD:
                        elem = XMRig(rec)
                        if elem.parent():
                            elem.p2pool = self.get_deployment_by_id(elem.parent())
                        self.xmrig_map[elem.instance()] = elem
                    
                    self.id_map[obj_id] = elem

            # Cleanup removed records
            for obj_id in list(self.id_map.keys()):
                if obj_id not in seen_ids:
                    elem = self.id_map.pop(obj_id)
                    if isinstance(elem, XMRig):
                        self.xmrig_map.pop(elem.instance(), None)
                    elif isinstance(elem, MoneroD) or isinstance(elem, MoneroDRemote):
                        self.monerod_map.pop(elem.instance(), None)
                    elif isinstance(elem, P2Pool) or isinstance(elem, P2PoolRemote):
                        self.p2pool_map.pop(elem.instance(), None)

    def delete_one(self, elem):
        with self._lock:
            class_map = {
                Db4E: DB4E_FIELD,
                MoneroD: MONEROD_FIELD,
                MoneroDRemote: MONEROD_REMOTE_FIELD,
                P2Pool: P2POOL_FIELD,
                P2PoolRemote: P2POOL_REMOTE_FIELD,
                XMRig: XMRIG_FIELD
            }
            elem_class = class_map[type(elem)]
            instance = elem.instance()        

            results = self.db.delete_one(
                col_name=self.depl_col,
                    filter = {
                        ELEMENT_TYPE_FIELD: elem_class,
                        COMPONENTS_FIELD: {
                            "$elemMatch": {
                                FIELD_FIELD: INSTANCE_FIELD,
                                VALUE_FIELD: instance
                            }
                        }
                    }
                )
            
            id = elem.id()
            if id in self.id_map:
                del self.id_map[id]

            if elem_class == MONEROD_FIELD or elem_class == MONEROD_REMOTE_FIELD:
                if instance in self.monerod_map:
                    del self.monerod_map[instance]

            elif elem_class == P2POOL_FIELD or elem_class == P2POOL_REMOTE_FIELD:
                if instance in self.p2pool_map:
                    del self.p2pool_map[instance]

            elif elem_class == XMRIG_FIELD:
                if instance in self.xmrig_map:
                    del self.xmrig_map[instance]


    def get_deployment(self, elem_type, instance):
        with self._lock:
            if elem_type == DB4E_FIELD:
                return deepcopy(self.db4e)
            
            if elem_type == MONEROD_FIELD or elem_type == MONEROD_REMOTE_FIELD:
                return deepcopy(self.monerod_map.get(instance))
                    
            elif elem_type == P2POOL_FIELD or elem_type == P2POOL_REMOTE_FIELD:
                print(f"DbCache:get_deployment(): instance: {instance}")
                p2pool = self.p2pool_map.get(instance)
                if type(p2pool) == P2Pool:
                    p2pool.monerod = self.get_deployment_by_id(p2pool.parent())
                print(f"DbCache:get_deployment(): map: {self.p2pool_map}")
                print(f"DbCache:get_deployment(): p2pool: {p2pool}")
                return deepcopy(p2pool)
                    
            elif elem_type == XMRIG_FIELD:
                xmrig = self.xmrig_map.get(instance)
                xmrig.p2pool = self.get_deployment_by_id(xmrig.parent())
                if type(xmrig.p2pool) == P2Pool:
                    xmrig.p2pool.monerod = self.get_deployment_by_id(xmrig.p2pool.parent())
                return deepcopy(xmrig)
            
            else:
                raise ValueError(f"DbCache:get_deployment(): No handler for {elem_type}")


    def get_deployments(self):
        return [self.db4e] + list(self.monerod_map.values()) + \
            list(self.p2pool_map.values()) + list(self.xmrig_map.values())
    

    def get_db4e(self):
        return deepcopy(self.db4e)


    def get_deployment_by_id(self, id):
        with self._lock:
            if id in self.id_map:
                return deepcopy(self.id_map[id])
            else:
                return False


    def get_deployment_ids_and_instances(self, elem_type):
        with self._lock:
            if elem_type == P2POOL_FIELD or elem_type == P2POOL_REMOTE_FIELD:
                instance_map = {}
                for p2pool in self.p2pool_map.values():
                    instance_map[p2pool.instance()] = p2pool.id()
                print(f"DbCache:get_deployment_ids_and_instances(): {instance_map}")
                return instance_map
                    
            elif elem_type == MONEROD_FIELD or elem_type == MONEROD_REMOTE_FIELD:
                instance_map = {}
                for monerod in self.monerod_map.values():
                    instance_map[monerod.instance()] = monerod.id()
                return instance_map


    def get_monerods(self):
        return list(self.monerod_map.values())


    def get_p2pools(self):
        return list(self.p2pool_map.values())


    def get_xmrigs(self):
        return list(self.xmrig_map.values())


    def insert_one(self, elem):
        with self._lock:
            msgs = elem.pop_msgs()
            self.db.insert_one(self.depl_col, elem.to_rec())
            elem.push_msgs(msgs)

            print(f"DbCache:insert_one(): before {self.p2pool_map.values()}")
            if type(elem) == MoneroD or type(elem) == MoneroDRemote:
                self.monerod_map[elem.instance()] = elem
                self.id_map[elem.id()] = elem

            elif type(elem) == P2Pool or type(elem) == P2PoolRemote:
                self.p2pool_map[elem.instance()] = elem
                self.id_map[elem.id()] = elem

            elif type(elem) == XMRig:
                self.xmrig_map[elem.instance()] = elem
                self.id_map[elem.id()] = elem

            print(f"DbCache:insert_one(): after {self.p2pool_map.values()}")
            return elem


    def update_one(self, elem):
        with self._lock:
            print(f"DbCache:update_one(): {elem}")
            self.db.update_one(self.depl_col, { OBJECT_ID_FIELD: elem.id() }, elem.to_rec())

            if type(elem) == MoneroD or type(elem) == MoneroDRemote:
                self.monerod_map[elem.instance()] = elem
                self.id_map[elem.id()] = elem

            elif type(elem) == P2Pool or type(elem) == P2PoolRemote:
                self.p2pool_map[elem.instance()] = elem
                self.id_map[elem.id()] = elem

            elif type(elem) == XMRig:
                self.xmrig_map[elem.instance()] = elem
                self.id_map[elem.id()] = elem

            return elem

