"""
db4e/JobQueue.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

from datetime import datetime


from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.Job import Job
from db4e.Constants.Fields import (
    ELEMENT_TYPE_FIELD, INSTANCE_FIELD, OBJECT_ID_FIELD, ELEMENT_FIELD)
from db4e.Constants.Defaults import OPS_COL_DEFAULT
from db4e.Constants.Jobs import (
    OP_FIELD, PENDING_FIELD, PROCESSING_FIELD, COMPLETED_FIELD
)

class JobQueue:
    def __init__(self, db: DbMgr, log=None):
        self.col_name = OPS_COL_DEFAULT
        self.db = db
        self.log = log


    def complete_job(self, job: Job):
        job.status(COMPLETED_FIELD)
        job.updated_at(datetime.now())
        self.db.update_one(self.col_name, {OBJECT_ID_FIELD: job.id()}, job.to_rec())        


    def get_jobs(self):
        jobs = []
        for rec in self.db.get_jobs():
            job = Job()
            job.from_rec(rec)
            jobs.append(job)
        return jobs


    def grab_job(self):
        job_rec = self.db.grab_job()
        if job_rec:
            #print(f"JobQueue:grab_job(): job_rec: {job_rec}")
            job = Job()
            job.from_rec(job_rec)
            #print(f"JobQueue:grab_job(): job.elem(): {job.elem()}")
            job.status(PROCESSING_FIELD)
            #self.db.update_one(self.col_name, {"_id": job_rec["_id"]}, job.to_rec())
            self.log.critical(f"JobQueue:grab_job(): {job}")
            return job
        else:
            return False


    def post_completed_job(self, job: Job):
        job.status(COMPLETED_FIELD)
        job.updated_at(datetime.now())
        self.db.insert_one(self.col_name, job.to_rec())


    def post_job(self, details: dict):
        job = Job(details[OP_FIELD], details[ELEMENT_TYPE_FIELD], details[INSTANCE_FIELD])
        job_rec = job.to_rec()
        if ELEMENT_FIELD in details:
            job_rec[ELEMENT_FIELD] = details[ELEMENT_FIELD].to_rec()
        self.db.insert_one(self.col_name, job_rec)
        #print(f"JobQueue:post_job(): Job posted: {job}")


