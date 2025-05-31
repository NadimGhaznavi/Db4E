""""
lib/Mining/P2pool/P2pool.py
"""

# Import supporting modules
import os, sys
import time
import re
from datetime import datetime
from bson.decimal128 import Decimal128
from decimal import Decimal

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
from Db4eLog.Db4eLog import Db4eLog
from MiningDb.MiningDb import MiningDb
from P2PoolPaymentCsv.P2PoolPaymentCsv import P2PoolPaymentCsv
from BlocksFoundCsv.BlocksFoundCsv import BlocksFoundCsv
from SharesFoundCsv.SharesFoundCsv import SharesFoundCsv
from SharesFoundByHostCsv.SharesFoundByHostCsv import SharesFoundByHostCsv

class P2Pool():

  def __init__(self):
    config = Db4eConfig()
    install_dir = config.config['p2pool']['install_dir']
    log_dir = config.config['p2pool']['log_dir']
    log_file = config.config['p2pool']['log_file']
    self._p2pool_log = os.path.join(install_dir, log_dir, log_file)
    self._debug = config.config['db4e']['debug']
    logger = Db4eLog()
    # Assign the logger's log_msg method to self.log_msg
    self.log_msg = logger.log_msg
    self._db = MiningDb()
    
  def db(self):
    return self._db
  
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
      self.log_msg("---------- Block Found ----------")
      self.log_msg(f"  Timestamp        : {timestamp}")
      localtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      self.log_msg(f"  Local Time       : {localtime}")
      db = self.db()
      db.add_block_found(timestamp)
      blocksfoundcsv = BlocksFoundCsv(self.log_msg)
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
      self.log_msg(f"---------- ({localtime}) Main chain hashrate: {hashrate}")
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
      self.log_msg(f"---------- ({localtime}) Pool hashrate: {hashrate}")
      db = self.db()
      db.add_pool_hashrate(hashrate)

  def is_share_found(self, log_line):
    """
    Sample log messages to watch for:

    2024-11-10 00:47:47.5596 StratumServer SHARE FOUND: mainchain height 3277956, sidechain height 9143872, diff 126624856, client 192.168.0.86:37294, user sally, effort 91.663%
    """
    if self._debug == 9:
      self.log_msg("P2Pool.is_share_found()")
      self.log_msg(f"  log_line: ({log_line})")
    pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} StratumServer SHARE FOUND:.*client (?P<ip_addr>\d+.\d+.\d+.\d+):\d+, user (?P<worker>.*), effort (?P<effort>\d+.\d+)"
    match = re.search(pattern, log_line)
    if match:
      timestamp = match.group('timestamp')
      timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
      ip_addr = match.group('ip_addr')
      worker = match.group('worker')
      effort = float(match.group('effort'))
      self.log_msg("---------- Share Found ----------")
      self.log_msg(f"  Timestamp        : {timestamp}")
      localtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      self.log_msg(f"  Local Time       : {localtime}")
      self.log_msg(f"  Worker name      : {worker}")
      self.log_msg(f"  IP Address       : {ip_addr}")
      self.log_msg(f"  Effort           : {effort}%")
      db = self.db()
      db.add_share_found(timestamp, worker, ip_addr, effort)
      sharesfoundcsv = SharesFoundCsv(self.log_msg)
      sharesfoundcsv.new_shares_found_csv()
      sharesfoundbyhostcsv = SharesFoundByHostCsv(self.log_msg)
      sharesfoundbyhostcsv.new_shares_found_by_host_csv()
      

  def is_share_position(self, log_line):
    """
    Sample log messages to watch for:

    Your shares position      = [.........................1....]
    Your shares               = 0 blocks (+0 uncles, 0 orphans)
    """
    if self._debug == 9:
      self.log_msg("P2Pool.is_share_position()")
      self.log_msg(f"  log_line: ({log_line})")
    pattern = r"Your shares position .* = (?P<position>\[.*\])"
    match = re.search(pattern, log_line)
    if match:
      position = match.group('position')
      self.log_msg(f"---------- Position(s) {position}")
      localtime = datetime.now().strftime("%H:%M")
      db = self.db()
      db.add_share_position(localtime, position)
    pattern = r"Your shares .* = 0 .*"
    match = re.search(pattern, log_line)
    if match:
      position = '[..............................]'
      self.log_msg(f"---------- Position(s) {position}")
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
      self.log_msg(f"---------- ({localtime}) Side chain hashrate: {hashrate}")
      db = self.db()
      db.add_sidechain_hashrate(hashrate)

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
      self.log_msg("---------- XMR Payment ----------")
      self.print_payout_banner()
      self.log_msg(f"  Timestamp        : {timestamp}")
      localtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      self.log_msg(f"  Local Time       : {localtime}")
      self.log_msg(f"  Payout           : {payout} XMR")
      self.log_msg(f"  Wallet Balance   : {wallet_balance} XMR")
      db = self.db()
      db.add_xmr_payment(timestamp, payout)
      p2poolcsv = P2PoolPaymentCsv(self.log_msg)
      p2poolcsv.new_p2pool_payment_csv()

  def monitor_log(self):
    log_filename = self._p2pool_log
    if self._debug == 9:
      self.log_msg("P2Pool.monitor_log()")
      self.log_msg(f"  log_filename: {log_filename}")
    self.log_msg(f"Monitoring log file ({log_filename})...")
    p2p_log = open(log_filename, 'r')
    self._loglines = self.watch_log(p2p_log)
    loglines = self.watch_log(p2p_log)
                                           
    try:
      for log_line in loglines:
        #while True:
        #log_line = self.get_next_logline()

        if self._debug == 9:
          self.log_msg("P2Pool.monitor_log()")
          self.log_msg(f"  log line: {log_line[0:-1]}")

        self.is_worker_stats(log_line)
        self.is_share_found(log_line)
        self.is_share_position(log_line)
        self.is_block_found(log_line)
        self.is_xmr_payment(log_line)
        self.is_side_chain_hashrate(log_line)
        self.is_main_chain_hashrate(log_line)
        self.is_pool_hashrate(log_line)

    except KeyboardInterrupt:
      self.log_msg("Exiting")
      sys.exit(0)

  def print_payout_banner(self):
    self.log_msg("   ________       ______    ____      ____   _______    ____   ____   __________   ")
    self.log_msg("  |    __  \\\    /      \\\ |   \\\    /   ||/       \\\  |   |\ |   \\\/          \\\ ")
    self.log_msg("  |   || \  \\\  /   /\   \\\\\    \\\  /   ///   //\   \\\ |   || |   ||\___    ___// ")
    self.log_msg("  |   ||_/   |||   ||_|   ||\    \\\/   //|   //  \   |||   || |   ||    |   ||      ")
    self.log_msg("  |         // |          || \        // |   ||  |   |||   || |   ||    |   ||      ")
    self.log_msg("  |   _____|/  |   ____   ||  \_     //  |   \\\  /   |||   || |   ||    |   ||      ")
    self.log_msg("  |   ||       |   || |   ||   /    //    \   \\\/   // |   ||_|   ||    |   ||      ")
    self.log_msg("  |___|/       |___|| | __|/  |____//      \_______//   \_________//    |___|/      ")
    self.log_msg("")

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

