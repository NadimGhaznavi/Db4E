#!/usr/bin/python3
"""
bin/hashrates.py
"""

# Import supporting modules
import os
import sys
import datetime

# The directory that this script is in
script_dir = os.path.dirname(__file__)
# DB4E modules are in the lib_dir
lib_dir = script_dir + '/../lib/'
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from MiningDb.MiningDb import MiningDb
from Db4eGit.Db4eGit import Db4eGit
from Db4eStartup.Db4eStartup import Db4eStartup

# Initialize the DB4E startup
db4e_startup = Db4eStartup()

# Connect to the DB4E database
db = MiningDb()
# Retrieve the pool hashrate data
mainchain_hashrates = db.get_docs('pool_hashrate')
# Create a dictionary to hold the hashrate data
pool_hashrates_dict = {}
# The CSV filename to write the hashrate data to
csv_filename = db4e_startup.pool_hashrates_csv()
try:
  csv_handle = open(csv_filename, 'w')
  # print(f"Preparing to write to CSV file ({csv_filename})")
except:
  print(f"Error opening CSV file ({csv_filename}) for writing")
  sys.exit(1)

csv_header = "Datetime,Hashrate\n"
csv_handle.write(csv_header)
# Loop through the hashrate data and populate the dictionary
for data in mainchain_hashrates:
  # Get the timestamp and convert it to a date string
  timestamp = data['timestamp'] + ':00:00'
  # The hashrate data is in KH/s (e.g. "6.889 KH/s")
  hashrate = data['hashrate'].split(' ')[0]
  pool_hashrates_dict[timestamp] = data['hashrate']
  csv_handle.write(f"{timestamp},{hashrate}\n")
# Close the CSV file
csv_handle.close()
db4e_git = Db4eGit()
db4e_git.push(csv_filename, 'Updated Mainchain Pool Hashrate')

