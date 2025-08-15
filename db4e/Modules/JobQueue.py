

from datetime import datetime
import uuid
import time

from db4e.Modules.DbMgr import DbMgr
from db4e.Constants.Fields import (
    OP_FIELD, ATTEMPTS_FIELD, CREATED_AT_FIELD, JOB_ID_FIELD,
    ELEMENT_TYPE_FIELD, STATUS_FIELD, PENDING_FIELD, INSTANCE_FIELD)
from db4e.Constants.Defaults import OPS_COL_DEFAULT

class JobQueue:
    def __init__(self, db: DbMgr, log=None):
        self.col_name = OPS_COL_DEFAULT
        self.db = db
        self.log = log


    def post_job(self, details):
        job_id = str(uuid.uuid4())
        job = {
            JOB_ID_FIELD: job_id,
            OP_FIELD: details[OP_FIELD],
            STATUS_FIELD: PENDING_FIELD,
            CREATED_AT_FIELD: datetime.now(),
            ATTEMPTS_FIELD: 0,
            ELEMENT_TYPE_FIELD: details[ELEMENT_TYPE_FIELD],
            INSTANCE_FIELD: details[INSTANCE_FIELD]
        }
        self.db.insert_one(self.col_name, job)
        print(f"Job posted: {job[JOB_ID_FIELD]}")

    def grab_job(self):
        job = self.db.grab_job()
        if job:
            self.log.info(f"Processing job: {job['_id']}")
            try:
                # Simulate job processing
                time.sleep(2)

                self.db.update_one(
                    self.col_name,
                    {"_id": job["_id"]},
                    {"status": "completed", "updated_at": datetime.now()}
                )
                self.log.info(f"Job {job['_id']} completed.")
            except Exception as e:
                self.db.update_one(
                    self.col_name,
                    {"_id": job["_id"]},
                    {"status": "failed", "error": str(e), "updated_at": datetime.now()}
                )
                self.log.error(f"Job {job['_id']} failed: {e}")
        else:
            return False

# Example Usage:
# queue = JobQueue()
# queue.post_job({"task": "send_email", "recipient": "test@example.com"})
# queue.grab_job()