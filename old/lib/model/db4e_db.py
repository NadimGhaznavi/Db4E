"""
lib/model/db4e_db.py


  This file is part of *db4e*, the *Database 4 Everything* project
  <https://github.com/NadimGhaznavi/db4e>, developed independently
  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
  <https://github.com/NadimGhaznavi/db4e>.
 
  This program is free software: you can redistribute it and/or 
  modify it under the terms of the GNU General Public License as 
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received aLine copy (LICENSE.txt) of the GNU General 
  if match:
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""

import time
import os, sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid

# Setup the db4e paths
DB4E_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 
DB4E_LIB_DIR = os.path.join(DB4E_DIR, 'lib')
DB4E_COMPONENTS_DIR = os.path.join(DB4E_LIB_DIR, 'components')
DB4E_MODEL_DIR = os.path.join(DB4E_LIB_DIR, 'model')
sys.path.append(DB4E_LIB_DIR)
sys.path.append(DB4E_COMPONENTS_DIR)
sys.path.append(DB4E_MODEL_DIR)

from settings import Db4eConfig
from model.logging import Db4eLogger 
from db_records import DB4E_RECORD

class Db4eDb:

    def __init__(self):
        ini = Db4eConfig()
        # MongoDB settings
        retry_timeout            = ini.config['db']['retry_timeout']
        db_server                = ini.config['db']['server']
        db_port                  = ini.config['db']['port']
        self._max_backups        = ini.config['db']['max_backups']
        self._db_name            = ini.config['db']['name']
        self._db_collection      = ini.config['db']['collection']
        self._depl_collection    = ini.config['db']['depl_collection']
        self._log_collection     = ini.config['db']['log_collection']
        self._log_retention      = ini.config['db']['log_retention_days']
        self._metrics_collection = ini.config['db']['metrics_collection']
        self.ini = ini
        # Setup logging
        self.log = Db4eLogger('Db4eDb')

        # Connect to MongoDB
        db_uri = f'mongodb://{db_server}:{db_port}'
        try:
            self._client = MongoClient(db_uri)
        except ConnectionFailure as e:
            self.log.critical(f'Connection failed: {e}. Retrying in {retry_timeout} seconds...')
            time.sleep(retry_timeout)
        
        self._db = self._client[self._db_name]

        # Used for backups
        self._db4e_dir = None
        self._repo_dir = None
        self.init_db()             

    def ensure_indexes(self):
        log_col = self.get_collection(self._log_collection)
        if "timestamp_1" not in log_col.index_information():
            log_col.create_index("timestamp")
            self.log.debug("Created index on 'timestamp' for log collection.")

    def find_one(self, col_name, filter):
        col = self.get_collection(col_name)
        return col.find_one(filter)

    def get_collection(self, col_name):
        return self._db[col_name]

    def get_new_rec(self, rec_type):
        if rec_type == 'db4e':
            return DB4E_RECORD

    def init_db(self):
        # Make sure the 'db4e' database, core collections and indexes exist.
        db_col = self._db_collection
        log_col = self._log_collection
        depl_col = self._depl_collection
        metrics_col = self._metrics_collection
        db_col_names = self._db.list_collection_names()
        for aCol in [ db_col, log_col, depl_col, metrics_col ]:
            if aCol not in db_col_names:
                try:
                    self._db.create_collection(aCol)
                    if aCol == log_col:
                        log_col = self.get_collection(log_col)
                        log_col.create_index('timestamp')
                except CollectionInvalid:
                    self.log.warning(f"Attempted to create existing collection: {aCol}")
                self.log.debug(f'Created DB collection ({aCol})')
            self.ensure_indexes()

    def insert_one(self, col_name, jdoc):
        collection = self.get_collection(col_name)
        return collection.insert_one(jdoc)