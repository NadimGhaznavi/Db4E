"""
bin/db4e-purge-logs.py

This is a utility program that purges old log records from MongoDB.
This *only* purges log records. It does not touch the mining,
deployment or other MongoDB collections. This is basic housekeeping.


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
import os
import sys

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..', 'lib')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eDb.Db4eDb import Db4eDb

db = Db4eDb()
db.purge_old_logs()