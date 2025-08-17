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

from db4e.Constants.Fields import (PENDING_FIELD, JOB_ID_FIELD, OP_FIELD,
    ATTEMPTS_FIELD, CREATED_AT_FIELD, STATUS_FIELD, ERROR_FIELD, ELEMENT_TYPE_FIELD,
    INSTANCE_FIELD, UPDATED_AT_FIELD)


class Job:


    def __init__(self, op=None, elem_type=None, instance=None):
        self._job_id = str(uuid.uuid4())
        self._op = op
        self._status = PENDING_FIELD
        self._attempts = 0
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._error = None
        self._element_type = elem_type
        self._instance = instance


    def __repr__(self):
        return f"{type(self).__name__}({self.op()}): {self.status()} {self.elem_type()}/{self.instance()}"


    def attempts(self):
        return self._attempts


    def created_at(self):
        return self._created_at


    def elem_type(self):
        return self._element_type


    def error(self):
        return self._error


    def from_rec(self, rec: dict):
        self._job_id = rec[JOB_ID_FIELD]
        self._op = rec[OP_FIELD]
        self._status = rec[STATUS_FIELD]
        self._attempts = rec[ATTEMPTS_FIELD]
        self._created_at = rec[CREATED_AT_FIELD]
        self._updated_at = rec[UPDATED_AT_FIELD]
        self._error = rec[ERROR_FIELD]
        self._element_type = rec[ELEMENT_TYPE_FIELD]
        self._instance = rec[INSTANCE_FIELD]


    def instance(self):
        return self._instance


    def job_id(self):
        return self._job_id
    

    def op(self):
        return self._op


    def status(self, status=None):
        if status:
            self._status = status
            self._updated_at = datetime.now()
        return self._status


    def to_rec(self):
        return {
            JOB_ID_FIELD: self._job_id,
            OP_FIELD: self._op,
            STATUS_FIELD: self._status,
            ATTEMPTS_FIELD: self._attempts,
            CREATED_AT_FIELD: self._created_at,
            UPDATED_AT_FIELD: self._updated_at,
            ERROR_FIELD: self._error,
            ELEMENT_TYPE_FIELD: self._element_type,
            INSTANCE_FIELD: self._instance
        }
    

    def updated_at(self):
        return self._updated_at


    def update_time(self):
        self._updated_at = datetime.now()


