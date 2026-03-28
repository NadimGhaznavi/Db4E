# db4e/Constants/DJobs.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from typing import Final
from db4e.constants.DField import DField


class DJob:
    ATTEMPTS: Final[str] = "attempts"
    COMPLETED: Final[str] = "completed"
    CREATED_AT: Final[str] = "created_at"
    DELETE: Final[str] = "delete"
    DISABLE: Final[str] = "disable"
    ELEMENT: Final[str] = DField.ELEMENT
    ELEMENT_TYPE: Final[str] = DField.ELEMENT_TYPE
    ENABLE: Final[str] = "enable"
    INSTANCE: Final[str] = DField.INSTANCE
    JOB_ID: Final[str] = "job_id"
    JOB_QUEUE: Final[str] = "job_queue"
    MESSAGE: Final[str] = DField.MESSAGE
    NEW: Final[str] = "new"
    OBJECT_ID: Final[str] = DField.OBJECT_ID
    OP: Final[str] = DField.OP
    PRIORITY: Final[str] = "priority"
    PENDING: Final[str] = "pending"
    RETRY: Final[str] = "retry"
    PROCESSING: Final[str] = "processing"
    RESTART: Final[str] = "restart"
    SET_PRIMARY: Final[str] = "set primary"
    STATUS: Final[str] = "status"
    UPDATE: Final[str] = "update"
    UPDATED_AT: Final[str] = "updated_at"
