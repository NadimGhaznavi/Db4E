"""
db4e/Constants/Jobs.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from enum import StrEnum

from db4e.Constants.Fields import ELEMENT_FIELD, INSTANCE_FIELD
from db4e.Constants.Fields import DField

class DJob(StrEnum):
    ATTEMPTS = "attempts"
    COMPLETED = "completed"
    CREATED_AT = "created_at"
    DELETE = "delete"
    DISABLE = "disable"
    ELEMENT = ELEMENT_FIELD
    ELEMENT_TYPE = DField.ELEMENT_TYPE
    ENABLE = "enable"
    INSTANCE = INSTANCE_FIELD
    JOB_ID = "job_id"
    JOB_QUEUE = "job_queue"
    MESSAGE = DField.MESSAGE.value
    NEW = "new"
    OP = "op"
    PENDING = "pending"
    POST_JOB = "post_job"
    PROCESSING = "processing"
    RESTART = "restart"
    SET_PRIMARY = "set_primary"
    STATUS = "status"
    UPDATE = "update"
    UPDATED_AT = "updated_at"
