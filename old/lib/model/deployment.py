"""
lib/model/deployment.py


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
import os, sys
from datetime import datetime, timezone
import getpass

# Setup the db4e paths
DB4E_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 
DB4E_LIB_DIR = os.path.join(DB4E_DIR, 'lib')
DB4E_COMPONENTS_DIR = os.path.join(DB4E_LIB_DIR, 'components')
DB4E_MODEL_DIR = os.path.join(DB4E_LIB_DIR, 'model')
sys.path.append(DB4E_LIB_DIR)
sys.path.append(DB4E_COMPONENTS_DIR)
sys.path.append(DB4E_MODEL_DIR)

from db4e_db import Db4eDb
from settings import Db4eConfig

# The Mongo collection that houses the deployment records
DEPL_COL = 'depl'

class DeplModel:

    def __init__(self):
        self.db = Db4eDb()
        self.ini = Db4eConfig()
        self.col = DEPL_COL

    def add_deployment(self, rec):
        rec['doc_type'] = 'deployment'
        rec['updated'] = datetime.now(timezone.utc)
        # Get the component version from the static YAML config file
        rec['version'] = self.ini.config[rec['component']]['version']
        if rec['component'] == 'db4e':
            rec['user'] = getpass.getuser()
            rec['install_dir'] = DB4E_DIR
        self.db.insert_one(self.col, rec)

    def get_deployment(self, component):
        # Ask the db for the component record
        rec = self.db.find_one(self.col, {'doc_type': 'deployment', 'component': component})
        # Found it, so return it.
        if rec:
            return rec
        # No record for this deployment exists

        # Check if this is the first time the app has been run
        rec = self.db.find_one(self.col, {'doc_type': 'deployment', 'component': 'db4e'})
        if not rec:
            return False
        
        rec = self.db.get_new_rec(component)
        self.add_deployment(rec)
        # Call ourself, now there will be a record
        return self.get_deployment(component) 

    def get_deployment_by_instance(self, component, instance):
        if instance == 'db4e core':
            return self.get_deployment('db4e')





