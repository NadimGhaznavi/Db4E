#!/usr/bin/python3
"""
test/lib/Infrastructure/Db4eStartup
"""

import unittest
import os, sys

# Setup sys.path to include the DB4E modules
lib_dir = os.path.dirname(__file__) + "/../../../../lib"
db4e_dirs = [
  lib_dir + '/Infrastructure',
  lib_dir + '/Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eStartup.Db4eStartup import Db4eStartup

class TestDb4eStartup(unittest.TestCase):

  