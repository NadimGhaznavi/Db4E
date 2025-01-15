"""
lib/Mining/SharesFoundCsv/SharesFoundCsv.py
"""

import os, sys
import datetime

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eStartup.Db4eStartup import Db4eStartup
from MiningDb.MiningDb import MiningDb
from Db4eGit.Db4eGit import Db4eGit

class SharesFoundCsv():

  def __init__(self, log_function):
    startup = Db4eStartup()
    self._debug = startup.debug()
    self.log = log_function

  def new_shares_found_csv(self):
    if self._debug == 9:
      self.log("SharesFoundCsv.new_blocks_found_csv()\n")
    db = MiningDb()
    shares_found = db.get_docs('share_found_event')
    
    shares_found_dict = {}
    for event in shares_found:
      timestamp = event['timestamp'].strftime("%Y-%m-%d")
      if timestamp not in shares_found_dict:
        shares_found_dict[timestamp] = 1
      else:
        shares_found_dict[timestamp] = shares_found_dict[timestamp] + 1

    key_list = []
    for key in shares_found_dict.keys():
      key_list.append(key)

    key_list.sort()

    startup = Db4eStartup()
    csv_filename = startup.shares_found_csv()
    try:
      csv_handle = open(csv_filename, 'w')
    except:
      self.log(f"ERROR: Unable to open Shares Found CSV ({csv_filename})")

    csv_handle.write("Date,Shares Found\n")
    for key in key_list:
      csv_handle.write(str(key) + "," + str(shares_found_dict[key]) + "\n")
    
    csv_handle.close()
      
    db4e_git = Db4eGit()
    db4e_git.push(csv_filename, 'Updated Shares Found')
    self.log(f"  Shares Found CSV : {csv_filename}")
