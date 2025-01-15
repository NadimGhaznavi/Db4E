"""
lib/Mining/BlocksFoundCsv/BlocksFoundCsv.py
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

class BlocksFoundCsv():

  def __init__(self, log_function):
    startup = Db4eStartup()
    self._debug = startup.debug()
    self.log = log_function

  def new_blocks_found_csv(self):
    if self._debug == 9:
      self.log("BlocksFoundCsv.new_blocks_found_csv()\n")
    db = MiningDb()
    blocks_found = db.get_docs('block_found_event')
    
    blocks_found_dict = {}
    for event in blocks_found:
      timestamp = event['timestamp'].strftime("%Y-%m-%d")
      if timestamp not in blocks_found_dict:
        blocks_found_dict[timestamp] = 1
      else:
        blocks_found_dict[timestamp] = blocks_found_dict[timestamp] + 1

    key_list = []
    for key in blocks_found_dict.keys():
      key_list.append(key)

    key_list.sort()

    startup = Db4eStartup()
    csv_filename = startup.blocks_found_csv()
    try:
      csv_handle = open(csv_filename, 'w')
    except:
      self.log(f"ERROR: Unable to open Blocks Found CSV ({csv_filename})")

    csv_handle.write("Date,Blocks Found\n")
    for key in key_list:
      csv_handle.write(str(key) + "," + str(blocks_found_dict[key]) + "\n")
    
    csv_handle.close()
      
    db4e_git = Db4eGit()
    db4e_git.push(csv_filename, 'Updated Blocks Found')
    self.log(f"  Blocks Found CSV : {csv_filename}")
