

from datetime import datetime
import uuid 

from db4e.Modules.DbMgr import DbMgr
from db4e.Constants.Fields import (
    OP_FIELD, ATTEMPTS_FIELD, CREATED_AT_FIELD, JOB_ID_FIELD,
    COMPONENT_FIELD, ID_FIELD, STATUS_FIELD, PENDING_FIELD, INSTANCE_FIELD,
    RESULTS_FIELD, PROCESSING_FIELD, UPDATED_AT_FIELD)
from db4e.Constants.Defaults import OPS_COL_DEFAULT

class JobQueue:
    def __init__(self, db: DbMgr):
        self.col_name = OPS_COL_DEFAULT
        self.db = db

    def post_job(self, details):
        job_id = str(uuid.uuid4())
        job = {
            JOB_ID_FIELD: job_id,
            OP_FIELD: details[OP_FIELD],
            STATUS_FIELD: PENDING_FIELD,
            CREATED_AT_FIELD: datetime.now(),
            ATTEMPTS_FIELD: 0,
            COMPONENT_FIELD: details[COMPONENT_FIELD],
            INSTANCE_FIELD: details[INSTANCE_FIELD]
        }
        self.db.insert_one(self.col_name, job)
        print(f"Job enqueued: {job['_id']}")

    def get_and_process_job(self):
        job = self.collection.find_one_and_update(
            {STATUS_FIELD: PENDING_FIELD},
            {"$set": {STATUS_FIELD: PROCESSING_FIELD, UPDATED_AT_FIELD: datetime.now(), 
            "$inc": {"attempts": 1}}},
            return_document=True
        )
        if job:
            print(f"Processing job: {job['_id']}")
            try:
                # Simulate job processing
                # time.sleep(2)
                # if random.random() < 0.1:
                #     raise Exception("Simulated error")

                self.collection.update_one(
                    {"_id": job["_id"]},
                    {"$set": {"status": "completed", "updated_at": datetime.now()}}
                )
                print(f"Job {job['_id']} completed.")
            except Exception as e:
                self.collection.update_one(
                    {"_id": job["_id"]},
                    {"$set": {"status": "failed", "error": str(e), "updated_at": datetime.now()}}
                )
                print(f"Job {job['_id']} failed: {e}")
        else:
            print("No pending jobs.")

# Example Usage:
# queue = JobQueue()
# queue.enqueue_job({"task": "send_email", "recipient": "test@example.com"})
# queue.get_and_process_job()
```