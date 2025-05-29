"""
lib/Infrastructure/Db4eGit/Db4eGit.py
"""

import os, sys
import subprocess

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

# DB4E modules
from Db4eStartup.Db4eStartup import Db4eStartup

class Db4eGit():

  def __init__(self):
    startup = Db4eStartup()
    self._push_script = startup.git_push_script()
    self._debug = startup.debug()

  def push(self, fully_qualified_file, comment):
    base_file = os.path.basename(fully_qualified_file)
    base_dir = os.path.dirname(fully_qualified_file)
    push_script = self._push_script
    if self._debug == 1:
      subprocess.run([push_script, base_dir, base_file, comment])
    else:
      subprocess.run([push_script, base_dir, base_file, comment, "1"])

