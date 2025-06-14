"""
lib/Infrastructure/Db4eDb/Db4eDb.py

This module implements a key component of the Data Abstraction Layer.
Aside from the Db4edDbLogHandler class, this is the only class that
interfaces with MongoDB.
"""


"""
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
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eLogger.Db4eLogger import Db4eLogger

class Db4eDb():

  def __init__(self):
    ini = Db4eConfig()
    # MongoDB settings
    retry_timeout         = ini.config['db']['retry_timeout']
    db_server             = ini.config['db']['server']
    db_port               = ini.config['db']['port']
    self._db_name         = ini.config['db']['name']
    self._db_collection   = ini.config['db']['collection']
    self._log_collection  = ini.config['db']['log_collection']
    self._depl_collection = ini.config['db']['depl_collection']
    # Backup script settings
    db4e_dir              = ini.config['db4e']['install_dir']
    web_dir               = ini.config['web']['install_dir']
    backup_dir            = ini.config['web']['backup_dir']
    backup_script         = ini.config['db']['backup_script']
    self._log_retention   = ini.config['db']['log_retention_days']
    self._backup_script   = os.path.join(db4e_dir, backup_script)
    self._backup_dir      = os.path.join(web_dir, backup_dir)
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
    self.init_db()

  def backup_db(self):
    backup_script = self._backup_script
    backup_dir = self._backup_dir
    db_name = self._db_name
    col = self._db_collection
    log_col = self._log_collection
    depl_col = self._depl_collection
    for aCol in [ col, log_col, depl_col ]:
      subprocess.run([backup_script, db_name, aCol, backup_dir])
      self.log.info(f'Created a new backup of ({aCol}) in {backup_dir}')

  def init_db(self):
    db_col  = self._db_collection
    log_col = self._log_collection
    depl_col = self._depl_collection
    db_col_names = self._db.list_collection_names()
    for aCol in [ db_col, log_col, depl_col]:
       if aCol not in db_col_names:
          try:
            self._db.create_collection(aCol)
          except CollectionInvalid:
            self.log.warning(f"Attempted to create existing collection: {aCol}")
          self.log.debug(f'Created DB collection ({aCol})')

  def get_collection(self, name):
      return self._db[name]

  def find_one(self, collection, filter):
      return collection.find_one(filter)

  def find_many(self, collection, filter):
      return collection.find(filter)

  def insert_one(self, collection, jdoc):
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

  def update_one(self, collection, filter, new_values):
      return collection.update_one(filter, new_values)

  def close(self):
      self._client.close()


