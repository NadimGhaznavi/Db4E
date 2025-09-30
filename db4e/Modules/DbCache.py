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
from db4e.Modules.MiningDb import MiningDb
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig
from db4e.Modules.XMRigRemote import XMRigRemote


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
    

    def __init__(self, db: DbMgr, mining_db=None):
        self.db = db
        self.mining_db = mining_db
        self.depl_col = DDef.DEPLOYMENT_COL

        self.db4es_map = {}
        self.monerod_map, self.monerod_remote_map = {}, {}
        self.p2pool_map, self.p2pool_remote_map, self.int_p2pool_map = {}, {}, {}
        self.xmrig_map, self.xmrig_remote_map = {}, {}
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

            ## Get remote xmrig instances
            # The remote xmrig list is based on real-time miner stats, not the depl collection
            remote_xmrig_recs = self.mining_db.get_xmrigs_remote()
            for rec in remote_xmrig_recs:
                xmrig = XMRigRemote(rec)
                self.xmrig_remote_map[xmrig.instance()] = xmrig
                self.id_map[xmrig.id()] = xmrig
            
            # Remove the local deployments from the map, the local instances
            # show up in the depl collection's real-time miner stats
            for xmrig in self.xmrig_map.values():
                if xmrig.instance() in self.xmrig_remote_map:
                    del self.xmrig_remote_map[xmrig.instance()]

            for rec in recs:
                elem_type = rec[DField.ELEMENT_TYPE]
                #print(f"DbCache:build_cache(): [{count}/{len(recs)}]: {elem_type}")
                #print(f"DbCache:build_cache(): elem_type: {elem_type}")
                #print(f"DbCache:build_cache(): rec: {rec}")
                count += 1

                obj_id = rec[DField.OBJECT_ID]
                seen_ids.add(obj_id)

                if obj_id in self.id_map:
                    # Update existing object in-place
                    elem = self.id_map[obj_id]
                    elem.from_rec(rec)

                    if elem_type == DElem.DB4E:
                        elem.instance_map(self.get_deployment_ids_and_instances(DElem.MONEROD))
                        self.db4es_map[elem.instance()] = elem

                    elif elem_type == DElem.MONEROD:
                        self.monerod_map[elem.instance()] = elem

                    elif  elem_type == DElem.MONEROD_REMOTE:
                        self.monerod_remote_map[elem.instance()] = elem
    
                    elif elem_type == DElem.P2POOL:
                        elem.instance_map(self.get_deployment_ids_and_instances(DElem.MONEROD))
                        if elem.parent():
                            elem.monerod = self.get_deployment_by_id(elem.parent())
                        self.p2pool_map[elem.instance()] = elem
                    
                    elif elem_type == DElem.P2POOL_REMOTE:
                        self.p2pool_remote_map[elem.instance()] = elem
                    
                    elif elem_type == DElem.INT_P2POOL:
                        elem.instance_map(self.get_deployment_ids_and_instances(DElem.MONEROD))
                        if elem.parent():
                            elem.monerod = self.get_deployment_by_id(elem.parent())
                        self.int_p2pool_map[elem.instance()] = elem
                        
                    elif elem_type == DElem.XMRIG:
                        elem.p2pool = self.get_deployment_by_id(elem.parent())
                        if type(elem.p2pool) == P2Pool:
                            elem.p2pool.monerod = self.get_deployment_by_id(elem.p2pool.parent())
                            elem.instance_map(self.get_deployment_ids_and_instances(DElem.P2POOL))
                        self.xmrig_map[elem.instance()] = elem
                    
                else:
                    # Create new object
                    if elem_type == DElem.DB4E:
                        elem = Db4E(rec)
                        elem.instance_map(self.get_deployment_ids_and_instances(DElem.MONEROD))
                        self.db4es_map[elem.instance()] = elem
                        
                    elif elem_type == DElem.MONEROD:
                        elem = MoneroD(rec)
                        self.monerod_map[elem.instance()] = elem
                        
                    elif elem_type == DElem.MONEROD_REMOTE:
                        elem = MoneroDRemote(rec)
                        self.monerod_remote_map[elem.instance()] = elem

                    elif elem_type == DElem.P2POOL:
                        elem = P2Pool(rec)
                        elem.instance_map(self.get_deployment_ids_and_instances(DElem.MONEROD))
                        if elem.parent():
                            elem.monerod = self.get_deployment_by_id(elem.parent())
                        self.p2pool_map[elem.instance()] = elem

                    elif elem_type == DElem.P2POOL_REMOTE:
                        elem = P2PoolRemote(rec)
                        self.p2pool_remote_map[elem.instance()] = elem

                    elif elem_type == DElem.INT_P2POOL:
                        elem = InternalP2Pool(rec)
                        if elem.parent():
                            elem.monerod = self.get_deployment_by_id(elem.parent())
                        self.int_p2pool_map[elem.instance()] = elem

                    elif elem_type == DElem.XMRIG:
                        elem = XMRig(rec)
                        if elem.parent():
                            elem.p2pool = self.get_deployment_by_id(elem.parent())
                            if type(elem.p2pool) == P2Pool:
                                elem.p2pool.monerod = self.get_deployment_by_id(elem.p2pool.parent())
                        self.xmrig_map[elem.instance()] = elem
                    
                    self.id_map[obj_id] = elem
                
                #print(f"DbCache:build_cache(): db4es_map {self.db4es_map}")
                #print(f"DbCache:build_cache(): monerod_map {self.monerod_map}")
                #print(f"DbCache:build_cache(): monerod_remote_map {self.monerod_remote_map}")
                #print(f"DbCache:build_cache(): p2pool_map {self.p2pool_map}")
                #print(f"DbCache:build_cache(): p2pool_remote_map {self.p2pool_remote_map}")
                #print(f"DbCache:build_cache(): int_p2pool_map {self.int_p2pool_map}")
                #print(f"DbCache:build_cache(): xmrig_map {self.xmrig_map}")
                #print(f"DbCache:build_cache(): id_map {self.id_map}")
                #print(f"DbCache:build_cache(): seen_ids {seen_ids}")


            # Cleanup removed records
            for obj_id in list(self.id_map.keys()):
                if obj_id not in seen_ids:
                    elem = self.id_map.pop(obj_id)
                    elem_type = elem.elem_type()
                    if type(elem) ==  MoneroD:
                        self.monerod_map.pop(elem.instance(), None)
                    elif type(elem) == MoneroDRemote:
                        self.monerod_remote_map.pop(elem.instance(), None)
                    elif type(elem) == P2Pool:
                        self.p2pool_map.pop(elem.instance(), None)
                    elif type(elem) == P2PoolRemote:
                        self.p2pool_remote_map.pop(elem.instance(), None)
                    elif type(elem) == InternalP2Pool:
                        self.int_p2pool_map.pop(elem.instance(), None)
                    elif type(elem) == XMRig:
                        self.xmrig_map.pop(elem.instance(), None)
            

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
            elem_type = class_map[type(elem)]
            instance = elem.instance()        

            results = self.db.delete_one(
                col_name=self.depl_col,
                    filter = {
                        DField.ELEMENT_TYPE: elem_type,
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

            elif elem_type == DElem.MONEROD:
                if instance in self.monerod_map:
                    del self.monerod_map[instance]

            elif elem_type == DElem.MONEROD_REMOTE:
                if instance in self.monerod_remote_map:
                    del self.monerod_remote_map[instance]

            elif elem_type == DElem.P2POOL:
                if instance in self.p2pool_map:
                    del self.p2pool_map[instance]

            elif elem_type == DElem.P2POOL_REMOTE:
                if instance in self.p2pool_remote_map:
                    del self.p2pool_remote_map[instance]

            elif elem_type == DElem.XMRIG:
                if instance in self.xmrig_map:
                    del self.xmrig_map[instance]


    def get_deployment(self, elem_type, instance):
        with self._lock:

            # Db4E
            if elem_type == DElem.DB4E:
                elem = deepcopy(self.db4es_map.get(instance))
            
            # MoneroD
            elif elem_type == DElem.MONEROD:
                elem = deepcopy(self.monerod_map.get(instance))
            
            elif elem_type == DElem.MONEROD_REMOTE:
                elem = deepcopy(self.monerod_remote_map.get(instance))

            # P2Pool
            elif elem_type == DElem.P2POOL:
                elem = deepcopy(self.p2pool_map.get(instance))
            
            # Remote P2Pool
            elif elem_type == DElem.P2POOL_REMOTE:
                elem = deepcopy(self.p2pool_remote_map.get(instance))

            # Internal P2Pool
            elif elem_type == DElem.INT_P2POOL:
                elem = deepcopy(self.int_p2pool_map.get(instance))

            # XMRig
            elif elem_type == DElem.XMRIG:
                elem = deepcopy(self.xmrig_map.get(instance))
            
            # Remote XMRig
            elif elem_type == DElem.XMRIG_REMOTE:
                elem = deepcopy(self.xmrig_remote_map.get(instance))
            
            else:
                raise ValueError(f"DbCache:get_deployment(): No handler for {elem_type}")

            if not elem:
                self.build_cache()
                # Db4E
                if elem_type == DElem.DB4E:
                    elem = deepcopy(self.db4es_map.get(instance))
                
                # MoneroD
                if elem_type == DElem.MONEROD:
                    elem = deepcopy(self.monerod_map.get(instance))
                
                elif elem_type == DElem.MONEROD_REMOTE:
                    elem = deepcopy(self.monerod_remote_map.get(instance))

                # P2Pool
                elif elem_type == DElem.P2POOL:
                    elem = deepcopy(self.p2pool_map.get(instance))
                
                # Remote P2Pool
                elif elem_type == DElem.P2POOL_REMOTE:
                    elem = deepcopy(self.p2pool_remote_map.get(instance))

                # Internal P2Pool
                elif elem_type == DElem.INT_P2POOL:
                    elem = deepcopy(self.int_p2pool_map.get(instance))

                # Internal P2Pool
                elif elem_type == DElem.INT_P2POOL:
                    elem = deepcopy(self.int_p2pool_map.get(instance))

                # XMRig
                elif elem_type == DElem.XMRIG:
                    elem = deepcopy(self.xmrig_map.get(instance))
                
                # Remote XMRig
                elif elem_type == DElem.XMRIG_REMOTE:
                    elem = deepcopy(self.xmrig_remote_map.get(instance))
                
                return elem
            return elem

    def get_deployments(self):
        return deepcopy(list(self.db4es_map.values())) + \
            deepcopy(list(self.monerod_map.values())) + \
            deepcopy(list(self.monerod_remote_map.values())) + \
            deepcopy(list(self.p2pool_map.values())) + \
            deepcopy(list(self.p2pool_remote_map.values())) +\
            deepcopy(list(self.int_p2pool_map.values())) + \
            deepcopy(list(self.xmrig_map.values())) + \
            deepcopy(list(self.xmrig_remote_map.values()))


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
                for remote_p2pool in self.p2pool_remote_map.values():
                    instance_map[remote_p2pool.instance()] = remote_p2pool.id()
                return instance_map
                    
            elif elem_type == DElem.MONEROD or elem_type == DElem.MONEROD_REMOTE:
                instance_map = {}
                for monerod in self.monerod_map.values():
                    instance_map[monerod.instance()] = monerod.id()
                for remote_monerod in self.monerod_remote_map.values():
                    instance_map[remote_monerod.instance()] = remote_monerod.id()
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


    def get_db4es(self):
        return deepcopy(list(self.db4es_map.values()))


    def get_monerods(self):
        return deepcopy(list(self.monerod_map.values()))


    def get_monerods_remote(self):
        return deepcopy(list(self.monerod_remote_map.values()))


    def get_p2pools(self):
        return deepcopy(list(self.p2pool_map.values()))


    def get_p2pools_remote(self):
        return deepcopy(list(self.p2pool_remote_map.values()))


    def get_int_p2pools(self):
        return deepcopy(list(self.int_p2pool_map.values()))


    def get_xmrigs(self):
        return deepcopy(list(self.xmrig_map.values()))


    def get_xmrigs_remote(self):
        return deepcopy(list(self.xmrig_remote_map.values()))


    def insert_one(self, elem):
        with self._lock:
            msgs = elem.pop_msgs()
            object_id = self.db.insert_one(self.depl_col, elem.to_rec())
            elem.id(object_id)
            for msg in msgs:
                elem.add_msg(msg)
            self.id_map[elem.id()] = elem
            return object_id
        

    def update_one(self, elem):
        with self._lock:
            self.db.update_one(self.depl_col, { DField.OBJECT_ID: elem.id() }, elem.to_rec())

            if type(elem) == Db4E:
                self.db4es_map[elem.instance()] = elem

            elif type(elem) == MoneroD:
                self.monerod_map[elem.instance()] = elem

            elif type(elem) == MoneroDRemote:
                self.monerod_remote_map[elem.instance()] = elem

            elif type(elem) == P2Pool:
                self.p2pool_map[elem.instance()] = elem

            elif type(elem) == P2PoolRemote:
                self.p2pool_remote_map[elem.instance()] = elem

            elif type(elem) == InternalP2Pool:
                self.int_p2pool_map[elem.instance()] = elem

            elif type(elem) == XMRig:
                self.xmrig_map[elem.instance()] = elem

            self.id_map[elem.id()] = elem
            return elem

