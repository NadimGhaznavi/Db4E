"""
db4e/Modules/OpsDb.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from datetime import datetime
from collections import defaultdict
from datetime import datetime, timedelta

from db4e.Modules.DbMgr import DbMgr

from db4e.Constants.DDef import DDef
from db4e.Constants.DMongo import DMongo
from db4e.Constants.DSystemD import DSystemD
from db4e.Constants.DField import DField
from db4e.Constants.DOps import DOps


class OpsDb:
    
    def __init__(self, db: DbMgr):
        self.db = db
        self.ops_col = DDef.OPS_COL

    def get_ops_events(self):
        return list(self.db.find_many(self.ops_col, {}, { DMongo.TIMESTAMP: -1 }))
    

    def add_start_event(self, elem_type, instance):
        self.add_start_stop_event(elem_type, instance, DSystemD.START)
        # Add a current uptime record
        cur_event = {
            DMongo.DOC_TYPE: DOps.CURRENT_UPTIME,
            DMongo.ELEM_TYPE: elem_type,
            DMongo.INSTANCE: instance,
            DOps.START_TIME: datetime.now().replace(microsecond=0),
            DOps.STOP_TIME: None,
            DOps.TOTAL_UPTIME: None,
        }
        self.db.insert_one(self.ops_col, cur_event)


    def add_stop_event(self, elem_type, instance):
        self.add_start_stop_event(elem_type, instance, DSystemD.STOP)
        # Update the current uptime record
        cur_event = self.db.find_one(self.ops_col, {
            DMongo.DOC_TYPE: DOps.CURRENT_UPTIME,
            DMongo.ELEM_TYPE: elem_type,
            DMongo.INSTANCE: instance,
            DOps.STOP_TIME: None,
            DOps.TOTAL_UPTIME: None
        })
        cur_event[DOps.STOP_TIME] = datetime.now().replace(microsecond=0)
        cur_event[DOps.TOTAL_UPTIME] = cur_event[DOps.STOP_TIME] - cur_event[DOps.START_TIME]
        self.db.update_one(
            self.ops_col, {DMongo.OBJECT_ID: cur_event[DMongo.OBJECT_ID]}, cur_event)
        # Get the total uptime record
        total_event = self.db.find_one(self.ops_col, {
            DMongo.DOC_TYPE: DOps.TOTAL_UPTIME,
            DMongo.ELEM_TYPE: elem_type,
            DMongo.INSTANCE: instance
        })
        # Update existing total uptime record
        if total_event:
            total_event[DOps.TOTAL_UPTIME] += cur_event[DOps.TOTAL_UPTIME]
            self.db.update_one(
                self.ops_col, {DMongo.OBJECT_ID: total_event[DMongo.OBJECT_ID]}, total_event)
        # Create a new total uptime record
        else:
            total_event = {
                DMongo.DOC_TYPE: DOps.TOTAL_UPTIME,
                DMongo.ELEM_TYPE: elem_type,
                DMongo.INSTANCE: instance,
                DOps.TOTAL_UPTIME: cur_event[DOps.TOTAL_UPTIME]
            }
            self.db.insert_one(self.ops_col, total_event)

    def add_start_stop_event(self, elem_type, instance, event):
        timestamp = datetime.now().replace(microsecond=0)
        event = {
            DMongo.DOC_TYPE: DOps.START_STOP_EVENT,
            DMongo.ELEM_TYPE: elem_type,
            DMongo.INSTANCE: instance,
            DMongo.EVENT: event,
            DMongo.TIMESTAMP: timestamp
        }
        self.db.insert_one(self.ops_col, event)



class OpsETL:

    def __init__(self, ops_db: OpsDb):
        self.ops_db = ops_db


    def get_ops_summary(self):
        pass