"""
db4e/Modules/DeploymentManager.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""

import os, shutil
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
      if rec['component'] == 'db4e':
         rec['user'] = getpass.getuser()
      else:
         rec['version'] = self.ini.config[rec['component']]['version']
      self.db.insert_one(self.col_name, rec)

   def is_initialized(self):
      rec = self.db.find_one(self.col_name, {'doc_type': 'deployment', 'component': 'db4e'})
      if rec:
         return True
      else:
         return False

   def get_deployment(self, component):
      print(f"DeploymentMgr:get_deployment(): {component}")
      # Ask the db for the component record
      db_rec = self.db.find_one(self.col_name, {'doc_type': 'deployment', 'component': component})
      # rec is a cursor object.
      if db_rec:
         rec = {}
         component = db_rec['component']
         if component == 'db4e':
            rec['group'] = db_rec['group']
            rec['install_dir'] = db_rec['install_dir']
            rec['user'] = db_rec['user']
            rec['user_wallet'] = db_rec['user_wallet']
            rec['vendor_dir'] = db_rec['vendor_dir']
         return rec
      # No record for this deployment exists

      # Check if this is the first time the app has been run
      rec = self.db.find_one(self.col_name, {'doc_type': 'deployment', 'component': 'db4e'})
      if not rec:
         return False
        
   def get_deployment_by_instance(self, component, instance):
      if instance == 'db4e core':
         return self.get_deployment('db4e')
      
   def update_deployent(self, rec):
      component = rec['component']
      if component == 'db4e':
         filter = {'doc_type': 'deployment', 'component': 'db4e'}
         self.db.update_one(self.col_name, filter, rec)