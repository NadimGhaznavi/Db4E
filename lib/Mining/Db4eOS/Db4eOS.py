"""
lib/Infrastructure/Db4eOS/Db4eOS.py

The Db4eOS module is the backend to the db4e-os.sh deployment tool. It
manages the Operating System environment and helps users configure
and run *db4e*.
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

import os, sys
import subprocess
import psutil
import yaml

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

# DB4E modules
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eLogger.Db4eLogger import Db4eLogger
from Db4eOSDb.Db4eOSDb import Db4eOSDb

COMPONENTS = ['db4e', 'p2pool', 'monerod', 'xmrig', 'repo']

class Db4eOS:
    def __init__(self):
        # Possibly store paths, config state, environment, etc.
        ini  = Db4eConfig()
        # Set the db4e dir
        self.db4e_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
        # Setup the deployment config
        db4e_conf_dir = ini.config['db4e']['conf_dir']
        deployment_file = ini.config['db4e']['deployment_file']
        fq_path = os.path.join(self.db4e_dir, db4e_conf_dir, deployment_file)
        self._depl_file = fq_path
        self.load(fq_path)

        for component in COMPONENTS:
            self.probe_env(component)

    def get_pid(self, proc_name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc_name in proc.info['name']:
                return proc.info['pid']
        return None        

    def start_component(self, component):
        """
        Start a given component daemon or process.
        """
        pass

    def stop_component(self, component):
        """
        Stop the running process cleanly.
        """
        pass

    def probe_env(self, component):
        if component == 'repo':
            pass

    def load(self, yaml_file):
        with open(yaml_file, 'r') as file:
            self.depl = yaml.safe_load(file)
            self.depl['runtime'] = {}
            self.depl['runtime']['yaml_file'] = yaml_file