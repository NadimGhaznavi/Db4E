"""
db4e/Modules/DbManager.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import sys
from datetime import datetime
from copy import deepcopy
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import (
    ConnectionFailure, CollectionInvalid, ServerSelectionTimeoutError)

from db4e.Modules.XMRig import XMRig
from db4e.Modules.Db4E import Db4E
from db4e.Constants.Fields import (
    DB4E_FIELD, ELEMENT_TYPE_FIELD, ELEMENT_TYPE_FIELD)
from db4e.Constants.Jobs import (
    STATUS_FIELD, PENDING_FIELD, ATTEMPTS_FIELD,UPDATED_AT_FIELD, PROCESSING_FIELD)
from db4e.Constants.Defaults import (OPS_COL_DEFAULT, MINING_COL_DEFAULT, 
    LOG_COLLECTION_DEFAULT, LOG_RETENTION_DAYS_DEFAULT, MAX_BACKUPS_DEFAULT,
    METRICS_COLLECTION_DEFAULT, DEPLOYMENT_COL_DEFAULT, TEMPLATES_COLLECTION_DEFAULT,
    DB_NAME_DEFAULT, DB_PORT_DEFAULT, DB_SERVER_DEFAULT, DB_RETRY_TIMEOUT_DEFAULT)


def as_worker(method):
    def wrapper(self, *args, use_worker=True, **kwargs):
        if use_worker and self._runner:
            def blocking():
                return method(self, *args, use_worker=False, **kwargs)
            return self._runner.run_worker(blocking, exclusive=False, thread_name="dbmgr")
        return method(self, *args, use_worker=False, **kwargs)
    return wrapper


class DbMgr:
    def __init__(self, runner=None):
        self._runner = runner
        self.db4e = None
        self._client = None
        # MongoDB settings
        retry_timeout      = DB_RETRY_TIMEOUT_DEFAULT
        db_server          = DB_SERVER_DEFAULT
        db_port            = DB_PORT_DEFAULT

        self.max_backups   = MAX_BACKUPS_DEFAULT
        self.db_name       = DB_NAME_DEFAULT
        self.db_col        = MINING_COL_DEFAULT
        self.depl_col      = DEPLOYMENT_COL_DEFAULT
        self.log_col       = LOG_COLLECTION_DEFAULT
        self.log_retention = LOG_RETENTION_DAYS_DEFAULT
        self.metrics_col   = METRICS_COLLECTION_DEFAULT
        self.ops_col       = OPS_COL_DEFAULT
        self.tmpl_col      = TEMPLATES_COLLECTION_DEFAULT

        # Connect to MongoDB
        db_uri = f'mongodb://{db_server}:{db_port}'

        try:
            self._client = MongoClient(db_uri, serverSelectionTimeoutMS=retry_timeout)
            # Force a connection test
            self._client.admin.command('ping')
            self.db4e = self._client[self.db_name]

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print("\nFatal error: Cannot connect to MongoDB.\n\n"
                  "See https://db4e.osoyalce.com/pages/Installing-MongoDB.html " \
                  "for instructions on how to install MongoDB Community Edition.\n")
            self._client = None
            self.db4e = None
            sys.exit(1)
      
        self.db4e = self._client[self.db_name]

        # Initialize the schema if needed
        self.init_db()             


    @as_worker
    def delete_one(self, col_name, filter, use_worker=True):
        col = self.get_collection(col_name)
        return col.delete_one(filter)


    def ensure_indexes(self):
        log_col = self.get_collection(self.log_col)
        if "timestamp_1" not in log_col.index_information():
            log_col.create_index("timestamp")


    @as_worker
    def exists(self, col_name, filter, use_worker=True):
        col = self.get_collection(col_name)
        return col.count_documents(filter)


    @as_worker
    def find_many(self, col_name, filter, use_worker=True):
        col = self.get_collection(col_name)
        return list(col.find(filter))


    @as_worker
    def find_one(self, col_name, filter, use_worker=True):
        col = self.get_collection(col_name)
        return col.find_one(filter)


    @as_worker
    def find_one_and_update(self, col_name, filter, update, return_document=True, use_worker=True):
        col = self.get_collection(col_name)
        return col.find_one_and_update(filter, update, return_document=return_document)


    def get_collection(self, col_name):
        if self.db4e is None:
            raise RuntimeError("MongoDB connection is not initialized.")
        return self.db4e[col_name]


    def get_jobs(self):
        collection = self.get_collection(self.ops_col)
        return collection.find().sort(UPDATED_AT_FIELD, -1)


    def grab_job(self):
        collection = self.get_collection(self.ops_col)
        #print(f"DbMgr:grab_job():\nSTATUS_FIELD: {STATUS_FIELD}\nPROCESSING_FIELD: {PROCESSING_FIELD}")
        return collection.find_one_and_update(
            {STATUS_FIELD: PENDING_FIELD},
            {
                "$set": {
                    STATUS_FIELD: PROCESSING_FIELD,
                    UPDATED_AT_FIELD: datetime.now()
                },
                "$inc": {
                    ATTEMPTS_FIELD: 1
                }
            },
            return_document=ReturnDocument.AFTER
        )


    def init_db(self):
        # Make sure the 'db4e' database, core collections and indexes exist.
        db_col = self.db_col
        log_col = self.log_col
        depl_col = self.depl_col
        metrics_col = self.metrics_col
        tmpl_col = self.tmpl_col
        db_col_names = self.db4e.list_collection_names()
        for aCol in [ db_col, log_col, depl_col, metrics_col, tmpl_col ]:
            if aCol not in db_col_names:
                try:
                    self.db4e.create_collection(aCol)
                    if aCol == log_col:
                        log_col = self.get_collection(log_col)
                        log_col.create_index('timestamp')
                except CollectionInvalid:
                    # TODO self.log.warning(f"Attempted to create existing collection: {aCol}")
                    pass
        self.ensure_indexes()
        db4e_rec = self.find_one(col_name=depl_col, filter={ELEMENT_TYPE_FIELD: DB4E_FIELD})

        # Make sure there's a Db4E deployment record for Db4E
        if not db4e_rec:
            db4e = Db4E()
            print(f"DbMgr:init_db(): db4e: {db4e}")
            rec = db4e.to_rec()
            rec.pop("_id", None)
            self.insert_one(col_name=depl_col, jdoc=db4e.to_rec())
            

    @as_worker
    def insert_one(self, col_name, jdoc, use_worker=True):
        elem_type = ""
        if ELEMENT_TYPE_FIELD in jdoc:
            elem_type = jdoc[ELEMENT_TYPE_FIELD]
        #print(f"DbMgr:insert_one(): collection: {col_name}, element type: {elem_type}")
        col = self.get_collection(col_name)
        jdoc.pop("_id", None)
        return col.insert_one(deepcopy(jdoc))


    @as_worker
    def update_one(self, col_name, filter, new_values, use_worker=True):
        elem_type = ""
        if ELEMENT_TYPE_FIELD in new_values:
            elem_type = new_values[ELEMENT_TYPE_FIELD]
        #print(f"DbMgr:update_one(): collection: {col_name}, filter: {filter}, type:{elem_type}")
        collection = self.get_collection(col_name)
        new_values.pop("_id", None)
        return collection.update_one(filter, {'$set': new_values})



   
