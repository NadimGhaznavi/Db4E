""""
lib/Mining/P2pool/P2pool.py
"""

# Import supporting modules
import os, sys
import time
import re
from datetime import datetime
from decimal import Decimal
import json

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
from P2PoolPaymentCsv.P2PoolPaymentCsv import P2PoolPaymentCsv
from BlocksFoundCsv.BlocksFoundCsv import BlocksFoundCsv
from SharesFoundCsv.SharesFoundCsv import SharesFoundCsv
from SharesFoundByHostCsv.SharesFoundByHostCsv import SharesFoundByHostCsv

# This is the name of the file where the P2Pool daemon stores info
P2POOL_API_FILE = 'stats_mod'

class P2Pool():

  def __init__(self, log_func):
    # Setup access to centralized logging
    self.log = log_func
    # Get configuration values
    config = Db4eConfig()
    self._install_dir = config.config['p2pool']['install_dir']
    self._api_dir = config.config['p2pool']['api_dir']
    self._debug = config.config['db4e']['debug']

    log_dir = config.config['p2pool']['log_dir']
    log_file = config.config['p2pool']['log_file']
    self._p2pool_log = os.path.join(self._install_dir, log_dir, log_file)
    
    # Get a backend DB object
    self._db = MiningDb()

  def db(self):
    return self._db
  
  def get_sidechain_miners(self):
    install_dir = self._install_dir
    api_dir = self._api_dir
    api_file = P2POOL_API_FILE

    api = os.path.join(install_dir, api_dir, api_file)
    if not os.path.exists(api):
      raise FileNotFoundError(f"P2Pool API file not found: {api_file}")
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
      self.log("---------- Block Found ----------")
      self.log(f"  Timestamp        : {timestamp}")
      localtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      self.log(f"  Local Time       : {localtime}")
      db = self.db()
      db.add_block_found(timestamp)
      blocksfoundcsv = BlocksFoundCsv(self.log)
      blocksfoundcsv.new_blocks_found_csv()

  def is_main_chain_hashrate(self, log_line):
    """
    Sample log message to watch for:

    Main chain hashrate       = 3.105 GH/s
    """
    pattern = r"Main chain hashrate .* = (?P<hashrate>.*H/s)"
    match = re.search(pattern, log_line)
    localtime = datetime.now().strftime("%H:%M")
    if match:
      hashrate = match.group('hashrate')
      self.log(f"---------- ({localtime}) Main chain hashrate: {hashrate}")
      db = self.db()
      db.add_mainchain_hashrate(hashrate)

  def is_pool_hashrate(self, log_line):
    """
    Sample log message to watch for:

    Hashrate (1h  est) = 6.610 KH/s
    """
    pattern = r"Hashrate .*1h.* = (?P<hashrate>.*H/s)"
    match = re.search(pattern, log_line)
    localtime = datetime.now().strftime("%H:%M")
    if match:
      hashrate = match.group('hashrate')
      self.log(f"---------- ({localtime}) Pool hashrate: {hashrate}")
      db = self.db()
      db.add_pool_hashrate(hashrate)

  def is_share_found(self, log_line):
    """
    Sample log messages to watch for:

    2024-11-10 00:47:47.5596 StratumServer SHARE FOUND: mainchain height 3277956, sidechain height 9143872, diff 126624856, client 192.168.0.86:37294, user sally, effort 91.663%
    """
    if self._debug == 9:
      self.log("P2Pool.is_share_found()")
      self.log(f"  log_line: ({log_line})")
    pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} StratumServer SHARE FOUND:.*client (?P<ip_addr>\d+.\d+.\d+.\d+):\d+, user (?P<worker>.*), effort (?P<effort>\d+.\d+)"
    match = re.search(pattern, log_line)
    if match:
      timestamp = match.group('timestamp')
      timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
      ip_addr = match.group('ip_addr')
      worker = match.group('worker')
      effort = float(match.group('effort'))
      self.log("---------- Share Found ----------")
      self.log(f"  Timestamp        : {timestamp}")
      localtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      self.log(f"  Local Time       : {localtime}")
      self.log(f"  Worker name      : {worker}")
      self.log(f"  IP Address       : {ip_addr}")
      self.log(f"  Effort           : {effort}%")
      db = self.db()
      db.add_share_found(timestamp, worker, ip_addr, effort)
      sharesfoundcsv = SharesFoundCsv(self.log)
      sharesfoundcsv.new_shares_found_csv()
      sharesfoundbyhostcsv = SharesFoundByHostCsv(self.log)
      sharesfoundbyhostcsv.new_shares_found_by_host_csv()
      

  def is_share_position(self, log_line):
    """
    Sample log messages to watch for:

    Your shares position      = [.........................1....]
    Your shares               = 0 blocks (+0 uncles, 0 orphans)
    """
    if self._debug == 9:
      self.log("P2Pool.is_share_position()")
      self.log(f"  log_line: ({log_line})")
    pattern = r"Your shares position .* = (?P<position>\[.*\])"
    match = re.search(pattern, log_line)
    if match:
      position = match.group('position')
      self.log(f"---------- Position(s) {position}")
      localtime = datetime.now().strftime("%H:%M")
      db = self.db()
      db.add_share_position(localtime, position)
    pattern = r"Your shares .* = 0 .*"
    match = re.search(pattern, log_line)
    if match:
      position = '[..............................]'
      self.log(f"---------- Position(s) {position}")
      localtime = datetime.now().strftime("%H:%M")
      db = self.db()
      db.add_share_position(localtime, position)

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
      self.log(f"---------- ({localtime}) Side chain hashrate: {hashrate}")
      db = self.db()
      db.add_sidechain_hashrate(hashrate)

      # While we're at it, let's also collect the number of miners 
      # on the sidechain at this time.
      sidechain_miners = self.get_sidechain_miners()
      self.log(f"---------- ({localtime}) Side miners: {sidechain_miners}")
      db.add_sidechain_miners(sidechain_miners)


  def is_worker_stats(self, log_line):
    """
    Sample log message to watch for:
    
    2024-11-09 20:05:01.4647 StratumServer 192.168.0.27:57888         no     14h 59m 52s         23666               788 H/s        paris
    """
    # Look for a worker stat line
    pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} StratumServer (?P<ip_addr>\d+.\d+.\d+.\d+):\d+\s+no\s+\d+h \d+m \d+s\s+\d+\s+(?P<hashrate>\d+.*) (?P<unit>[H|K]).*/s\s+ (?P<worker_name>.*$)"
    match = re.search(pattern, log_line)
    if match:
      ip_addr = match.group('ip_addr')
      hashrate = float(match.group('hashrate'))
      unit = match.group('unit')
      if unit == 'K':
        # Convert KH/s into H/s
        hashrate = hashrate * 1000
        hashrate = int(hashrate)
      worker_name = match.group('worker_name')
      db = self.db()
      db.update_worker(worker_name, hashrate)

  def is_xmr_payment(self, log_line):
    """
    Sample log message to watch for:

    2024-11-09 19:52:19.1740 P2Pool Your wallet 48wY7nYBsQNSw7fDEG got a payout of 0.001080066485 XMR in block 3277801
    """
    pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} .* got a payout of (?P<payout>0.\d+) XMR"
    match = re.search(pattern, log_line)
    if match:
      timestamp = match.group('timestamp')
      timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
      payout = Decimal128(match.group('payout'))
      db = self.db()
      db.add_to_wallet(payout)
      wallet_balance = db.get_wallet_balance()
      self.log("---------- XMR Payment ----------")
      self.print_payout_banner()
      self.log(f"  Timestamp        : {timestamp}")
      localtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      self.log(f"  Local Time       : {localtime}")
      self.log(f"  Payout           : {payout} XMR")
      self.log(f"  Wallet Balance   : {wallet_balance} XMR")
      db = self.db()
      db.add_xmr_payment(timestamp, payout)
      p2poolcsv = P2PoolPaymentCsv(self.log)
      p2poolcsv.new_p2pool_payment_csv()

  def monitor_log(self):
    log_filename = self._p2pool_log
    if self._debug == 9:
      self.log("P2Pool.monitor_log()")
      self.log(f"  log_filename: {log_filename}")
    self.log(f"Monitoring log file ({log_filename})...")
    p2p_log = open(log_filename, 'r')
    self._loglines = self.watch_log(p2p_log)
    loglines = self.watch_log(p2p_log)
                                           
    try:
      for log_line in loglines:
        #while True:
        #log_line = self.get_next_logline()
        #print(log_line)

        if self._debug == 9:
          self.log("P2Pool.monitor_log()")
          self.log(f"  log line: {log_line[0:-1]}")

        self.is_worker_stats(log_line)
        self.is_share_found(log_line)
        self.is_share_position(log_line)
        self.is_block_found(log_line)
        self.is_xmr_payment(log_line)
        self.is_side_chain_hashrate(log_line)
        self.is_main_chain_hashrate(log_line)
        self.is_pool_hashrate(log_line)

    except KeyboardInterrupt:
      self.log("Exiting")
      sys.exit(0)

  def print_payout_banner(self):
    self.log("   ________       ______    ____      ____   _______    ____   ____   __________   ")
    self.log("  |    __  \\\    /      \\\ |   \\\    /   ||/       \\\  |   |\ |   \\\/          \\\ ")
    self.log("  |   || \  \\\  /   /\   \\\\\    \\\  /   ///   //\   \\\ |   || |   ||\___    ___// ")
    self.log("  |   ||_/   |||   ||_|   ||\    \\\/   //|   //  \   |||   || |   ||    |   ||      ")
    self.log("  |         // |          || \        // |   ||  |   |||   || |   ||    |   ||      ")
    self.log("  |   _____|/  |   ____   ||  \_     //  |   \\\  /   |||   || |   ||    |   ||      ")
    self.log("  |   ||       |   || |   ||   /    //    \   \\\/   // |   ||_|   ||    |   ||      ")
    self.log("  |___|/       |___|| | __|/  |____//      \_______//   \_________//    |___|/      ")
    self.log("")

  def stop_monitor_p2pool_log(self):
    pidfile= self._monitor_p2pool_pid_file
    with open(pidfile, encoding='utf-8') as pidfile_handle:
      pid = pidfile_handle.read()
      pidfile_handle.close()
      os.kill(int(pid), 15)

  def watch_log(self, p2p_log):
    p2p_log.seek(0, os.SEEK_END)

    while True:
      log_line = p2p_log.readline()
      if not log_line:
        time.sleep(1)
        continue

      yield log_line

