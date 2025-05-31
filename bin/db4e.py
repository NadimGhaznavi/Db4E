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
from P2PoolPaymentCsv.P2PoolPaymentCsv import P2PoolPaymentCsv
from BlocksFoundCsv.BlocksFoundCsv import BlocksFoundCsv
from SharesFoundCsv.SharesFoundCsv import SharesFoundCsv
from SharesFoundByHostCsv.SharesFoundByHostCsv import SharesFoundByHostCsv
from HashRates.HashRates import Hashrates
from MiningDb.MiningDb import MiningDb
from Db4eDb.Db4eDb import Db4eDb
from Db4eLog.Db4eLog import Db4eLog

print("Database 4 Everything")

# See if the user passed in an action
config = Db4eConfig()
action = config.config['db4e']['action']
logger = Db4eLog()
log_func = logger.log_msg

if action:
  if action == 'get_wallet_balance':
    db = MiningDb()
    balance = db.get_wallet_balance()
    print(f"Wallet balance: {balance} XMR")
  elif action == 'monitor_p2pool_log':
    p2pool = P2Pool()
    p2pool.monitor_log()
  elif action == 'new_p2pool_payment_csv':
    csv = P2PoolPaymentCsv(log_func)
    csv.new_p2pool_payment_csv()
  elif action == 'new_blocks_found_csv':
    csv = BlocksFoundCsv(log_func)
    csv.new_blocks_found_csv()
  elif action == 'new_shares_found_csv':
    csv = SharesFoundCsv(log_func)
    csv.new_shares_found_csv()
  elif action == 'new_shares_found_by_host_csv':
    csv = SharesFoundByHostCsv(log_func)
    csv.new_shares_found_by_host_csv()
  elif action == 'new_hashrates_csv':
    csv = Hashrates(log_func)
    csv.new_hashrates_csv()
  elif action == 'backup_db':
    db = Db4eDb()
    db.backup_db()
  else:
    print(f"ERROR: Unknown action ({action}), use '-la' to get a list of valid actions.")
