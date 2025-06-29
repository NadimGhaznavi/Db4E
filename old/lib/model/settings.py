"""
lib/model/settings.py


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

import yaml
import os

DB4E_CONFIG = 'db4e.yml'

class Db4eConfig:

    def __init__(self):
        # Read the db4e settings
        conf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'conf'))
        config_file = os.path.join(conf_dir, DB4E_CONFIG)
        self.load(config_file)

    def load(self, config_file):
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)

