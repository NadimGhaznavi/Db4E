#!/opt/prod/db4e/venv/bin/python
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
from MiningReports.MiningReports import MiningReports

print("Database 4 Everything")

ini = Db4eConfig()

if 'reports' in ini.config['export']:
  report = ini.config['export']['reports']
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
  db.backup_db()
  

