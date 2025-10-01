"""
db4e/Job.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

import uuid
from datetime import datetime

from db4e.Modules.Db4E import Db4E
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig

from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DJob import DJob


class Job:


    def __init__(self, op=None, elem_type=None, instance=None, elem=None):
        self._attempts = 0
        self._created_at = datetime.now()
        self._element = elem
        self._element_type = elem_type
        self._instance = instance
        self._job_id = str(uuid.uuid4())
        self._msg = ""
        self._object_id = None
        self._op = op
        self._status = DJob.PENDING
        self._updated_at = datetime.now()


    def __repr__(self):
        return f"{type(self).__name__}({self.op()}): {self.status()} {self.elem_type()}/{self.instance()}"


    def add_msg(self, msg):
        self._msg += "\n" + msg
    

    def attempts(self):
        return self._attempts
    

    def created_at(self):
        return self._created_at


    def elem(self, elem=None):
        if elem is not None:
            self._element = elem
        return self._element


    def elem_type(self, elem_type=None):
        if elem_type is not None:
            self._element_type = elem_type
        return self._element_type


    def from_rec(self, rec: dict):
        self._attempts = rec[DJob.ATTEMPTS]
        self._created_at = rec[DJob.CREATED_AT]
        self._element_type = rec[DField.ELEMENT_TYPE]
        self._instance = rec[DJob.INSTANCE]
        self._job_id = rec[DJob.JOB_ID]
        self._msg = rec[DJob.MESSAGE]
        self._object_id = rec[DJob.OBJECT_ID]
        self._op = rec[DJob.OP]
        self._status = rec[DJob.STATUS]
        self._updated_at = rec[DJob.UPDATED_AT]
        
        if DField.ELEMENT in rec:
            elem_rec = rec[DField.ELEMENT]
            elem_type = elem_rec[DField.ELEMENT_TYPE]
            #print(f"Job:from_rec(): elem_type: {elem_type}")
            if elem_type == DElem.DB4E:
                self._element = Db4E(elem_rec)
            elif elem_type == DElem.MONEROD:
                self._element = MoneroD(elem_rec)
            elif elem_type == DElem.MONEROD_REMOTE:
                self._element = MoneroDRemote(elem_rec)
            elif elem_type == DElem.P2POOL:
                self._element = P2Pool(elem_rec)
            elif elem_type == DElem.P2POOL_REMOTE:
                self._element = P2PoolRemote(elem_rec)
            elif elem_type == DElem.XMRIG:
                self._element = XMRig(elem_rec)
            self._instance = self.elem().instance()
            self._element_type = self.elem().elem_type()


    def id(self, object_id=None):
        if object_id != None:
            self._object_id = object_id
        return self._object_id

    def instance(self, instance=None):
        if instance != None:
            self._instance = instance
        return self._instance

    def job_id(self):
        return self._job_id
    

    def msg(self, msg=None):
        if msg != None:
            self._msg = msg
        return self._msg


    def op(self):
        return self._op


    def status(self, status=None):
        if status:
            self._status = status
            self._updated_at = datetime.now()
        return self._status


    def to_rec(self):
        job_rec = {
            DJob.ATTEMPTS: self._attempts,
            DJob.CREATED_AT: self._created_at,
            DJob.ELEMENT_TYPE: self._element_type,
            DJob.INSTANCE: self._instance,
            DJob.JOB_ID: self._job_id,
            DJob.MESSAGE: self._msg,
            DJob.OP: self._op,
            DJob.STATUS: self._status,
            DJob.UPDATED_AT: self._updated_at,
        }

        elem = self.elem()
        if elem:
            job_rec[DField.ELEMENT] = elem.to_rec()

        return job_rec


    def updated_at(self, timestamp=None):
        if timestamp:
            self._updated_at = timestamp
        return self._updated_at


    def update_time(self):
        self._updated_at = datetime.now()



