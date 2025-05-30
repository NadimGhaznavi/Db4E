#!/home/db4e/db4e/bin/python

"""
monerod-status.py - Monero daemon status script

This script checks the status of a Monero daemon and outputs the result.
"""

import os, sys

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../lib"
# Import DB4E modules
db4e_dirs = [
  lib_dir + '/Infrastructure',
  lib_dir + '/Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig
from MoneroD.MoneroD import MoneroD

# Load the db4e configuration
config = Db4eConfig()

monerod = MoneroD()
log_file = monerod.log_file()
stdin_pipe = monerod.stdin_pipe()

print("Monero Daemon Status:")

# Make sure the log file exists
print(f"Log file: {log_file}")
if not os.path.exists(log_file):
    print("ERROR: Monerod log file does not exist.")
    sys.exit(1)

# Make sure the STDIN pipe exists
print(f"STDIN pipe: {stdin_pipe}")
if not os.path.exists(stdin_pipe):
    print("ERROR: Monerod STDIN pipe does not exist.")
    sys.exit(1)

monerod.get_height()

