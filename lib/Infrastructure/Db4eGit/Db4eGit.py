"""
lib/Infrastructure/Db4eGit/Db4eGit.py

The Db4eGit module provides git support to *db4e*. It is used to manage 
the *db4e* GitHub Pages website and to push MongoDB backups to GitHub.
"""


"""
  This file is part of *db4e*, the *Database 4 Everything* project
  <https://github.com/NadimGhaznavi/db4e>, developed independently
  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
  <https://github.com/NadimGhaznavi/db4e>.
 
  This program is free software: you can redistribute it and/or 
  modify it under the terms of the GNU General Public License as 
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy (LICENSE.txt) of the GNU General 
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
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
from Db4eLogger.Db4eLogger import Db4eLogger

class Db4eGit():

  def __init__(self, repo_dir=None):
    # Load the DB4E configuration
    config = Db4eConfig()
    self._push_script = config.config['git']['push_script']
    self._git_script = config.config['git']['git_script']
    self._install_dir = config.config['db4e']['install_dir']

    self._push_script = os.path.join(self._install_dir, self._push_script)
    self._git_script = os.path.join(self._install_dir, self._git_script)

    # New code uses this
    self._repo_dir = repo_dir
    # Setup backend logging
    self.log = Db4eLogger('Db4eGit')
    
  def add(self, repo_file):
    git_script = self._git_script
    repo_dir = self._repo_dir
    subprocess.run([git_script, repo_dir, 'add', repo_file])
    self.log.debug(f'Added file ({repo_file})', {'new_file': repo_file, 'file_type': 'git'})

  def commit(self, msg):
    git_script = self._git_script
    repo_dir = self._repo_dir
    subprocess.run([git_script, repo_dir, 'commit', msg])
    self.log.debug(f'Executed a git commit for the added files')

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
      self.log.debug(f'Executed a git push for the added files')


