"""
lib/Infrastructure/Db4eDb/Db4eDb.py
"""

# Import supporting modules
from pymongo import MongoClient
import os, sys
import subprocess
import logging
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

class Db4eDb():

  def __init__(self):
    ini = Db4eConfig()
    # Setup the logger object
    log_level_str        = ini.config['db4e']['log_level']
    self._retry_timeout  = ini.config['db']['retry_timeout']
    self._db_server      = ini.config['db']['server']
    self._db_port        = ini.config['db']['port']
    self._db_name        = ini.config['db']['name']
    self._db_collection  = ini.config['db']['collection']
    self._log_collection = ini.config['db']['log_collection']
    self._backup_dir     = ini.config['db']['backup_dir']
    self._debug          = ini.config['db4e']['debug']
    
    install_dir = ini.config['db4e']['install_dir']
    backup_dir = ini.config['db']['backup_dir']
    backup_script = ini.config['db']['backup_script']
    
    self._backup_script = os.path.join(install_dir, backup_script)
    self._backup_dir = os.path.join(install_dir, backup_dir)
    self._db_name = ini.config['db']['name']

    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    self.logger = logging.getLogger('db4e')
    self.logger.setLevel(log_level)

    self.connected = False
    self.init_db()

  def backup_db(self):
    backup_script = self._backup_script
    backup_dir = self._backup_dir
    db_name = self._db_name
    subprocess.run([backup_script, db_name, backup_dir])
    self.log(logging.INFO, f'Created a new backup in {backup_dir}')

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
      self.log(logging.CRITICAL, f'Could not connect to DB ({db_server}:{db_port}), waiting {retry_timeout} seconds')
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
      db[db_col]
    if log_col not in db_col_names:
      db[log_col]

  def insert_uniq_one(self, collection, jdoc):
    col = self.db[collection]
    doc_type = jdoc['doc_type']
    timestamp = jdoc['timestamp']
    if not col.find_one({'doc_type': doc_type, 'timestamp': timestamp}):
      col.insert_one(jdoc)
      self.log(logging.INFO, f'New DB record ({doc_type})')

  def log(self, level, message, extra):
    extra = dict(extra or {})
    if 'component' in extra:
      component = extra['component']
    else:
      component = 'Db4eDb'

    log_entry = {
      'timestamp': datetime.now(timezone.utc),
      'level': logging.getLevelName(level), 
      'message': message,
      'component': component
    }

    if 'new_file' in extra:
      log_entry['new_file'] = extra['new_file']
    if 'file_type' in extra:
      log_entry['file_type'] = extra['file_type']
      
    db = self.db()
    log_col = db[self._log_collection]
    log_col.insert_one(log_entry)



