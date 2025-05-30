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

from Db4eConfig.Db4eConfig import Db4eConfig
from MiningDb.MiningDb import MiningDb
from Db4eGit.Db4eGit import Db4eGit

class BlocksFoundCsv():

  def __init__(self, log_function):
    config = Db4eConfig()
    self._debug = config.config['db4e']['debug']
    export_dir = config.config['export']['export_dir']
    blocks_found_csv = config.config['export']['blocks_found_csv']
    self._csv_filename = os.path.join(export_dir, blocks_found_csv)
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


    # Create the Blocks Found CSV file
    csv_filename = self._csv_filename
    try:
      csv_handle = open(csv_filename, 'w')
    except:
      self.log(f"ERROR: Unable to open Blocks Found CSV ({csv_filename})")

    csv_header = "Date,Blocks Found\n"
    csv_handle.write(csv_header)
    for key in key_list:
      csv_handle.write(str(key) + "," + str(blocks_found_dict[key]) + "\n")
    csv_handle.close()

    # Create a shorter version of the CSV file, last 30 days
    short_csv_filename = csv_filename.replace('.csv', '_short.csv')
    csv_short_handle = open(short_csv_filename, 'w')
    csv_short_handle.write(csv_header)
    # Get the last 30 days of data
    csv_handle = open(csv_filename, 'r')
    lines = csv_handle.readlines()
    datapoints = 30
    for line in lines[-datapoints:]:
      csv_short_handle.write(line)
    csv_short_handle.close()
    csv_handle.close()

    # Push the CSV files to the git repository      
    db4e_git = Db4eGit()
    db4e_git.push(csv_filename, 'Updated Blocks Found')
    db4e_git.push(short_csv_filename, 'Updated Blocks Found')

    # Log the CSV file paths
    self.log(f"  Blocks Found CSV : {csv_filename}")
    self.log(f"  Blocks Found CSV : {short_csv_filename}")
