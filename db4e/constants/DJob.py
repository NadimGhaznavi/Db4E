"""
db4e/Constants/DJobs.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup
from db4e.Constants.DField import DField

class DJob(ConstGroup):
    ATTEMPTS : str = "attempts"
    COMPLETED : str = "completed"
    CREATED_AT : str = "created_at"
    DELETE : str = "delete"
    DISABLE : str = "disable"
    ELEMENT : str = DField.ELEMENT
    ELEMENT_TYPE : str = DField.ELEMENT_TYPE
    ENABLE : str = "enable"
    INSTANCE : str = DField.INSTANCE
    JOB_ID : str = "job_id"
    JOB_QUEUE : str = "job_queue"
    MESSAGE : str = DField.MESSAGE
    NEW : str = "new"
    OBJECT_ID : str = DField.OBJECT_ID
    OP : str = DField.OP
    PRIORITY : str = "priority"
    PENDING : str = "pending"
    RETRY : str = "retry"
    PROCESSING : str = "processing"
    RESTART : str = "restart"
    SET_PRIMARY : str = "set primary"
    STATUS : str = "status"
    UPDATE : str = "update"
    UPDATED_AT : str = "updated_at"
