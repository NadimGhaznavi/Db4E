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

from Db4eStartup.Db4eStartup import Db4eStartup

class Db4eDb():

  def __init__(self):
    startup = Db4eStartup()
    self._db_server = startup.db_server()
    self._db_port = startup.db_port()
    self._db_name = startup.db_name()
    self._debug = startup.debug()
    self._backup_db_script = startup.backup_db_script()
    self._environ = startup.environ()
    self.init_db()

  def backup_db(self):
    backup_script = self._backup_db_script
    environ = self._environ
    subprocess.run([backup_script, environ])

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
    if 'mining' not in db.list_collection_names():
      db['mining']

  def insert_uniq_one(self, collection, jdoc):
    db = self.db()
    col = db[collection]
    doc_type = jdoc['doc_type']
    timestamp = jdoc['timestamp']
    if not col.find_one({'doc_type': doc_type, 'timestamp': timestamp}):
      col.insert_one(jdoc)




