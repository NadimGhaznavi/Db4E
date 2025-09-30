"""
db4e/Modules/DbMgr.py

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

from db4e.Modules.Db4E import Db4E
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DDef import DDef
from db4e.Constants.DJob import DJob



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
        retry_timeout      = DDef.DB_RETRY_TIMEOUT
        db_server          = DDef.DB_SERVER
        db_port            = DDef.DB_PORT

        self.max_backups   = DDef.MAX_BACKUPS
        self.db_name       = DDef.DB_NAME
        self.db_col        = DDef.MINING_COL
        self.depl_col      = DDef.DEPLOYMENT_COL
        self.jobs_col      = DDef.JOBS_COL
        self.log_col       = DDef.LOG_COLLECTION
        self.log_retention = DDef.LOG_RETENTION_DAYS
        self.metrics_col   = DDef.METRICS_COLLECTION
        self.ops_col       = DDef.OPS_COL

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
    def find_many(self, col_name, filter, res_sort=None, use_worker=True):
        col = self.get_collection(col_name)
        cursor = col.find(filter)
        if res_sort is not None:
            # convert dict to list of tuples
            sort_list = list(res_sort.items())
            cursor = cursor.sort(sort_list)
        return list(cursor)


    @as_worker
    def find_one(self, col_name, filter, use_worker=True):
        col = self.get_collection(col_name)
        #print(f"DbMgr:find_one(): collection: {col_name}, filter: {filter}")
        return col.find_one(filter)


    @as_worker
    def find_one_and_update(self, col_name, filter, update, return_document=True, use_worker=True):
        col = self.get_collection(col_name)
        return col.find_one_and_update(filter, update, return_document=return_document)


    def get_collection(self, col_name): 
        if self.db4e is None:
            raise RuntimeError("MongoDB connection is not initialized.")
        # col_name is a DDef instance, we need to convert it to a string
        return self.db4e[str(col_name)]


    def init_db(self):
        # Make sure the 'db4e' database, core collections and indexes exist.
        db_col = self.db_col
        jobs_col = self.jobs_col
        log_col = self.log_col
        depl_col = self.depl_col
        metrics_col = self.metrics_col
        ops_col = self.ops_col
        db_col_names = self.db4e.list_collection_names()
        for aCol in [ db_col, log_col, depl_col, metrics_col, jobs_col, ops_col ]:
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
        db4e_rec = self.find_one(
            col_name=depl_col, filter={DField.ELEMENT_TYPE: DElem.DB4E})
            

    @as_worker
    def insert_one(self, col_name, jdoc, use_worker=True):
        elem_type = ""
        if DField.ELEMENT_TYPE in jdoc:
            elem_type = jdoc[DField.ELEMENT_TYPE]
        #print(f"DbMgr:insert_one(): collection: {col_name}, element type: {elem_type}")
        col = self.get_collection(col_name)
        jdoc.pop("_id", None)
        insert_result = col.insert_one(jdoc)
        return insert_result.inserted_id


    def insert_uniq_by_timestamp(self, collection, jdoc):
        timestamp = jdoc['timestamp']
        doc_type = jdoc['doc_type']
        existing = self.find_one(collection, {'doc_type': doc_type, 
                                            'timestamp': timestamp})
        if not existing:
            return self.insert_one(collection, jdoc)
        return False
    
    @as_worker
    def update_one(self, col_name, filter, new_values, use_worker=True):
        elem_type = ""
        if DField.ELEMENT_TYPE in new_values:
            elem_type = new_values[DField.ELEMENT_TYPE]
        #print(f"DbMgr:update_one(): collection: {col_name}, filter: {filter}, type:{elem_type}")
        collection = self.get_collection(col_name)
        new_values.pop("_id", None)
        collection.update_one(filter, {'$set': new_values})
        



   
