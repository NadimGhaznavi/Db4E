"""
bin/db4e.py

This is the core *db4e* application. It is used to monitor the
P2Pool log, backup the db4e database and push the backup to 
GitHub, support a parallel QA environment, return the mining 
farm wallet balance (from MongoDB, not from your wallet), run
reports manuall and display the db4e version.


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

# Setup the db4e paths
DB4E_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
DB4E_MODULE_DIR = os.path.join(DB4E_DIR, 'lib')
sys.path.append(DB4E_MODULE_DIR)

from app import Db4eApp

if __name__ == "__main__":
    app = Db4eApp()
    app.run()

"""
# Old code references

from P2Pool.P2Pool import P2Pool
from MiningDb.MiningDb import MiningDb
from Db4eDb.Db4eDb import Db4eDb
from MiningReports.MiningReports import MiningReports
from Db4eLogger.Db4eLogger import Db4eLogger
from Db4eOSModel.Db4eOSModel import Db4eOSModel
from Db4eService.Db4eService import Db4eService

# Get a Python logging object
log = Db4eLogger('db4e.py')

# Import DB4E modules
from config import Db4eConfig

# Get a config object
ini = Db4eConfig()

try:

  if 'reports' in ini.config['db4e']:
    report = ini.config['db4e']['reports']
    reports = MiningReports(report)
    reports.run()

  elif 'monitor_log' in ini.config['p2pool']:
    p2pool = P2Pool()
    p2pool.monitor_log()

  elif 'wallet_balance' in ini.config['db4e']:
    db = MiningDb()
    balance = db.get_wallet_balance()
    print(f"Wallet balance: {balance} XMR")

  elif 'backup_db' in ini.config['db']:
    db = Db4eDb()
    # Get the current db4e and repo install directories
    os_model = Db4eOSModel()
    db.set_db4e_dir(os_model.get_db4e_dir())
    db.set_repo_dir(os_model.get_repo_dir())
    db.backup_db()

  elif ini.config['db4e']['service']:
    db4e_service = Db4eService()
    db4e_service.start()

except KeyboardInterrupt:
  log.warning("Caught keyboard interrupt, exiting...")
  log.shutdown() # Flush all handlers
  sys.exit(0)


"""



