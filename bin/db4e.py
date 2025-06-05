#!/usr/bin/python3
"""
bin/db4e.py
"""

# Import supporting modules
import os
import sys

# The directory that this script is in
script_dir = os.path.dirname(__file__)
# DB4E modules are in the lib_dir
lib_dir = script_dir + '/../lib/'

# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining',
  lib_dir + 'Mining/export'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig
from P2Pool.P2Pool import P2Pool
from MiningDb.MiningDb import MiningDb
from Db4eDb.Db4eDb import Db4eDb
from Db4eLog.Db4eLog import Db4eLog
from MiningReports.MiningReports import MiningReports

print("Database 4 Everything")

config = Db4eConfig()
logger = Db4eLog()
log_func = logger.log_msg

# See if the user passed in an action
if 'action' in config.config['db4e']:
  action = config.config['db4e']['action']

  if action == 'get_wallet_balance':
    db = MiningDb()
    balance = db.get_wallet_balance()
    print(f"Wallet balance: {balance} XMR")

  elif action == 'monitor_p2pool_log':
    p2pool = P2Pool(log_func)
    p2pool.monitor_log()

  elif action == 'backup_db':
    db = Db4eDb()
    db.backup_db()
  
  else:
    print(f"ERROR: Unknown action ({action}), use '-la' to get a list of valid actions.")

elif 'reports' in config.config['export']:
  report = config.config['export']['reports']
  reports = MiningReports(log_func, report)
  reports.run()

  

