"""
db4e/Modules/DbManager.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

import time
from copy import deepcopy
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid

from db4e.Modules.ConfigMgr import Config
from db4e.Constants.MongoRecords import (
    Db4E_Record_Template, MoneroD_Remote_Record_Template, MoneroD_Record_Template,
    P2Pool_Remote_Record_Template, P2Pool_Record_Template, XMRig_Record_Template
)
from db4e.Constants.Fields import (
    DB4E_FIELD, DB_FIELD, DB_NAME_FIELD, DEPLOYMENT_COL_FIELD, 
    LOG_COLLECTION_FIELD, LOG_RETENTION_DAYS_FIELD, MAX_BACKUPS_FIELD, 
    METRICS_COLLECTION_FIELD, MINING_COL_FIELD, MONEROD_FIELD, 
    MONEROD_REMOTE_FIELD, P2POOL_FIELD, PORT_FIELD, RETRY_TIMEOUT_FIELD, 
    P2POOL_REMOTE_FIELD, SERVER_FIELD, XMRIG_FIELD)

class DbMgr:
    def __init__(self, config: Config):
        self.ini = config
        # MongoDB settings
        retry_timeout            = self.ini.config[DB_FIELD][RETRY_TIMEOUT_FIELD]
        db_server                = self.ini.config[DB_FIELD][SERVER_FIELD]
        db_port                  = self.ini.config[DB_FIELD][PORT_FIELD]
        self.max_backups         = self.ini.config[DB_FIELD][MAX_BACKUPS_FIELD]
        self.db_name             = self.ini.config[DB_FIELD][DB_NAME_FIELD]
        self.db_collection       = self.ini.config[DB_FIELD][MINING_COL_FIELD]
        self.depl_collection     = self.ini.config[DB_FIELD][DEPLOYMENT_COL_FIELD]
        self.log_collection      = self.ini.config[DB_FIELD][LOG_COLLECTION_FIELD]
        self.log_retention       = self.ini.config[DB_FIELD][LOG_RETENTION_DAYS_FIELD]
        self.metrics_collection  = self.ini.config[DB_FIELD][METRICS_COLLECTION_FIELD]

        self.templates = {
            DB4E_FIELD: Db4E_Record_Template,
            MONEROD_REMOTE_FIELD: MoneroD_Remote_Record_Template,
            MONEROD_FIELD: MoneroD_Record_Template,
            P2POOL_REMOTE_FIELD: P2Pool_Remote_Record_Template,
            P2POOL_FIELD: P2Pool_Record_Template,
            XMRIG_FIELD: XMRig_Record_Template
        }

        # Connect to MongoDB
        db_uri = f'mongodb://{db_server}:{db_port}'
        try:
            self._client = MongoClient(db_uri)
        except ConnectionFailure as e:
            time.sleep(retry_timeout)
      
        self.db4e = self._client[self.db_name]
        # Used for backups
        self.db4e_dir = None
        self.repo_dir = None
        self.init_db()             

    def delete_one(self, col_name, dbquery):
        col = self.get_collection(col_name)
        return col.delete_one(dbquery)

    def ensure_indexes(self):
        log_col = self.get_collection(self.log_collection)
        if "timestamp_1" not in log_col.index_information():
            log_col.create_index("timestamp")
            # TODO self.log.debug("Created index on 'timestamp' for log collection.")

    def find_many(self, col_name, filter):
        col = self.get_collection(col_name)
        return col.find(filter)

    def find_one(self, col_name, filter):
        col = self.get_collection(col_name)
        rec = col.find_one(filter)
        #print(f"DbMgr:find_one(): {col_name}/{filter} > {rec}")
        return rec

    def get_collection(self, col_name):
        return self.db4e[col_name]

    def get_new_rec(self, rec_type):
        return deepcopy(self.templates.get(rec_type))

    def init_db(self):
        # Make sure the 'db4e' database, core collections and indexes exist.
        db_col = self.db_collection
        log_col = self.log_collection
        depl_col = self.depl_collection
        metrics_col = self.metrics_collection
        db_col_names = self.db4e.list_collection_names()
        for aCol in [ db_col, log_col, depl_col, metrics_col ]:
            if aCol not in db_col_names:
                try:
                    self.db4e.create_collection(aCol)
                    if aCol == log_col:
                        log_col = self.get_collection(log_col)
                        log_col.create_index('timestamp')
                except CollectionInvalid:
                    # TODO self.log.warning(f"Attempted to create existing collection: {aCol}")
                    pass
            # TODO self.log.debug(f'Created DB collection ({aCol})')
        self.ensure_indexes()

    def insert_one(self, col_name, jdoc):
        collection = self.get_collection(col_name)
        return collection.insert_one(jdoc)
   
    def update_one(self, col_name, filter, new_values):
        collection = self.get_collection(col_name)
        # Remove the "_id" field if it's present
        new_values.pop("_id", None)
        return collection.update_one(filter, {'$set' : new_values})
