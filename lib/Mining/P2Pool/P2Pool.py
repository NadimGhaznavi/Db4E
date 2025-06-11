""""
lib/Mining/P2pool/P2Pool.py

The P2Pool class is responsible for monitoring the P2Pool log file
and querying the P2Pool API. It creates MongoDB records based on
events in the logs and triggers new report generation (e.g. payments)
when appropriate.
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


# Import supporting modules
import os, sys
import time
import re
from datetime import datetime
from decimal import Decimal
import json
from bson.decimal128 import Decimal128

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig
from MiningDb.MiningDb import MiningDb
from Db4eLogger.Db4eLogger import Db4eLogger
from MiningReports.MiningReports import MiningReports

# This is the name of the file where the P2Pool daemon stores info
P2POOL_API_FILE = 'stats_mod'

class P2Pool():

  def __init__(self):
    # Get configuration values
    ini = Db4eConfig ()
    self._install_dir = ini.config['p2pool']['install_dir']
    self._api_dir     = ini.config['p2pool']['api_dir']
    log_dir           = ini.config['p2pool']['log_dir']
    log_file          = ini.config['p2pool']['log_file']
    self._p2pool_log  = os.path.join(self._install_dir, log_dir, log_file)
    
    # Get a backend Mining DB object
    self._db = MiningDb()
    # Get a backend Logging object
    self.log = Db4eLogger('P2Pool')

  def db(self):
    return self._db
  
  def get_sidechain_miners(self):
    install_dir = self._install_dir
    api_dir = self._api_dir
    api_file = P2POOL_API_FILE

    api = os.path.join(install_dir, api_dir, api_file)
    if not os.path.exists(api):
      self.log.error(f'P2Pool API file not found: {api_file}')
    with open(api, 'r') as file:
      api_string_data = file.read()
      api_data = json.loads(api_string_data)
      return api_data['pool']['miners']
  
  def is_block_found(self, log_line):
    """
    Sample log messages to watch for:

    2024-11-09 19:52:19.1734 P2Pool BLOCK FOUND: main chain block at height 3277801 was mined by someone else in this p2pool
    """
    pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} P2Pool BLOCK FOUND"
    match = re.search(pattern, log_line)
    if match:
      timestamp = match.group('timestamp')
      timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
      # Create a new blocks_found_event in the DB
      db = self.db()
      db.add_block_found(timestamp)
      # Generate fresh 'blocksfound' reports
      reports = MiningReports('blocksfound')
      reports.run()
      # Log the event
      self.log.debug('Block found')

  def is_main_chain_hashrate(self, log_line):
    """
    Sample log message to watch for:

    Main chain hashrate       = 3.105 GH/s
    Main chain hashrate       = 5.079 GH/s
    """
    pattern = r"Main chain hashrate .* = (?P<hashrate>.*H/s)"
    match = re.search(pattern, log_line)
    localtime = datetime.now().strftime("%H:%M")
    if match:
      hashrate = match.group('hashrate')
      db = self.db()
      db.add_mainchain_hashrate(hashrate)
      self.log.debug(f"Detected mainchain hashrate ({hashrate})")

  def is_pool_hashrate(self, log_line):
    """
    Sample log message to watch for:

    Your hashrate (pool-side) = 13.137 KH/s
    Hashrate (1h  est)   = 7.384 KH/s
    """
    pattern = r"Hashrate \(1h  est\) .* = (?P<hashrate>.*H/s)"
    match = re.search(pattern, log_line)
    localtime = datetime.now().strftime("%H:%M")
    if match:
      hashrate = match.group('hashrate')
      db = self.db()
      db.add_pool_hashrate(hashrate)
      self.log.debug(f"Detected pool hashrate ({hashrate})")

  def is_share_found(self, log_line):
    """
    Sample log messages to watch for:

    2024-11-10 00:47:47.5596 StratumServer SHARE FOUND: mainchain height 3277956, sidechain height 9143872, diff 126624856, client 192.168.0.86:37294, user sally, effort 91.663%
    """
    pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} StratumServer SHARE FOUND:.*client (?P<ip_addr>\d+.\d+.\d+.\d+):\d+, user (?P<worker>.*), effort (?P<effort>\d+.\d+)"
    match = re.search(pattern, log_line)
    if match:
      timestamp = match.group('timestamp')
      timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
      ip_addr = match.group('ip_addr')
      worker = match.group('worker')
      effort = float(match.group('effort'))
      db = self.db()
      db.add_share_found(timestamp, worker, ip_addr, effort)
      reports = MiningReports('blocksfound')
      reports.run()
      self.log.debug('Share found event', { 'miner': worker }) 

  def is_share_position(self, log_line):
    """
    Sample log messages to watch for:

    Your shares position      = [.........................1....]
    Your shares               = 0 blocks (+0 uncles, 0 orphans)
    """
    pattern = r"Your shares position .* = (?P<position>\[.*\])"
    match = re.search(pattern, log_line)
    if match:
      position = match.group('position')
      timestamp = datetime.now()
      db = self.db()
      db.add_share_position(timestamp, position)
      self.log.debug(f'Detected share position ({position})')
    pattern = r"Your shares .* = 0 .*"
    match = re.search(pattern, log_line)
    if match:
      position = '[..............................]'
      timestamp = datetime.now()
      db = self.db()
      db.add_share_position(timestamp, position)
      self.log.debug(f'Detected share position ({position})')

  def is_side_chain_hashrate(self, log_line):
    """
    Sample log message to watch for:

    Side chain hashrate       = 12.291 MH/s
    """
    pattern = r"Side chain hashrate .* = (?P<hashrate>.*H/s)"
    match = re.search(pattern, log_line)
    localtime = datetime.now().strftime("%H:%M")
    if match:
      hashrate = match.group('hashrate')
      db = self.db()
      db.add_sidechain_hashrate(hashrate)
      self.log.debug(f'Detected sidechain hashrate ({hashrate})')

      # While we're at it, let's also collect the number of miners 
      # on the sidechain at this time.
      sidechain_miners = self.get_sidechain_miners()
      db.add_sidechain_miners(sidechain_miners)
      self.log.debug(f'Detected sidechain miners ({sidechain_miners})')


  def is_worker_stats(self, log_line):
    """
    Sample log message to watch for:
    
    2024-11-09 20:05:01.4647 StratumServer 192.168.0.27:57888         no     14h 59m 52s         23666               788 H/s        paris
    """
    # Look for a worker stat line
    pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} StratumServer (?P<ip_addr>\d+.\d+.\d+.\d+):\d+\s+no\s+\d+h \d+m \d+s\s+\d+\s+(?P<hashrate>\d+.*) (?P<unit>[H|K]).*/s\s+ (?P<worker_name>.*$)"
    match = re.search(pattern, log_line)
    if match:
      hashrate = float(match.group('hashrate'))
      unit = match.group('unit')
      if unit == 'K':
        # Convert KH/s into H/s
        hashrate = hashrate * 1000
        hashrate = int(hashrate)
      worker_name = match.group('worker_name')
      db = self.db()
      db.update_worker(worker_name, hashrate)
      self.log.debug(f'Detected miner ({worker_name}) hashrate ({hashrate} H/s)') 

  def is_xmr_payment(self, log_line):
    """
    Sample log message to watch for:

    2024-11-09 19:52:19.1740 P2Pool Your wallet 48wY7nYBsQNSw7fDEG got a payout of 0.001080066485 XMR in block 3277801
    2025-06-02 21:42:53.0727 P2Pool Your wallet 48wdY6fDEG got a payout of 0.000295115076 XMR in block 3425427
    """
    pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} .*got a payout of (?P<payout>0.\d+) XMR"
    match = re.search(pattern, log_line)
    if match:
      timestamp = match.group('timestamp')
      timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
      payout = Decimal128(match.group('payout'))
      db = self.db()
      db.add_xmr_payment(timestamp, payout)
      reports = MiningReports('payments')
      reports.run()
      self.log.debug(f"Payout event ({payout}) XMR", {'payout': {payout.to_decimal()}})

  def monitor_log(self):
    log_filename = self._p2pool_log
    self.log.info(f"Monitoring log file ({log_filename})...")

    try:    
      p2p_log = open(log_filename, 'r')
    except FileNotFoundError:
      self.log.critical(f"P2Pool log file ({log_filename}) not found, exiting")
      return None
    
    self._loglines = self.watch_log(p2p_log)
    loglines = self.watch_log(p2p_log)
                                           
    for log_line in loglines:
      self.is_worker_stats(log_line)
      self.is_share_found(log_line)
      self.is_share_position(log_line)
      self.is_block_found(log_line)
      self.is_xmr_payment(log_line)
      self.is_side_chain_hashrate(log_line)
      self.is_main_chain_hashrate(log_line)
      self.is_pool_hashrate(log_line)

  def watch_log(self, p2p_log):
    p2p_log.seek(0, os.SEEK_END)

    while True:
      log_line = p2p_log.readline()
      if not log_line:
        time.sleep(1)
        continue

      yield log_line

