"""
lib/Db4eDb/Db4eDb.py

This module implements a key component of the Data Abstraction Layer.
Aside from the Db4edDbLogHandler class, this is the only class that
interfaces with MongoDB.


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

  You should have received a copy (LICENSE.txt) of the GNU General 
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""


# Import supporting modules
from pymongo import MongoClient
import os, sys
import subprocess
from datetime import datetime, timezone, timedelta
import time
from pymongo.errors import ConnectionFailure, CollectionInvalid

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eLogger.Db4eLogger import Db4eLogger

class Db4eDb():

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

  def backup_db(self):
    backup_dir = self.ini.config['web']['backup_dir']
    backup_script = self.ini.config['db']['backup_script']
    bin_dir = self.ini.config['db4e']['bin_dir']
    self._backup_script   = os.path.join(self._db4e_dir, bin_dir, backup_script)
          
    self._backup_dir      = os.path.join(self._repo_dir, backup_dir)
    backup_script = self._backup_script
    backup_dir = self._backup_dir
    db_name = self._db_name
    col = self._db_collection
    log_col = self._log_collection
    depl_col = self._depl_collection
    metrics_col = self._metrics_collection
    for aCol in [ col, log_col, depl_col, metrics_col ]:
      subprocess.run([backup_script, db_name, aCol, backup_dir, str(self._max_backups)])
      self.log.debug(f'Created a new backup of ({aCol}) in {backup_dir}')
      print(f'Created a new backup of ({aCol}) in {backup_dir}')

  def delete_one(self, collection, dbquery):
     return collection.delete_one(dbquery)

  def init_db(self):
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

  def ensure_indexes(self):
    log_col = self.get_collection(self._log_collection)
    if "timestamp_1" not in log_col.index_information():
      log_col.create_index("timestamp")
      self.log.debug("Created index on 'timestamp' for log collection.")

  def get_collection(self, name):
      return self._db[name]

  def find_one(self, collection, filter):
      return collection.find_one(filter)

  def find_many(self, collection, filter):
      return collection.find(filter)

  def insert_one(self, col_name, jdoc):
      collection = self.get_collection(col_name)
      return collection.insert_one(jdoc)
  
  def insert_uniq_by_timestamp(self, collection, jdoc):
    timestamp = jdoc['timestamp']
    doc_type = jdoc['doc_type']
    existing = self.find_one(collection, {'doc_type': doc_type, 
                                          'timestamp': timestamp})
    if not existing:
        self.insert_one(collection, jdoc)
        return True
    return False
  
  def purge_old_logs(self):
    try:
      retention_days = self._log_retention
      log_col = self.get_collection(self._log_collection)
      threshold_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
      result = log_col.delete_many({"timestamp": {"$lt": threshold_date}})
      self.log.debug(f'Purged ({result.deleted_count}) old log entries')
    except:
      self.log.error(f'Error purging logs: {e}')

  def set_db4e_dir(self, db4e_dir):
      self._db4e_dir = db4e_dir

  def set_repo_dir(self, repo_dir):
      self._repo_dir = repo_dir

  def update_one(self, collection, filter, new_values):
      return collection.update_one(filter, new_values)

  def close(self):
      self._client.close()


