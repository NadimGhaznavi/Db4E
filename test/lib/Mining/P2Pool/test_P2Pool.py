#!/usr/bin/python3
"""
test/lib/Mining/P2Pool/test_P2Pool.py
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

# Import the module we're testing
from P2Pool.P2Pool import P2Pool

class TestP2Pool(unittest.TestCase):

  def test___init__(self):
    p2pool = P2Pool()
    self.assertEqual('foo'.upper(), 'FOO')


if __name__ == '__main__':
  unittest.main()