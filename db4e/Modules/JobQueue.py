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
from db4e.Constants.DDef import DDef
from db4e.Constants.DJob import DJob
from db4e.Constants.DMongo import DMongo



class JobQueue:
    def __init__(self, db: DbMgr):
        self.col_name = DDef.JOBS_COL
        self.db = db


    def complete_job(self, job: Job):
        job.status(DJob.COMPLETED)
        job.updated_at(datetime.now())
        self.db.update_one(self.col_name, {DMongo.OBJECT_ID: job.id()}, job.to_rec())        


    def get_jobs(self):
        jobs = []
        for rec in self.db.find_many(self.col_name, {}, {DJob.UPDATED_AT: -1}):
            job = Job()
            job.from_rec(rec)
            jobs.append(job)
        return jobs


    def grab_job(self):
        job_rec = self.db.find_one_and_update(
            self.col_name, 
            {DJob.STATUS: DJob.PENDING},
            {
                "$set": {
                    DJob.STATUS: DJob.PROCESSING,
                    DJob.UPDATED_AT: datetime.now()
                },
                "$inc": {
                    DJob.ATTEMPTS: 1
                }
            },
        )
        if job_rec:
            job = Job()
            job.from_rec(job_rec)
            job.status(DJob.PROCESSING)
            return job
        else:
            return False


    def post_completed_job(self, job: Job):
        if job.elem_type() is not None:
            job.status(DJob.COMPLETED)
            job.updated_at(datetime.now())
            self.db.insert_one(self.col_name, job.to_rec())


    def post_job(self, job: Job):
        job_rec = job.to_rec()
        self.db.insert_one(self.col_name, job_rec)
        #print(f"JobQueue:post_job(): Job posted: {job}")


