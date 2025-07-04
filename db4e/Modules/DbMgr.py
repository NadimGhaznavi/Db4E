"""
db4e/Modules/DbManager.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""

import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid

from db4e.Modules.ConfigMgr import Config
from db4e.Templates.db.Deployment import DB4E_RECORD

class DbMgr:
    
   def __init__(self, config: Config):
      self.ini = config
      # MongoDB settings
      retry_timeout            = self.ini.config['db']['retry_timeout']
      db_server                = self.ini.config['db']['server']
      db_port                  = self.ini.config['db']['port']
      self.max_backups         = self.ini.config['db']['max_backups']
      self.db_name             = self.ini.config['db']['name']
      self.db_collection       = self.ini.config['db']['collection']
      self.depl_collection     = self.ini.config['db']['depl_collection']
      self.log_collection      = self.ini.config['db']['log_collection']
      self.log_retention       = self.ini.config['db']['log_retention_days']
      self.metrics_collection  = self.ini.config['db']['metrics_collection']
      # TODO Setup logging
      #self.log = Db4eLogger('Db4eDb')

      # Connect to MongoDB
      db_uri = f'mongodb://{db_server}:{db_port}'
      try:
         self._client = MongoClient(db_uri)
      except ConnectionFailure as e:
         # TODO factor in the old Db4eLogger code....
         #self.log.critical(f'Connection failed: {e}. Retrying in {retry_timeout} seconds...')
         time.sleep(retry_timeout)
      
      self.db4e = self._client[self.db_name]

      # Used for backups
      self.db4e_dir = None
      self.repo_dir = None
      self.init_db()             

   def ensure_indexes(self):
      log_col = self.get_collection(self.log_collection)
      if "timestamp_1" not in log_col.index_information():
         log_col.create_index("timestamp")
         # TODO self.log.debug("Created index on 'timestamp' for log collection.")

   def find_one(self, col_name, filter):
      col = self.get_collection(col_name)
      return col.find_one(filter)

   def get_collection(self, col_name):
      return self.db4e[col_name]

   def get_new_rec(self, rec_type):
      if rec_type == 'db4e':
         return DB4E_RECORD

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
      return collection.update_one(filter, {'$set' : new_values})
