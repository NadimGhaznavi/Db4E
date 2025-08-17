"""
db4e/JobQueue.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.Job import Job
from db4e.Constants.Fields import (
    OP_FIELD, ELEMENT_TYPE_FIELD, PENDING_FIELD, INSTANCE_FIELD, JOB_ID_FIELD)
from db4e.Constants.Defaults import OPS_COL_DEFAULT

class JobQueue:
    def __init__(self, db: DbMgr, log=None):
        self.col_name = OPS_COL_DEFAULT
        self.db = db
        self.log = log


    def post_job(self, details: dict):
        job = Job(details[OP_FIELD], details[ELEMENT_TYPE_FIELD], details[INSTANCE_FIELD])
        self.db.insert_one(self.col_name, job.to_rec())
        print(f"JobQueue:post_job(): Job posted: {job}")

    def grab_job(self):
        job_rec = self.db.grab_job()
        if job_rec:
            job = Job()
            job.from_rec(job_rec)
            job.status(PENDING_FIELD)
            #self.db.update_one(self.col_name, {"_id": job_rec["_id"]}, job.to_rec())
            self.log.critical(f"JobQueue:grab_job(): {job}")
            return job
        else:
            return False
