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

from Db4eStartup.Db4eStartup import Db4eStartup

class Db4eLog():

  def __init__(self):
    startup = Db4eStartup()
    self._db4e_log = startup.db4e_log()
    self._db4e_log_handle = None

    if startup.debug() == 9:
      # stack = inspect.stack()
      #
      ### ERROR: "self" doesn't exit.
      #
      #the_class = stack[1][0].f_locals["self"].__class__.__name__
      #the_class = stack[1][0].f_locals
      #the_method = stack[1][0].f_code.co_name
      #
      # See:
      # for x in the_class:
      #   print(x)
      # -to find the class name
      handle = open(self._db4e_log, 'a')
      handle.write("Db4eLog.__init__()\n")
      handle.close()

  def __del__(self):
    if self._db4e_log_handle:
      self._db4e_log_handle.close()

  def log_msg(self, msg):
    if not self._db4e_log_handle:
      self._db4e_log_handle = open(self._db4e_log, 'a')
    self._db4e_log_handle.write(msg + '\n')
    self._db4e_log_handle.flush()

