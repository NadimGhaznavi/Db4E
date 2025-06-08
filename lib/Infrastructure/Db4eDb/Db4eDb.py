"""
lib/Infrastructure/Db4eDb/Db4eDb.py
"""

# Import supporting modules
from pymongo import MongoClient
import os, sys
import subprocess
from datetime import datetime, timezone
import time

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
    self._retry_timeout  = ini.config['db']['retry_timeout']
    self._db_server      = ini.config['db']['server']
    self._db_port        = ini.config['db']['port']
    self._db_name        = ini.config['db']['name']
    self._db_collection  = ini.config['db']['collection']
    self._log_collection = ini.config['db']['log_collection']
    
    db4e_dir             = ini.config['db4e']['install_dir']
    web_dir              = ini.config['web']['install_dir']
    backup_dir           = ini.config['web']['backup_dir']
    backup_script        = ini.config['db']['backup_script']
    
    self._backup_script  = os.path.join(db4e_dir, backup_script)
    self._backup_dir     = os.path.join(web_dir, backup_dir)

    # Setup logging
    self.log = Db4eLogger('Db4eDb')

    self.connected = False
    self.init_db()

  def backup_db(self):
    backup_script = self._backup_script
    backup_dir = self._backup_dir
    db_name = self._db_name
    col = self._db_collection
    log_col = self._log_collection

    for aCol in [ col, log_col ]:
      subprocess.run([backup_script, db_name, aCol, backup_dir])
      self.log.info(f'Created a new backup of ({aCol}) in {backup_dir}')

  def db(self):
    if not self.connected:
      self.connect()
    return self._db
  
  def connect(self):
    db_server = self._db_server
    db_port = self._db_port
    db_name = self._db_name
    retry_timeout = self._retry_timeout
    try:
      client = MongoClient(f"mongodb://{db_server}:{db_port}/")
    except:
      self.log.critical(f'Could not connect to DB ({db_server}:{db_port}), waiting {retry_timeout} seconds')
      time.sleep(retry_timeout)
    self.connected = True
    self._db = client[db_name]

  def get_docs(self, collection_name, doc_type):
    db = self.db()
    collection = db[collection_name]
    db_cursor = collection.find({'doc_type': doc_type})
    return db_cursor

  def init_db(self):
    db_col = self._db_collection
    log_col = self._log_collection
    db = self.db()
    db_col_names = db.list_collection_names()
    if db_col not in db_col_names:
      self.log.info(f'Created DB collection ({db_col})')
      db[db_col]
    if log_col not in db_col_names:
      self.log.info(f'Created logging DB collection ({log_col})')
      db[log_col]

  def insert_uniq_one(self, collection, jdoc):
    col = self._db[collection]
    doc_type = jdoc['doc_type']
    timestamp = jdoc['timestamp']
    if not col.find_one({'doc_type': doc_type, 'timestamp': timestamp}):
      col.insert_one(jdoc)
      self.log.debug(f'New DB record ({doc_type})')

  



