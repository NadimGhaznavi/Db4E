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
from db4e.Modules.InternalP2Pool import InternalP2Pool
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig

from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DDef import DDef

MONERODS = "monerods"
P2POOLS = "p2pools"
XMRIGS = "xmrigs"
MONERODS_MAP = "monerods_map"
P2POOLS_MAP = "p2pools_map"
XMRIGS_MAP = "xmrigs_map"

POLL_INTERVAL = 5

class DbCache:
    

    def __init__(self, db: DbMgr):
        self.db = db
        self.depl_col = DDef.DEPLOYMENT_COL

        self.db4e = None
        self.monerod_map, self.p2pool_map, self.xmrig_map, self.int_p2pool_map = \
            {}, {}, {}, {}
        self.id_map = {}

        self._thread = threading.Thread(target=self.bg_build_cache, daemon=True)
        self._lock = threading.RLock()
        self._thread.start()

        self.build_cache()


    def bg_build_cache(self):
        while True:
            self.build_cache()
            time.sleep(POLL_INTERVAL)


    def build_cache(self):
        with self._lock:
            recs = self.db.find_many(self.depl_col, {})
            #print(f"DbCache:build_cache(): # recs: {len(recs)}")

            seen_ids = set()

            count = 1
            for rec in recs:
                elem_type = rec[DField.ELEMENT_TYPE]
                #print(f"[{count}/{len(recs)}]: {elem_type}")
                count += 1

                obj_id = rec[DField.OBJECT_ID]
                seen_ids.add(obj_id)

                if obj_id in self.id_map:
                    # Update existing object in-place
                    elem = self.id_map[obj_id]
                    elem.from_rec(rec)

                    if elem_type == DElem.DB4E:
                        self.db4e = elem

                    elif elem_type == DElem.XMRIG:
                        elem.p2pool = self.get_deployment_by_id(elem.parent())
                        if type(elem.p2pool) == P2Pool or type(elem.p2pool) == P2PoolRemote:
                            self.p2pool_map[elem.p2pool.instance()] = elem.p2pool
                    
                    elif elem_type == DElem.INT_P2POOL:
                        if elem.parent():
                            elem.monerod = self.get_deployment_by_id(elem.parent())
                            if type(elem.monerod) == MoneroD or type(elem.monerod) == MoneroDRemote:
                                self.monerod_map[elem.monerod.instance()] = elem.monerod
                            self.int_p2pool_map[elem.instance()] = elem

                    elif elem_type == DElem.P2POOL:
                        elem.monerod = self.get_deployment_by_id(elem.parent())
                        if type(elem.monerod) == MoneroD or type(elem.monerod) == MoneroDRemote:
                            self.monerod_map[elem.monerod.instance()] = elem.monerod
                    
                    elif elem_type == DElem.P2POOL_REMOTE:
                        self.p2pool_map[elem.instance()] = elem
                    
                    elif elem_type == DElem.MONEROD or elem_type == DElem.MONEROD_REMOTE:
                        self.monerod_map[elem.instance()] = elem
    
                else:
                    # Create new object
                    if elem_type == DElem.DB4E:
                        # Special case this
                        db4e_rec = self.db.find_one(self.depl_col, {DField.ELEMENT_TYPE: DElem.DB4E})
                        elem = Db4E(db4e_rec)
                    elif elem_type == DElem.MONEROD:
                        elem = MoneroD(rec)
                        self.monerod_map[elem.instance()] = elem
                    elif elem_type == DElem.MONEROD_REMOTE:
                        elem = MoneroDRemote(rec)
                        self.monerod_map[elem.instance()] = elem
                    elif elem_type == DElem.P2POOL:
                        elem = P2Pool(rec)
                        elem.monerod = self.get_deployment_by_id(elem.parent())
                        self.p2pool_map[elem.instance()] = elem
                    elif elem_type == DElem.P2POOL_REMOTE:
                        elem = P2PoolRemote(rec)
                        self.p2pool_map[elem.instance()] = elem
                    elif elem_type == DElem.INT_P2POOL:
                        elem = InternalP2Pool(rec)
                        self.int_p2pool_map[elem.instance()] = elem
                    elif elem_type == DElem.XMRIG:
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
                Db4E: DElem.DB4E,
                MoneroD: DElem.MONEROD,
                MoneroDRemote: DElem.MONEROD_REMOTE,
                P2Pool: DElem.P2POOL,
                P2PoolRemote: DElem.P2POOL_REMOTE,
                XMRig: DElem.XMRIG
            }
            elem_class = class_map[type(elem)]
            instance = elem.instance()        

            results = self.db.delete_one(
                col_name=self.depl_col,
                    filter = {
                        DField.ELEMENT_TYPE: elem_class,
                        DField.COMPONENTS: {
                            "$elemMatch": {
                                DField.FIELD: DField.INSTANCE,
                                DField.VALUE: instance
                            }
                        }
                    }
                )
            
            id = elem.id()
            if id in self.id_map:
                del self.id_map[id]

            if elem_class == DElem.MONEROD or elem_class == DElem.MONEROD_REMOTE:
                if instance in self.monerod_map:
                    del self.monerod_map[instance]

            elif elem_class == DElem.P2POOL or elem_class == DElem.P2POOL_REMOTE:
                if instance in self.p2pool_map:
                    del self.p2pool_map[instance]

            elif elem_class == DElem.XMRIG:
                if instance in self.xmrig_map:
                    del self.xmrig_map[instance]


    def get_deployment(self, elem_type, instance=None):
        #print(f"DbCache:get_deployment(): {elem_type} {instance}")
        #print(f"DbCache:get_deployment(): monerod_map: {self.monerod_map}")
        #print(f"DbCache:get_deployment(): p2pool_map: {self.p2pool_map}")
        #print(f"DbCache:get_deployment(): int_p2pool_map: {self.int_p2pool_map}")
        #print(f"DbCache:get_deployment(): xmrig_map: {self.xmrig_map}")
        with self._lock:
            if elem_type == DElem.DB4E:
                return deepcopy(self.db4e)
            
            if elem_type == DElem.MONEROD or elem_type == DElem.MONEROD_REMOTE:
                return deepcopy(self.monerod_map.get(instance))

            elif elem_type == DElem.P2POOL or elem_type == DElem.P2POOL_REMOTE:
                p2pool = self.p2pool_map.get(instance)                

                if type(p2pool) == P2Pool:
                    p2pool.monerod = self.get_deployment_by_id(p2pool.parent())                        
                return deepcopy(p2pool)
                    
            elif elem_type == DElem.INT_P2POOL:
                return deepcopy(self.int_p2pool_map.get(instance))

            elif elem_type == DElem.XMRIG:
                xmrig = self.xmrig_map.get(instance)
                #print(f"DbCache:get_deployment(): xmrig: {xmrig}")
                xmrig.p2pool = self.get_deployment_by_id(xmrig.parent())
                if elem_type == DElem.P2POOL:
                    xmrig.p2pool.monerod = self.get_deployment_by_id(xmrig.p2pool.parent())
                return deepcopy(xmrig)
            
            else:
                raise ValueError(f"DbCache:get_deployment(): No handler for {elem_type}")


    def get_deployments(self):
        return [self.db4e] + list(self.monerod_map.values()) + \
            list(self.p2pool_map.values()) + list(self.xmrig_map.values()) + \
            list(self.int_p2pool_map.values())


    def get_deployment_by_id(self, id):
        with self._lock:
            if id in self.id_map:
                return deepcopy(self.id_map[id])
            else:
                return False


    def get_deployment_ids_and_instances(self, elem_type):
        with self._lock:
            if elem_type == DElem.P2POOL or elem_type == DElem.P2POOL_REMOTE:
                instance_map = {}
                for p2pool in self.p2pool_map.values():
                    instance_map[p2pool.instance()] = p2pool.id()
                #print(f"DbCache:get_deployment_ids_and_instances(): {instance_map}")
                return instance_map
                    
            elif elem_type == DElem.MONEROD or elem_type == DElem.MONEROD_REMOTE:
                instance_map = {}
                for monerod in self.monerod_map.values():
                    instance_map[monerod.instance()] = monerod.id()
                #print(f"DbCache:get_deployment_ids_and_instances(): {instance_map}")
                return instance_map

    def get_downstream(self, elem):
        if type(elem) == MoneroD or type(elem) == MoneroDRemote:
            p2pools = []
            for p2pool in self.p2pool_map.values():
                if isinstance(p2pool, P2Pool):
                    if p2pool.parent() == elem.id():
                        p2pools.append(deepcopy(p2pool))
            for int_p2pool in self.int_p2pool_map.values():
                if int_p2pool.parent() == elem.id():
                    p2pools.append(deepcopy(int_p2pool))
            return p2pools
        elif type(elem) == P2Pool or type(elem) == P2PoolRemote:
            xmrigs = []
            for xmrig in self.xmrig_map.values():
                if xmrig.parent() == elem.id():
                    xmrigs.append(deepcopy(xmrig))
            return xmrigs


    def get_internal_p2pools(self):
        return list(self.int_p2pool_map.values())


    def get_monerods(self):
        return list(self.monerod_map.values())


    def get_p2pools(self):
        return list(self.p2pool_map.values())


    def get_primary_monerod(self):
        for monerod in self.monerod_map.values():
            if monerod.primary_server():
                return monerod
        return None


    def get_xmrigs(self):
        return list(self.xmrig_map.values())


    def insert_one(self, elem):
        with self._lock:
            msgs = elem.pop_msgs()
            rec = self.db.insert_one(self.depl_col, elem.to_rec())
            elem.from_rec(rec)
            for msg in msgs:
                elem.add_msg(msg)

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


    def update_one(self, elem):
        with self._lock:
            print(f"DbCache:update_one(): {elem}")
            self.db.update_one(self.depl_col, { DField.OBJECT_ID: elem.id() }, elem.to_rec())

            if type(elem) == Db4E:
                self.db4e = elem
                self.id_map[elem.id()] = elem
                print(f"DbCache:update_one(): db4e.vendor_dir(): {elem.vendor_dir()}")

            elif type(elem) == MoneroD or type(elem) == MoneroDRemote:
                self.monerod_map[elem.instance()] = elem
                self.id_map[elem.id()] = elem

            elif type(elem) == P2Pool or type(elem) == P2PoolRemote:
                self.p2pool_map[elem.instance()] = elem
                self.id_map[elem.id()] = elem

            elif type(elem) == InternalP2Pool:
                self.int_p2pool_map[elem.instance()] = elem
                self.id_map[elem.id()] = elem

            elif type(elem) == XMRig:
                self.xmrig_map[elem.instance()] = elem
                self.id_map[elem.id()] = elem

            return elem

