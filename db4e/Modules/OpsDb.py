"""
db4e/Modules/OpsDb.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from datetime import datetime

from db4e.Modules.DbMgr import DbMgr

from db4e.Constants.DDef import DDef
from db4e.Constants.DMongo import DMongo
from db4e.Constants.DSystemD import DSystemD




class OpsDb:
    
    def __init__(self, db: DbMgr):
        self.db = db
        self.ops_col = DDef.OPS_COL

    def get_ops_events(self):
        return list(self.db.find_many(self.ops_col, {}, { DMongo.TIMESTAMP: -1 }))
    

    def add_start_event(self, elem_type, instance):
        self.add_event(elem_type, instance, DSystemD.START)


    def add_stop_event(self, elem_type, instance):
        self.add_event(elem_type, instance, DSystemD.STOP)


    def add_event(self, elem_type, instance, event):
        timestamp = datetime.now().replace(microsecond=0)
        event = {
            DMongo.ELEM_TYPE: elem_type,
            DMongo.INSTANCE: instance,
            DMongo.EVENT: event,
            DMongo.TIMESTAMP: timestamp
        }
        self.db.insert_one(self.ops_col, event)        