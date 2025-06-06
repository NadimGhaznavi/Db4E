"""
Infrastructure/Db4eLog/Db4eLog.py
"""
import os, sys
import logging
import json
from datetime import datetime

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eDb.Db4eDb import Db4eDb

class Db4eLog():

  def __init__(self, log_file=None):
    # Get the starting log level
    ini = Db4eConfig()
    # MongoDB setup
    self.db = Db4eDb()

  def log_msg(self, msg, extra=None):
    self.db.log(logging.WARN, 'Legacy ' + msg, extra)