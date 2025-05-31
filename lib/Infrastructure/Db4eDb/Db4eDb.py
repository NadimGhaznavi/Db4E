"""
lib/Infrastructure/Db4eDb/Db4eDb.py
"""

# Import supporting modules
from pymongo import MongoClient
import os, sys
import subprocess

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
    config = Db4eConfig()
    self._db_server = config.config['db']['server']
    self._db_port = config.config['db']['port']
    self._db_name = config.config['db']['name']
    self._db_collection = config.config['db']['collection']
    self._debug = config.config['db4e']['debug']
    self._backup_dir = config.config['db']['backup_dir']
    
    install_dir = config.config['db4e']['install_dir']
    backup_dir = config.config['db']['backup_dir']
    backup_script = config.config['db']['backup_script']
    
    self._backup_script = os.path.join(install_dir, backup_script)
    self._backup_dir = os.path.join(install_dir, backup_dir)
    self._db_name = config.config['db']['name']
    self.init_db()

  def backup_db(self):
    backup_script = self._backup_script
    backup_dir = self._backup_dir
    db_name = self._db_name
    subprocess.run([backup_script, db_name, backup_dir])

  def db(self):
    db_server = self._db_server
    db_port = self._db_port
    db_name = self._db_name
    try:
      db_client = MongoClient(f"mongodb://{db_server}:{db_port}/")
    except:
      print("FATAL ERROR: Could not connect to DB ({db_server}:{db_port}), exiting...")
      sys.exit(1)
    return db_client[db_name]

  def get_docs(self, collection_name, doc_type):
    if self._debug == 9:
      print("Db4eDb:get_docs(collection_name, doc_type)")
      print(f"  collection_name : ({collection_name})")
      print(f"  doc_type        : ({doc_type})\n")
    db = self.db()
    collection = db[collection_name]
    db_cursor = collection.find({'doc_type': doc_type})
    if self._debug == 9:
      print("Db4eDb:get_docs(collection_name, doc_type)")
      print(f"  returns         ; ({db_cursor})\n")
    return db_cursor

  def init_db(self):
    db = self.db()
    db_col = self._db_collection
    if db_col not in db.list_collection_names():
      db[db_col]

  def insert_uniq_one(self, collection, jdoc):
    db = self.db()
    col = db[collection]
    doc_type = jdoc['doc_type']
    timestamp = jdoc['timestamp']
    if not col.find_one({'doc_type': doc_type, 'timestamp': timestamp}):
      col.insert_one(jdoc)




