"""
Infrastructure/Db4eLog/Db4eLog.py
"""
import os, sys, inspect

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig

class Db4eLog():

  def __init__(self):
    config = Db4eConfig()

    install_dir = config.config['db4e']['install_dir']
    log_dir = config.config['db4e']['log_dir']
    log_file = config.config['db4e']['log_file']

    self._db4e_log = os.path.join(install_dir, log_dir, log_file)
    self._db4e_log_handle = None

  def __del__(self):
    if self._db4e_log_handle:
      self._db4e_log_handle.close()

  def log_msg(self, msg):
    if not self._db4e_log_handle:
      self._db4e_log_handle = open(self._db4e_log, 'a')
    self._db4e_log_handle.write(msg + '\n')
    self._db4e_log_handle.flush()

