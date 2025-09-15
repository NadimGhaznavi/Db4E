"""
db4e/Modules/DeplBase.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
from typing import overload

from db4e.Modules.Db4E import Db4E
from db4e.Modules.DbCache import DbCache
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.Job import Job
from db4e.Modules.JobQueue import JobQueue
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig


from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DJob import DJob
from db4e.Constants.DStatus import DStatus
from db4e.Constants.DLabel import DLabel



class DeplBase:


    def __init__(self):
        db_mgr = DbMgr()
        self.db_cache = DbCache(db=db_mgr)
        self.job_queue = JobQueue(db=db_mgr)


    # check_instance_and_fields is overloaded
    @overload
    def check_instance_and_fields(self, elem: Db4E) -> Db4E: ...
    @overload
    def check_instance_and_fields(self, elem: MoneroD) -> MoneroD: ...
    @overload
    def check_instance_and_fields(self, elem: MoneroDRemote) -> MoneroDRemote: ...
    @overload
    def check_instance_and_fields(self, elem: P2Pool) -> P2Pool: ...
    @overload
    def check_instance_and_fields(self, elem: P2PoolRemote) -> P2PoolRemote: ...
    @overload
    def check_instance_and_fields(self, elem: XMRig) -> XMRig: ...


    def check_db4e_fields(self, db4e: Db4E) -> bool:
        required = [
            db4e.donation_wallet(),
            db4e.vendor_dir(),
        ]
        return not all(required)


    def check_instance_and_fields(self, elem):
        elem_class = type(elem)

        # Check if an instance of the same basic type already exists
        instance_exists = False
        if isinstance(elem, MoneroD) or isinstance(elem, MoneroDRemote):
            instance_exists = self.instance_exists(elem, self.get_monerods())
        elif isinstance(elem, P2Pool) or isinstance(elem, P2PoolRemote):
            instance_exists = self.instance_exists(elem, self.get_p2pools())
        elif isinstance(elem, XMRig):
            instance_exists = self.instance_exists(elem, self.get_xmrigs())

        if instance_exists:
                msg = f"A deployment with the same name ({elem.instance()}) " \
                    f"already exists"
                elem.msg(DLabel.MONEROD, DStatus.WARN, msg)
                return elem

        # Make sure we have all the required fields
        missing_fields = False
        if elem_class == Db4E:
            missing_fields = self.check_db4e_fields(elem)
        elif elem_class == MoneroD:
            missing_fields = self.check_monerod_fields(elem)
        elif elem_class == MoneroDRemote:
            missing_fields = self.check_monerod_remote_fields(elem)
        elif elem_class == P2Pool:
            missing_fields = self.check_p2pool_fields(elem)
        elif elem_class == P2PoolRemote:
            missing_fields = self.check_p2pool_remote_fields(elem)
        elif elem_class == XMRig:
            missing_fields = self.check_xmrig_fields(elem)
    
        if missing_fields:
            return elem


    def check_monerod_fields(self, monerod: MoneroD) -> bool:
        required = [
            monerod.instance(),
            monerod.in_peers(),
            monerod.out_peers(),
            monerod.p2p_bind_port(),
            monerod.rpc_bind_port(),
            monerod.zmq_pub_port(),
            monerod.zmq_rpc_port(),
            monerod.log_level(),
            monerod.max_log_files(),
            monerod.max_log_size(),
            monerod.priority_node_1(),
            monerod.priority_port_1(),
            monerod.priority_node_2(),
            monerod.priority_port_2(),
        ]
        return not all(required)
    
    
    def check_monerod_remote_fields(self, monerod: MoneroDRemote) -> bool:
        required = [ 
            monerod.instance(), 
            monerod.ip_addr(), 
            monerod.rpc_bind_port(), 
            monerod.zmq_pub_port() 
            ]
        return not all(required)


    def check_p2pool_fields(self, p2pool: P2Pool) -> bool:
        required = [
            p2pool.instance(),
            p2pool.in_peers(),
            p2pool.out_peers(),
            p2pool.p2p_port(),
            p2pool.stratum_port(),
            p2pool.log_level(),
        ]
        return not all(required)


    def check_p2pool_remote_fields(self, p2pool: P2PoolRemote) -> bool:
        required = [
            p2pool.instance(),
            p2pool.ip_addr(),
            p2pool.stratum_port(),
        ]
        return not all(required)


    def check_xmrig_fields(self, xmrig: XMRig) -> bool:
        required = [
            xmrig.instance(),
            xmrig.num_threads(),
            xmrig.parent(),
        ]
        return not all(required)
    

    def get_deployment_by_id(self, id):
        return self.db_cache.get_deployment_by_id(id)


    def instance_exists(self, elem, collection) -> bool:
        return any(e.instance() == elem.instance() for e in collection)


