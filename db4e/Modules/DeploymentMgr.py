"""
db4e/Modules/DeploymentManager.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""
from datetime import datetime, timezone
import getpass

from db4e.Modules.ConfigMgr import Config
from db4e.Modules.DbMgr import DbMgr

# The Mongo collection that houses the deployment records
DEPL_COL = 'depl'

class DeploymentMgr:
    
   def __init__(self, config: Config):
      self.ini = config
      self.db = DbMgr(config)
      self.col_name = DEPL_COL

   def add_deployment(self, rec):
      rec['doc_type'] = 'deployment'
      rec['updated'] = datetime.now(timezone.utc)
      # Get the component version from the static YAML config file
      rec['version'] = self.ini.config[rec['component']]['version']
      if rec['component'] == 'db4e':
         rec['user'] = getpass.getuser()
         rec['vendor_dir'] = self.ini.config['db4e']['vendor_name']
         rec['group'] = self.ini.config['db4e']['group']
         rec['user_wallet'] = self.ini.config['db4e']['user_wallet']
      self.db.insert_one(self.col_name, rec)

   def is_initialized(self):
      rec = self.db.find_one(self.col_name, {'doc_type': 'deployment', 'component': 'db4e'})
      if rec:
         return True
      else:
         return False

   def get_deployment(self, component):
      # Ask the db for the component record
      rec = self.db.find_one(self.col_name, {'doc_type': 'deployment', 'component': component})
      # Found it, so return it.
      if rec:
         return rec
      # No record for this deployment exists

      # Check if this is the first time the app has been run
      rec = self.db.find_one(self.col_name, {'doc_type': 'deployment', 'component': 'db4e'})
      if not rec:
         return False
        
      rec = self.db.get_new_rec(component)
      self.add_deployment(rec)
      # Call ourself, now there will be a record
      return self.get_deployment(component) 

   def get_deployment_by_instance(self, component, instance):
      if instance == 'db4e core':
         return self.get_deployment('db4e')