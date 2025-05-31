"""
lib/Mining/export/HashRates/HashRates.py
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
from Db4eExport.Db4eExport import Db4eExport
from Db4eGit.Db4eGit import Db4eGit

class Hashrates():

  def __init__(self, log_function):
    config = Db4eConfig()
    self._debug = config.config['db4e']['debug']
    self._export_dir = config.config['export']['export_dir']
    self.log = log_function
    # Define the hashrates we're interested in
    self._hashrate_names = ['pool', 'sidechain', 'mainchain']
    self._header = "Datetime,Hashrate\n"

  def _export_hashrate(self, hashrate):
    
    # The hashrate data has been loaded with self.refresh_data()`
    hash_data = self._hashrate_data[hashrate]

    # Open the CSV file for writing
    hash_filename = f"{self._export_dir}/{hashrate}_hashrates.csv"
    hash_handle = open(hash_filename, 'w')
    
    # Write the header to the CSV file
    hash_handle.write(self._header)

    # Loop through the hashrate data and populate the CSV file
    for data in hash_data:
      # Get the timestamp and convert it to a date string
      timestamp = data['timestamp'] + ':00:00'
      # The hashrate data is in KH/s (e.g. "6.889 KH/s")
      hashrate_value = data['hashrate'].split(' ')[0]
      value = f"{timestamp},{hashrate_value}\n"
      if self._debug:
        print(value)
      hash_handle.write(value)
    hash_handle.close()

    # Push the CSV file to the git repository
    git = Db4eGit()
    git.push(hash_filename, 'New hashrate data export')
    self.log(f"  New export file: {hash_filename}")

    # Generate 30, 60 and 90 day short versions of the CSV file
    export_utils = Db4eExport(self.log)
    export_utils.in_file(hash_filename)
    export_utils.units('days')
    for num_days in [30, 60, 90]:
      export_utils.datapoints(num_days)
      # Generate the short version of the CSV file
      export_utils.export_short()

  def new_hashrates_csv(self):
    # Generate a set of CSV hashrate data files.

    # Fetch fresh data from the MiningDb
    self._refresh_data()

    # Generate the CSV files with the fresh data
    for hashrate in self._hashrate_names:
      self._export_hashrate(hashrate)

  def _refresh_data(self):
    # Get the latest data from the MiningDb
    db = MiningDb()
    self._hashrate_data = {}
    for hashrate in self._hashrate_names:
      # MongoDB document name 
      doc_name = f"{hashrate}_hashrate"
      self._hashrate_data[hashrate] = db.get_docs(doc_name)
