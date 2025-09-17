"""
db4e/Modules/DeplClient.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from typing import overload

from db4e.Modules.DeplBase import DeplBase
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



class DeplClient(DeplBase):

    # add_deployment() is overloaded ...
    @overload
    def add_deployment(self, elem: Db4E) -> Db4E: ...
    @overload
    def add_deployment(self, elem: MoneroD) -> MoneroD: ...
    @overload
    def add_deployment(self, elem: MoneroDRemote) -> MoneroDRemote: ...
    @overload
    def add_deployment(self, elem: P2Pool) -> P2Pool: ...
    @overload
    def add_deployment(self, elem: P2PoolRemote) -> P2PoolRemote: ...
    @overload
    def add_deployment(self, elem: XMRig) -> XMRig: ...
    
    # update_deployment() is overloaded ...
    @overload
    def update_deployment(self, elem: Db4E) -> Db4E: ...
    @overload
    def update_deployment(self, elem: MoneroD) -> MoneroD: ...
    @overload
    def update_deployment(self, elem: MoneroDRemote) -> MoneroDRemote: ...
    @overload
    def update_deployment(self, elem: P2Pool) -> P2Pool: ...
    @overload
    def update_deployment(self, elem: P2PoolRemote) -> P2PoolRemote: ...
    @overload
    def update_deployment(self, elem: XMRig) -> XMRig: ...


    def __init__(self, db: DbMgr, db_cache: DbCache):
        self.db_cache = db_cache
        self.job_queue = JobQueue(db=db)


    def add_deployment(self, elem):
        # Check for duplicate instance names and missing fields
        self.check_instance_and_fields(elem)

        class_map = {
            Db4E: DElem.DB4E,
            MoneroD: DElem.MONEROD,
            MoneroDRemote: DElem.MONEROD_REMOTE,
            P2Pool: DElem.P2POOL,
            P2PoolRemote: DElem.P2POOL_REMOTE,
            XMRig: DElem.XMRIG,
        }

        # Create an add job
        elem_type = class_map[type(elem)]
        
        job = Job(op=DJob.NEW, instance=elem.instance(), elem_type=elem_type, elem=elem)
        self.job_queue.post_job(job)
        return elem
    

    def delete_deployment(self, form_data):
        # Create a delete job
        elem = form_data[DField.ELEMENT]
        job = Job(op=DJob.DELETE, instance=elem.instance(), elem_type=elem.elem_type(), elem=elem)
        self.job_queue.post_job(job)


    def disable_deployment(self, form_data):
        # Create a disable job
        elem = form_data[DField.ELEMENT]
        job = Job(op=DJob.DISABLE, instance=elem.instance(), elem_type=elem.elem_type(), elem=elem)
        self.job_queue.post_job(job)


    def enable_deployment(self, form_data):
        # Create a delete job
        elem = form_data[DField.ELEMENT]
        job = Job(op=DJob.ENABLE, instance=elem.instance(), elem_type=elem.elem_type(), elem=elem)
        self.job_queue.post_job(job)


    def get_deployment(self, elem_type: str, instance=None):
        return self.db_cache.get_deployment(elem_type, instance)


    def get_deployment_ids_and_instances(self, elem_type):
        return self.db_cache.get_deployment_ids_and_instances(elem_type)
    

    def get_deployments(self):
        return self.db_cache.get_deployments()


    def get_monerods(self) -> list[MoneroD | MoneroDRemote]:
        return self.db_cache.get_monerods()


    def get_new(self, elem_type):

        if elem_type == DElem.MONEROD:
            return MoneroD()
        elif elem_type == DElem.MONEROD_REMOTE:
            return MoneroDRemote()
        elif elem_type == DElem.P2POOL:
            p2pool = P2Pool()
            db4e = self.db_cache.get_db4e()
            p2pool.user_wallet(db4e.user_wallet())
            return p2pool
        elif elem_type == DElem.P2POOL_REMOTE:
            return P2PoolRemote()
        elif elem_type == DElem.XMRIG:
            return XMRig()
        else:
            raise ValueError(f"DeploymentMgr:get_new(): No handler for {elem_type}")


    def get_p2pools(self) -> list[P2Pool | P2PoolRemote]:
        return self.db_cache.get_p2pools()


    def get_xmrigs(self) -> list[XMRig]:
        return self.db_cache.get_xmrigs()


    def is_initialized(self):
        db4e = self.db_cache.get_db4e()
        if db4e:
            if db4e.vendor_dir() and db4e.user_wallet():
                return True
            else:
                return False
        else:
            return False


    def update_deployment(self, form_data):
        # Chceck for duplicate intance names and missing fields
        elem = form_data[DField.ELEMENT]
        self.check_instance_and_fields(elem)

        # Create an update job
        if type(elem) == Db4E:
            job = Job(op=DJob.UPDATE, instance=DLabel.DB4E, elem_type=elem.elem_type(), elem=elem)
        else:
            job = Job(op=DJob.UPDATE, instance=elem.instance(), elem_type=elem.elem_type(), elem=elem)
        self.job_queue.post_job(job)
        return elem
    
