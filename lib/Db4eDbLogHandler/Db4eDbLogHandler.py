"""
lib/Db4eDbLogHandler/Db4eDbLogHandler

This class implements a Python logging log handler that sends log 
records to MongoDB.


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


# Import supporting modules
from pymongo import MongoClient
import os
import sys
import logging
from datetime import datetime, timezone
import traceback
import time

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eOSStrings.Db4eOSStrings import LOG_LEVELS

class Db4eDbLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()

        ini = Db4eConfig()
        self._retry_timeout  = ini.config['db']['retry_timeout']
        self._db_server      = ini.config['db']['server']
        self._db_port        = ini.config['db']['port']
        self._db_name        = ini.config['db']['name']
        self._log_collection = ini.config['db']['log_collection']

        # Flag for connection status
        self.connected = False
        # Database handle
        self._db = None

    def emit(self, record):
        log_entry = {
            'timestamp': datetime.now(timezone.utc),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        # Copy any custom attributes from the record
        for attr in ('component', 'miner', 'new_file', 'file_type'):  # list whatever custom fields you expect
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)

        try:
            self.log_db_message(log_entry)
        except Exception as e:
            print(f"Db4eDbLogHandler: Failed to log to DB: {e}", file=sys.stderr)
            traceback.print_exc()

    def db(self):
        if not self.connected:
            self.connect()
        return self._db
    
    def connect(self):
        db_server = self._db_server
        db_port = self._db_port
        db_name = self._db_name
        retry_timeout = self._retry_timeout
        try:
            client = MongoClient(f"mongodb://{db_server}:{db_port}/")
        except:
            self.log.critical(f'Could not connect to DB ({db_server}:{db_port}), waiting {retry_timeout} seconds')
            time.sleep(retry_timeout)
        self.connected = True
        self._db = client[db_name]        

    def log_db_message(self, log_entry):
        db = self.db()
        log_col = self._log_collection 
        col = db[log_col]
        col.insert_one(log_entry)
 
