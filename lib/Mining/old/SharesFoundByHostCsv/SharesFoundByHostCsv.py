"""
lib/Mining/SharesFoundByHostCsv/SharesFoundByHostCsv.py
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

class SharesFoundByHostCsv():

  def __init__(self, log_function):
    config = Db4eConfig()
    self._debug = config.config['db4e']['debug']
    export_dir = config.config['export']['export_dir']
    shares_found_csv = config.config['export']['shares_found_by_host_csv']
    self._csv_filename = os.path.join(export_dir, shares_found_csv)
    self.log = log_function

  def new_shares_found_by_host_csv(self):
    if self._debug == 9:
      self.log_msg("SharesFoundByHostCsv.new_shares_found_by_host_csv()")
    db = MiningDb()
    shares_found = db.get_docs('share_found_event')
    
    csv_data = {}
    workers = []
    for event in shares_found:
      timestamp = event['timestamp']
      # Replace the time part of the timestamp with 00:00:00
      timestamp = timestamp.replace(hour=0, minute=0,second=0,microsecond=0)
      worker = event['worker']

      if worker not in workers:
        workers.append(worker)

      if timestamp not in csv_data:
        csv_data[timestamp] = {}
      if worker not in csv_data[timestamp]:
        csv_data[timestamp][worker] = 0
      csv_data[timestamp][worker] += 1

    # Create the Shares Found CSV file
    csv_filename = self._csv_filename
    try:
      csv_handle = open(csv_filename, 'w')
    except:
      self.log(f"ERROR: Unable to open Shares Found CSV ({csv_filename})")

    csv_header = "Date," + ",".join(workers) + "\n"
    csv_handle.write(csv_header)
    key_list = sorted(csv_data.keys())
    for key in key_list:
      row_data = [str(key)]
      for worker in workers:
        if worker in csv_data[key]:
          row_data.append(str(csv_data[key][worker]))
        else:
          row_data.append("0")
      csv_handle.write(",".join(row_data) + "\n")
    csv_handle.close()

    # Create a shorter version of the CSV file, last 30 days
    short_csv_filename = csv_filename.replace('.csv', '_short.csv')
    csv_short_handle = open(short_csv_filename, 'w')
    csv_short_handle.write(csv_header)
    # Get the last 30 days of data
    csv_handle = open(csv_filename, 'r')
    lines = csv_handle.readlines()
    datapoints = 30  # 30 days of data
    for line in lines[-datapoints:]:
      csv_short_handle.write(line)
    csv_short_handle.close()
    csv_handle.close()

    # Push the CSV files to the git repository
    db4e_git = Db4eGit()
    db4e_git.push(csv_filename, 'Updated Shares Found')
    db4e_git.push(short_csv_filename, 'Updated Shares Found')

    # Log the CSV file paths
    self.log(f"  Shares Found CSV : {csv_filename}")
    self.log(f"  Shares Found CSV : {short_csv_filename}")
