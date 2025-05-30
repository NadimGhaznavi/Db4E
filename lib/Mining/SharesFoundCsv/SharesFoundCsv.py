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

from Db4eConfig.Db4eConfig import Db4eConfig
from MiningDb.MiningDb import MiningDb
from Db4eGit.Db4eGit import Db4eGit

class SharesFoundCsv():

  def __init__(self, log_function):
    config = Db4eConfig()
    self._debug = config.config['db4e']['debug']
    self.log = log_function

  def new_shares_found_csv(self):
    if self._debug == 9:
      self.log("SharesFoundCsv.new_blocks_found_csv()\n")
    db = MiningDb()
    shares_found = db.get_docs('share_found_event')
    
    shares_found_dict = {}
    for event in shares_found:
      timestamp = event['timestamp']
      timestamp = timestamp.replace(hour=0, minute=0, second=0)  # Get just the date part (YYYY-MM-DD) from the datetime object
      if timestamp not in shares_found_dict:
        shares_found_dict[timestamp] = 1
      else:
        shares_found_dict[timestamp] = shares_found_dict[timestamp] + 1

    key_list = []
    for key in shares_found_dict.keys():
      key_list.append(key)

    key_list.sort()

    # Create the Shares Found CSV file
    config = Db4eConfig()
    export_dir = config.config['export']['export_dir']
    shares_found_csv = config.config['export']['shares_found_csv']
    csv_filename = os.path.join(export_dir, shares_found_csv)
    try:
      csv_handle = open(csv_filename, 'w')
    except:
      self.log(f"ERROR: Unable to open Shares Found CSV ({csv_filename})")
    csv_header = "Date,Shares Found\n"
    csv_handle.write(csv_header)
    for key in key_list:
      csv_handle.write(str(key) + "," + str(shares_found_dict[key]) + "\n")
    csv_handle.close()

    # Create a shorter version of the CSV file, last 30 days
    short_csv_filename = csv_filename.replace('.csv', '_short.csv')
    csv_short_handle = open(short_csv_filename, 'w')
    csv_short_handle.write(csv_header)
    # Get the last 30 days of data
    csv_handle = open(csv_filename, 'r')
    lines = csv_handle.readlines()
    datapoints = 30  # hourly data for 30 days
    for line in lines[-datapoints:]:
      csv_short_handle.write(line)
    csv_short_handle.close()
    csv_handle.close()
    db4e_git = Db4eGit()
    db4e_git.push(csv_filename, 'Updated Shares Found')
    db4e_git.push(short_csv_filename, 'Updated Shares Found')

    self.log(f"  Shares Found CSV : {csv_filename}")
    self.log(f"  Shares Found CSV : {short_csv_filename}")
