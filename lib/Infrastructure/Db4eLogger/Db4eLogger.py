"""
lib/Infrastructure/Db4eLogger/Db4eLogger.py
"""

import os, sys
import logging

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eDb.Db4eDb import Db4eDb

class Db4eLogger:
    def __init__(self, component=None):
        self.db = Db4eDb()
        if component is not None:
            self._component = component
        else:
            self._component = 'core'

    def info(self, message, extra=None):
        extra = dict(extra or {})
        extra['component'] = self._component
        self.db.log(logging.INFO, message, extra)

    def debug(self, message, extra=None):
        extra = dict(extra or {})
        extra['component'] = self._component
        self.db.log(logging.DEBUG, message, extra)

    def warning(self, message, extra=None):
        extra = dict(extra or {})
        extra['component'] = self._component
        self.db.log(logging.WARNING, message, extra)

    def error(self, message, extra=None):
        extra = dict(extra or {})
        extra['component'] = self._component
        self.db.log(logging.ERROR, message, extra)

    def critical(self, message, extra=None):
        extra = dict(extra or {})
        extra['component'] = self._component
        self.db.log(logging.CRITICAL, message, extra)
