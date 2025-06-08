"""
lib/Infrastructure/Db4eLogHandler/Db4eLogHandler.py
"""

# Import supporting modules
import os, sys
import logging

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
from Db4eLogger.Db4eLogger import Db4eLogger


class MongoHandler(logging.Handler):

  def emit(self, record):
      component = getattr(record, 'component', 'core')
      extra_fields = {
          k: v for k, v in record.__dict__.items()
          if k not in ('name', 'msg', 'args', 'levelname', 'levelno',
                        'pathname', 'filename', 'module', 'exc_info',
                        'exc_text', 'stack_info', 'lineno', 'funcName',
                        'created', 'msecs', 'relativeCreated', 'thread',
                        'threadName', 'processName', 'process')
      }

      logger_instance = Db4eLogger(component=component)
      logger_instance.db.log(record.levelno, record.getMessage(), extra_fields)

class Db4eLoggerAdapter(logging.LoggerAdapter):
  def process(self, msg, kwargs):
      # Inject component into the `extra` dict
      if 'extra' not in kwargs:
          kwargs['extra'] = {}
      kwargs['extra']['component'] = self.extra.get('component', 'core')
      return msg, kwargs
  
def get_db4e_logger(component='core'):
    base_logger = logging.getLogger('db4e')
    return Db4eLoggerAdapter(base_logger, {'component': component})
