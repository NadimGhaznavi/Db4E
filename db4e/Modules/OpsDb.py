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
from db4e.Constants.DElem import DElem
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DOps import DOps


class OpsDb:
    
    def __init__(self, db: DbMgr):
        self.db = db
        self.ops_col = DDef.OPS_COL
        self.depl_col = DDef.DEPLOYMENT_COL


    def get_ops_events(self):
        return list(self.db.find_many(
            self.ops_col, { DMongo.DOC_TYPE: DOps.START_STOP_EVENT }))
    

    def add_start_event(self, elem_type, instance):
        self.add_start_stop_event(elem_type, instance, DSystemD.START)
        # Add a current uptime record
        cur_event = {
            DMongo.DOC_TYPE: DOps.CURRENT_UPTIME,
            DMongo.ELEMENT_TYPE: elem_type,
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
            DMongo.ELEMENT_TYPE: elem_type,
            DMongo.INSTANCE: instance,
            DOps.STOP_TIME: None,
            DOps.TOTAL_UPTIME: None
        })
        if not cur_event:
            return
        cur_event[DOps.STOP_TIME] = datetime.now().replace(microsecond=0)
        total_uptime = cur_event[DOps.STOP_TIME] - cur_event[DOps.START_TIME]
        # Convert the total_uptime into an int for Mongo
        cur_event[DOps.TOTAL_UPTIME] = int(total_uptime.total_seconds())
        self.db.update_one(
            self.ops_col, {DMongo.OBJECT_ID: cur_event[DMongo.OBJECT_ID]}, cur_event)
        # Get the total uptime record
        total_event = self.db.find_one(self.ops_col, {
            DMongo.DOC_TYPE: DOps.TOTAL_UPTIME,
            DMongo.ELEMENT_TYPE: elem_type,
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
                DMongo.ELEMENT_TYPE: elem_type,
                DMongo.INSTANCE: instance,
                DOps.TOTAL_UPTIME: cur_event[DOps.TOTAL_UPTIME]
            }
            self.db.insert_one(self.ops_col, total_event)

    def add_start_stop_event(self, elem_type, instance, event):
        timestamp = datetime.now().replace(microsecond=0)
        event = {
            DMongo.DOC_TYPE: DOps.START_STOP_EVENT,
            DMongo.ELEMENT_TYPE: elem_type,
            DMongo.INSTANCE: instance,
            DMongo.EVENT: event,
            DMongo.TIMESTAMP: timestamp
        }
        self.db.insert_one(self.ops_col, event)


    def get_uptime(self, elem_type, instance):
        LABEL_TABLE = {
            DElem.P2POOL: DLabel.P2POOL,
            DElem.XMRIG: DLabel.XMRIG,
        }
        cur_uptime_rec = self.db.find_one(self.ops_col, {
            DMongo.DOC_TYPE: DOps.CURRENT_UPTIME,
            DMongo.ELEMENT_TYPE: LABEL_TABLE[elem_type],
            DMongo.INSTANCE: instance
        })
        if not cur_uptime_rec:
            return None
        return cur_uptime_rec




class OpsETL:

    def __init__(self, ops_db: OpsDb):
        self.ops_db = ops_db


    def add_remote_xmrig_deployment(self, xmrig):
        self.ops_db.add_remote_xmrig_deployment(xmrig)


    def get_ops_summary(self):
        now = datetime.now().replace(microsecond=0)
        summary = []
        summary_dict = {}


        # Grab all current uptime docs
        current = self.ops_db.db.find_many(
            self.ops_db.ops_col,
            { DMongo.DOC_TYPE: DOps.CURRENT_UPTIME }
        )

        # Grab all total uptime docs
        totals = self.ops_db.db.find_many(
            self.ops_db.ops_col,
            { DMongo.DOC_TYPE: DOps.TOTAL_UPTIME }
        )
        totals_map = {
            (t[DMongo.ELEMENT_TYPE], t[DMongo.INSTANCE]): t for t in totals
        }

        for c in current:
            key = (c[DMongo.ELEMENT_TYPE], c[DMongo.INSTANCE])
            total_event = totals_map.get(key)

            # If still running, compute delta from START_TIME to now
            if c[DOps.STOP_TIME] is None:
                cur_uptime = now - c[DOps.START_TIME]
            else:
                cur_uptime = c[DOps.TOTAL_UPTIME]

            total_uptime = total_event[DOps.TOTAL_UPTIME] if total_event else cur_uptime

            # Convert the total_uptime (secs) into a datetime.timedelta object
            if type(total_uptime) == int:
                total_uptime = str(timedelta(seconds=total_uptime))

            if type(cur_uptime) == int:
                cur_uptime = str(timedelta(seconds=cur_uptime))

            summary_dict[c[DMongo.ELEMENT_TYPE] + "-" + c[DMongo.INSTANCE]] = {
                DMongo.ELEMENT_TYPE: c[DMongo.ELEMENT_TYPE],
                DMongo.INSTANCE: c[DMongo.INSTANCE],
                DOps.CURRENT_UPTIME: str(cur_uptime),
                DOps.TOTAL_UPTIME: str(total_uptime),
            }

        for key in summary_dict.keys():
            summary.append(summary_dict[key])

        return sorted(summary, key=lambda x: (x[DMongo.ELEMENT_TYPE], x[DMongo.INSTANCE]))


    def get_uptime(self, elem_type, instance):
        rec = self.ops_db.get_uptime(elem_type, instance)
        if not rec:
            return 0
        return rec[DOps.TOTAL_UPTIME]