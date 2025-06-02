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
from Db4eConfig.Db4eConfig import Db4eConfig

class Db4eGit():

  def __init__(self, repo_dir=None):
    # Load the DB4E configuration
    config = Db4eConfig()
    self._push_script = config.config['git']['push_script']
    self._git_script = config.config['git']['git_script']
    self._install_dir = config.config['db4e']['install_dir']
    self._debug = config.config['db4e']['debug']

    self._push_script = os.path.join(self._install_dir, self._push_script)
    self._git_script = os.path.join(self._install_dir, self._git_script)

    # New code uses this
    self._repo_dir = repo_dir
    
  def add(self, repo_file):
    git_script = self._git_script
    repo_dir = self._repo_dir
    subprocess.run([git_script, repo_dir, 'add', repo_file])

  def commit(self, msg):
    git_script = self._git_script
    repo_dir = self._repo_dir
    subprocess.run([git_script, repo_dir, 'commit', msg])

  def push(self, fully_qualified_file=None, comment=None):
    if comment:
      # Legacy git process
      base_file = os.path.basename(fully_qualified_file)
      repo_dir = os.path.dirname(fully_qualified_file)
      push_script = self._push_script
      if self._debug == 0:
        subprocess.run([push_script, repo_dir, base_file, comment])
      else:
        subprocess.run([push_script, repo_dir, base_file, comment, "1"])
    else:
      git_script = self._git_script
      subprocess.run([git_script, self._repo_dir, 'push'])


