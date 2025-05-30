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
from Db4eConfig.Db4eConfig import Db4eConfig

def write_csv_file(hashrates, csv_filename, short=False, debug=False):

  if debug:
    print(f"CSV filename {csv_filename}, Hashrates {hashrates}")

  csv_handle = open(csv_filename, 'w')
  csv_header = "Datetime,Hashrate\n"
  csv_handle.write(csv_header)

  # Loop through the hashrate data and populate the dictionary
  for data in hashrates:
    # Get the timestamp and convert it to a date string
    timestamp = data['timestamp'] + ':00:00'
    # The hashrate data is in KH/s (e.g. "6.889 KH/s")
    hashrate = data['hashrate'].split(' ')[0]
    value = f"{timestamp},{hashrate}\n"
    if debug:
      print(value)
    csv_handle.write(value)

  # Close the CSV file
  csv_handle.close()

  # Generate a shorter version, last 30 days
  short_csv_filename = csv_filename.replace('.csv', '_short.csv')
  csv_short_handle = open(short_csv_filename, 'w')
  csv_short_handle.write(csv_header)
  # Get the last 30 days of data
  csv_handle = open(csv_filename, 'r')
  lines = csv_handle.readlines()
  datapoints = 24 * 30 # hourly data for 30 days
  for line in lines[-datapoints:]:
    csv_short_handle.write(line)    
  csv_short_handle.close()
  csv_handle.close()
      
  # Upload to Github
  db4e_git = Db4eGit()
  db4e_git.push(csv_filename, 'Updated hashrate data')
  db4e_git.push(short_csv_filename, 'Updated hashrate data')

# Load the DB4E configuration
config = Db4eConfig()

# Connect to the DB4E database
db = MiningDb()

# CSV files are exported here
export_dir = config.config['export']['export_dir']

# Pool hashrate data
pool_hashrates = db.get_docs('pool_hashrate')
pool_filename = os.path.join(export_dir, config.config['export']['pool_hashrates_csv'])
write_csv_file(pool_hashrates, pool_filename)

# Sidechain hashrate data
sidechain_hashrates = db.get_docs('sidechain_hashrate')
sidechain_filename = os.path.join(export_dir, config.config['export']['sidechain_hashrates_csv'])
write_csv_file(sidechain_hashrates, sidechain_filename)

# Mainchain hashrate data
mainchain_hashrates = db.get_docs('mainchain_hashrate')
mainchain_filename = os.path.join(export_dir, config.config['export']['mainchain_hashrates_csv'])
write_csv_file(mainchain_hashrates, mainchain_filename)
