"""
db4e/Modules/DbManager.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import sys
from copy import deepcopy
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure, CollectionInvalid, ServerSelectionTimeoutError)

from db4e.Modules.ConfigMgr import Config
from db4e.Constants.SoftwareSystems import (
    Db4E_Template, MoneroD_Remote_Template, MoneroD_Template,
    P2Pool_Remote_Template, P2Pool_Template, XMRig_Template
)
from db4e.Constants.Fields import (
    DB4E_FIELD, DB_FIELD, DB_NAME_FIELD, DEPLOYMENT_COL_FIELD,
    ELEMENT_TYPE_FIELD, HEALTH_MSGS_FIELD,
    LOG_COLLECTION_FIELD, LOG_RETENTION_DAYS_FIELD, MAX_BACKUPS_FIELD,
    METRICS_COLLECTION_FIELD, MINING_COL_FIELD, MONEROD_FIELD,
    MONEROD_REMOTE_FIELD, P2POOL_FIELD, P2POOL_REMOTE_FIELD, PORT_FIELD,
    RETRY_TIMEOUT_FIELD, SERVER_FIELD, XMRIG_FIELD, TEMPLATES_COLLECTION_FIELD,
    ELEMENT_TYPE_FIELD )


def as_worker(method):
    def wrapper(self, *args, use_worker=True, **kwargs):
        if use_worker and self._runner:
            def blocking():
                return method(self, *args, use_worker=False, **kwargs)
            return self._runner.run_worker(blocking, exclusive=False, thread_name="dbmgr")
        return method(self, *args, use_worker=False, **kwargs)
    return wrapper


class DbMgr:
    def __init__(self, config: Config, runner=None):
        self.ini = config
        self._runner = runner
        self.db4e = None
        self._client = None
        # MongoDB settings
        retry_timeout      = self.ini.config[DB_FIELD][RETRY_TIMEOUT_FIELD]
        db_server          = self.ini.config[DB_FIELD][SERVER_FIELD]
        db_port            = self.ini.config[DB_FIELD][PORT_FIELD]

        self.max_backups   = self.ini.config[DB_FIELD][MAX_BACKUPS_FIELD]
        self.db_name       = self.ini.config[DB_FIELD][DB_NAME_FIELD]
        self.db_col        = self.ini.config[DB_FIELD][MINING_COL_FIELD]
        self.depl_col      = self.ini.config[DB_FIELD][DEPLOYMENT_COL_FIELD]
        self.log_col       = self.ini.config[DB_FIELD][LOG_COLLECTION_FIELD]
        self.log_retention = self.ini.config[DB_FIELD][LOG_RETENTION_DAYS_FIELD]
        self.metrics_col   = self.ini.config[DB_FIELD][METRICS_COLLECTION_FIELD]
        self.tmpl_col      = self.ini.config[DB_FIELD][TEMPLATES_COLLECTION_FIELD]

        self.templates = {
            DB4E_FIELD: Db4E_Template,
            MONEROD_FIELD: MoneroD_Template,
            MONEROD_REMOTE_FIELD: MoneroD_Remote_Template,
            P2POOL_FIELD: P2Pool_Template,
            P2POOL_REMOTE_FIELD: P2Pool_Remote_Template,
            XMRIG_FIELD: XMRig_Template
        }

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
        # Used for backups
        self.db4e_dir = None
        self.repo_dir = None
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


    def get_collection(self, col_name):
        if self.db4e is None:
            raise RuntimeError("MongoDB connection is not initialized.")
        return self.db4e[col_name]


    def get_new_rec(self, rec_type):
        rec = self.find_one(self.tmpl_col, {ELEMENT_TYPE_FIELD: rec_type})
        if rec:
            rec.pop("_id", None)
        return deepcopy(rec) if rec else None
    

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
            # TODO self.log.debug(f'Created DB collection ({aCol})'
        self.init_templates()
        self.ensure_indexes()


    def init_templates(self):        
        # Components
        templates = [
            Db4E_Template, MoneroD_Remote_Template, MoneroD_Template,
            P2Pool_Remote_Template, P2Pool_Template, XMRig_Template]
        for template in templates:
            # Only one doc of each component type ever gets created
            query = {ELEMENT_TYPE_FIELD: template[ELEMENT_TYPE_FIELD]}
            if not self.exists(self.tmpl_col, query):
                self.insert_one(self.tmpl_col, template)


    @as_worker
    def insert_one(self, col_name, jdoc, use_worker=True):
        elem_type = ""
        if ELEMENT_TYPE_FIELD in jdoc:
            elem_type = jdoc[ELEMENT_TYPE_FIELD]
        #print(f"DbMgr:insert_one(): collection: {col_name}, element type: {elem_type}")
        col = self.get_collection(col_name)
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



   
