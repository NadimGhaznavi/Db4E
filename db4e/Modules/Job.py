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

from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig
from db4e.Constants.Fields import (ELEMENT_FIELD, ELEMENT_TYPE_FIELD,
    INSTANCE_FIELD, OBJECT_ID_FIELD, MONEROD_FIELD, MONEROD_REMOTE_FIELD, 
    P2POOL_FIELD, P2POOL_REMOTE_FIELD, XMRIG_FIELD)
from db4e.Constants.Jobs import (
    JOB_ID_FIELD, OP_FIELD, MESSAGE_FIELD, PENDING_FIELD,
    ATTEMPTS_FIELD, CREATED_AT_FIELD, STATUS_FIELD, UPDATED_AT_FIELD)


class Job:


    def __init__(self, op=None, elem_type=None, instance=None):
        self._attempts = 0
        self._created_at = datetime.now()
        self._element = None
        self._element_type = elem_type
        self._instance = instance
        self._job_id = str(uuid.uuid4())
        self._msg = None
        self._object_id = None
        self._op = op
        self._status = PENDING_FIELD
        self._updated_at = datetime.now()


    def __repr__(self):
        return f"{type(self).__name__}({self.op()}): {self.status()} {self.elem_type()}/{self.instance()}"


    def attempts(self):
        return self._attempts
    

    def created_at(self):
        return self._created_at


    def elem(self):
        return self._element


    def elem_type(self):
        return self._element_type


    def from_rec(self, rec: dict):
        self._attempts = rec[ATTEMPTS_FIELD]
        self._created_at = rec[CREATED_AT_FIELD]
        self._element_type = rec[ELEMENT_TYPE_FIELD]
        self._instance = rec[INSTANCE_FIELD]
        self._job_id = rec[JOB_ID_FIELD]
        self._msg = rec[MESSAGE_FIELD]
        self._object_id = rec[OBJECT_ID_FIELD]
        self._op = rec[OP_FIELD]
        self._status = rec[STATUS_FIELD]
        self._updated_at = rec[UPDATED_AT_FIELD]
        if ELEMENT_FIELD in rec:
            elem_rec = rec[ELEMENT_FIELD]
            elem_type = elem_rec[ELEMENT_TYPE_FIELD]
            #print(f"Job:from_rec(): elem_type: {elem_type}")
            if elem_type == MONEROD_FIELD:
                self._element = MoneroD(elem_rec)
            elif elem_type == MONEROD_REMOTE_FIELD:
                self._element = MoneroDRemote(elem_rec)
            elif elem_type == P2POOL_FIELD:
                self._element = P2Pool(elem_rec)
            elif elem_type == P2POOL_REMOTE_FIELD:
                self._element = P2PoolRemote(elem_rec)
            elif elem_type == XMRIG_FIELD:
                self._element = XMRig(elem_rec)


    def id(self, object_id=None):
        if object_id != None:
            self._object_id = object_id
        return self._object_id

    def instance(self):
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
        return {
            ATTEMPTS_FIELD: self._attempts,
            CREATED_AT_FIELD: self._created_at,
            ELEMENT_TYPE_FIELD: self._element_type,
            INSTANCE_FIELD: self._instance,
            JOB_ID_FIELD: self._job_id,
            MESSAGE_FIELD: self._msg,
            OP_FIELD: self._op,
            STATUS_FIELD: self._status,
            UPDATED_AT_FIELD: self._updated_at,
        }
    

    def updated_at(self, timestamp=None):
        if timestamp:
            self._updated_at = timestamp
        return self._updated_at


    def update_time(self):
        self._updated_at = datetime.now()


