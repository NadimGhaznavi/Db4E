"""
db4e/Modules/P2PoolWatcher.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything P2Pool
"""

from datetime import datetime, timezone
from decimal import Decimal
from bson.decimal128 import Decimal128
import threading
import time
import os
import re
import errno
import json


from db4e.Modules.MiningDb import MiningDb
from db4e.Modules.Db4ELogger import Db4ELogger
from db4e.Modules.DeplMgr import DeplMgr

from db4e.Constants.DField import DField
from db4e.Constants.DDebug import DDebug
from db4e.Constants.DModule import DModule
from db4e.Constants.DMongo import DMongo
from db4e.Constants.DElem import DElem
from db4e.Constants.DSystemD import DSystemD
from db4e.Constants.DDef import DDef



DDebug.FUNCTION = True

class P2PoolWatcher:


    def __init__(
            self, mining_db: MiningDb, chain: str, log_file: str, 
            stop_event: threading.Event, stdin_path: str, instance: str, 
            depl_mgr: DeplMgr, db4e_log_file: str, stats_mod=None):
        self.mining_db = mining_db
        self.depl_mgr = depl_mgr
        self.ops_col = DDef.OPS_COL
        self._chain = chain
        self._stop_event = stop_event
        self._stdin_path = stdin_path
        self._instance = instance
        self.thread_control = None
        self._stats_mod = stats_mod
        self._log_file = log_file


        # If stats_mod was passed in, then this watcher is watching an InternalP2Pool
        if stats_mod:
            logger_id = DModule.P2POOL_WATCHER + "-" + chain
        
        else:
            logger_id = DModule.P2POOL_WATCHER + "-" + instance + "-" + chain
            # Create an Ops record when a P2PoolWatcher is created for a user defined P2Pool   

        self.log = Db4ELogger(db4e_module=logger_id, log_file=db4e_log_file)

    def chain(self):
        return self._chain
    

    def get_handlers(self):

        if self.stats_mod():
            # This is only used when the P2PoolWatcher is watching an internal P2Pool
            handlers = [
                self.is_block_found,
            ]
            if self.chain == DField.MAIN_CHAIN:
                handlers.extend([ self.is_main_chain_hashrate ])
            else:
                handlers.extend([ self.is_side_chain_hashrate ])            

        else:
            # User defined P2Pool, where they mine
            handlers = [
                self.is_pool_hashrate,
                self.is_share_found,
                self.is_share_position,
                self.is_miner_stats,
                self.is_xmr_payment,
            ]
        return handlers


    def get_num_miners(self):
        """
        Sample API stats_mod contents (one line...):

        {"config":{"ports":[{"port":3333,"tls":false}],
        "fee":0,"minPaymentThreshold":300000000},"network":
        {"height":3502949},"pool":{"stats":{"lastBlockFound":"0000"},
        "blocks":["0000...0000:0","0"],
        "miners":306,"hashrate":2335864,"roundHashes":19272205524784}}
        """
        try:
            stats_mod = self.stats_mod()
            if not os.path.exists(stats_mod):
                raise ValueError(f"P2PoolWatcher:get_sidechain_miners(): API file ({stats_mod}) not found")
            with open(stats_mod, 'r') as file:
                api_string_data = file.read()
                api_data = json.loads(api_string_data)
                return api_data[DField.POOL][DField.MINERS]
        except Exception as e:
            self.log.critical(f"P2PoolWatcher:get_sidechain_miners(): ERROR: {e}")
            

    def instance(self, instance=None):
        if instance is not None:
            self._instance = instance
        return self._instance

      
    def is_block_found(self, log_line):
        """
        Sample log messages to watch for:

        2024-11-09 19:52:19.1734 P2Pool BLOCK FOUND: main chain block at height 3277801 was mined by someone else in this p2pool

        """
        try:
            pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} P2Pool BLOCK FOUND"
            match = re.search(pattern, log_line)
            if match:
                timestamp = match.group('timestamp')
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                # Create a new blocks_found_event in the DB
                self.mining_db.add_block_found(timestamp=timestamp, chain=self.chain(), instance=self.instance())
        except Exception as e:
            self.log.critical(f"P2PoolWatcher:is_block_found(): ERROR: {e}")


    def is_main_chain_hashrate(self, log_line):
        """
        Sample log message to watch for:

        Main chain hashrate       = 3.105 GH/s
        Main chain hashrate       = 5.079 GH/s
        """
        try:
            pattern = r"Main chain hashrate\s*=\s*(?P<hashrate>[\d.]+)\s*(?P<unit>[KMGT]?H/s)"
            match = re.search(pattern, log_line)

            if match:
                hashrate = match.group('hashrate')
                unit = match.group('unit')

                self.mining_db.add_chain_hashrate(
                    chain=self.chain(), instance=self.instance(), hashrate=hashrate, unit=unit)

                # While we're at it, let's also collect the number of miners on the chain
                num_miners = self.get_num_miners()
                self.mining_db.add_chain_miners(chain=self.chain(), num_miners=num_miners)
        except Exception as e:
            self.log.critical(f"P2PoolWatcher:is_main_chain_hashrate(): ERROR: {e}")


    def is_miner_stats(self, log_line):
        """
        Sample log message to watch for:
        2025-09-21 10:33:36.2717 StratumServer 192.168.0.176:40816        no     0h 6m 21s           125002              4.166 kH/s     kermit
        2024-11-09 20:05:01.4647 StratumServer 192.168.0.27:57888         no     14h 59m 52s         23666               788 H/s        paris
        2025-09-21 10:33:36.2717 StratumServer 192.168.0.122:54958        no     1d 7h 28m 31s       49595               1.653 kH/s     islands
        """
        # Look for a worker stat line
        try:
            pattern = (
                r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s+"
                r"StratumServer\s+(?P<ip_addr>\d+\.\d+\.\d+\.\d+):\d+\s+"
                r"no\s+"
                r"(?P<uptime>(?:\d+d\s+)?\d+h \d+m \d+s)\s+"
                r"\d+\s+"
                r"(?P<hashrate_value>\d+(?:\.\d+)?)\s*"
                r"(?P<unit>(?:k|M)?H/s)\s+"
                r"(?P<miner_name>\S+)$"
            )

            match = re.search(pattern, log_line, flags=re.IGNORECASE)
            if match:
                hashrate = float(match.group("hashrate_value"))
                unit = match.group("unit").lower()  # normalize case

                if unit == "kh/s":
                    hashrate *= 1_000
                elif unit == "mh/s":
                    hashrate *= 1_000_000
                # "h/s" stays as-is

                hashrate = int(hashrate)
                miner_name = match.group('miner_name')
                ip_addr = match.group('ip_addr')
                uptime = match.group('uptime')
                timestamp = match.group('timestamp')

                self.mining_db.add_miner_hashrate(
                    chain=self.chain(), miner_name=miner_name, ip_addr=ip_addr, 
                    hashrate=hashrate, uptime=uptime, timestamp=timestamp, 
                    p2pool_instance=self.instance())
                
                self.depl_mgr.add_remote_xmrig_deployment(
                    miner_name=miner_name, ip_addr=ip_addr, hashrate=hashrate, uptime=uptime,
                    timestamp=timestamp)
        except Exception as e:
            self.log.critical(f"P2PoolWatcher:is_miner_stats(): ERROR: {e}")

    def is_side_chain_hashrate(self, log_line):
        """
        Sample log message to watch for:

        Side chain hashrate       = 12.291 MH/s
        """
        try:
            pattern = r"Side chain hashrate\s*=\s*(?P<hashrate>[\d.]+)\s*(?P<unit>[KMGT]?H/s)"
            match = re.search(pattern, log_line)
            if match:
                hashrate = match.group('hashrate')
                unit = match.group('unit')

                self.mining_db.add_chain_hashrate(
                    chain=self.chain(), instance=self.instance(), hashrate=hashrate, unit=unit)

                # While we're at it, let's also collect the number of miners on the chain
                num_miners = self.get_num_miners()
                self.mining_db.add_chain_miners(chain=self.chain(), num_miners=num_miners)
        except Exception as e:
            self.log.critical(f"P2PoolWatcher:is_side_chain_hashrate(): ERROR: {e}")


    def is_pool_hashrate(self, log_line):
        """
        Sample log message to watch for:

        Hashrate (1h  est)   = 5.515 kH/s
        """
        try:
            pattern = r"Hashrate\s*\(1h\s*est\)\s*=\s*(?P<hashrate>[\d.]+)\s*(?P<unit>[kKMmGgTt]?H/s)"
            match = re.search(pattern, log_line)
            if match:
                hashrate = match.group('hashrate')
                unit = match.group('unit')
                self.mining_db.add_pool_hashrate(
                    chain=self.chain(), instance=self.instance(), hashrate=hashrate, unit=unit)
        except Exception as e:
            self.log.critical(f"P2PoolWatcher:is_pool_hashrate(): ERROR: {e}")


    def is_share_found(self, log_line):
        """
        Sample log messages to watch for:

        2024-11-10 00:47:47.5596 StratumServer SHARE FOUND: mainchain height 3277956, sidechain height 9143872, diff 126624856, client 192.168.0.86:37294, user sally, effort 91.663%
    
        """
        try:
            pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} StratumServer SHARE FOUND:.* sidechain height (?P<height>\d+).*client (?P<ip_addr>\d+.\d+.\d+.\d+):\d+, user (?P<miner>.*), effort (?P<effort>\d+.\d+)"
            match = re.search(pattern, log_line)
            if match:
                sidechain_height = int(match.group('height'))
                if sidechain_height > 1000000:
                    timestamp = match.group('timestamp')
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                    ip_addr = match.group('ip_addr')
                    miner = match.group('miner')
                    effort = float(match.group('effort'))
                    self.mining_db.add_share_found(
                        chain=self.chain(), timestamp=timestamp, miner=miner, 
                        ip_addr=ip_addr, effort=effort)
        except Exception as e:
            self.log.critical(f"P2PoolWatcher:is_share_found(): ERROR: {e}")


    def is_share_position(self, log_line):
        """
        Sample log messages to watch for:

        Your shares position      = [.........................1....]
        Your shares               = 0 blocks (+0 uncles, 0 orphans)
        """
        try:
            pattern = r"Your shares position .* = (?P<position>\[.*\])"
            match = re.search(pattern, log_line)
            if match:
                position = match.group('position')
                timestamp = datetime.now()
                self.mining_db.add_share_position(
                    chain=self.chain(), timestamp=timestamp, position=position)
            pattern = r"Your shares .* = 0 .*"
            match = re.search(pattern, log_line)
            if match:
                position = '[..............................]'
                timestamp = datetime.now()
                self.mining_db.add_share_position(
                    chain=self.chain(), timestamp=timestamp, position=position)
        except Exception as e:
            self.log.critical(f"P2PoolWatcher:is_share_position(): ERROR: {e}")


    def is_xmr_payment(self, log_line):
        """
        Sample log message to watch for:

        2024-11-09 19:52:19.1740 P2Pool Your wallet 48wY7nYBsQNSw7fDEG got a payout of 0.001080066485 XMR in block 3277801
        2025-06-02 21:42:53.0727 P2Pool Your wallet 48wdY6fDEG got a payout of 0.000295115076 XMR in block 3425427
        """
        try:
            pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} .*got a payout of (?P<payment>0.\d+) XMR"
            match = re.search(pattern, log_line)
            if match:
                timestamp = match.group('timestamp')
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                payment = Decimal128(match.group('payment'))
                self.mining_db.add_xmr_payment(
                    chain=self.chain(), timestamp=timestamp, payment=payment)
        except Exception as e:
            self.log.critical(f"P2PoolWatcher:is_xmr_payment(): ERROR: {e}")



    def log_file(self):
        return self._log_file
    

    def monitor_log(self):

        self.spawn_p2pool_cmds()
        log_file = self.log_file()

        self.log.info(f"Monitoring log file: {log_file}")
        while not self._stop_event.is_set():
            try:
                with open(log_file, "r") as log_handle:
                    log_handle.seek(0, os.SEEK_END)

                    while not self._stop_event.is_set():
                        line = log_handle.readline()

                        if not line:
                            # Handle log rotation/truncation
                            try:
                                if os.stat(log_file).st_size < log_handle.tell():
                                    break  # reopen the file
                            except FileNotFoundError:
                                break  # file got rotated away
                            time.sleep(0.2)
                            continue

                        log_line = line.strip()

                        for handler in self.get_handlers():
                            handler(log_line)

            except FileNotFoundError:
                # File not created yet, retry later
                time.sleep(1)
            except Exception as e:
                print(f"{self.__class__.__name__}:monitor_log(): ERROR: {e}")
                time.sleep(1)


    def send_cmd(self, cmd: str):
        if not cmd.endswith("\n"):
            cmd += "\n"
        encoded_cmd = cmd.encode("utf-8")  # encode explicitly for non-blocking write

        try:
            # Make sure the socket has been setup 
            stdin_path = self.stdin_path()
            if not os.path.exists(stdin_path):
                self.log.critical(f"P2PoolWatcher: send_cmd(): Missing STDIN: {stdin_path}")
                return
            fd = os.open(stdin_path, os.O_WRONLY | os.O_NONBLOCK)
        except OSError as e:
            if e.errno == errno.ENXIO:
                # No reader yet
                return
            else:
                raise

        try:
            os.write(fd, encoded_cmd)
        finally:
            os.close(fd)


    def send_status(self):
        self.log.debug("Sending status command")
        self.send_cmd(DField.STATUS)


    def send_workers(self):
        self.log.debug("Sending workers command")
        self.send_cmd(DField.WORKERS)


    def stats_mod(self, stats_mod=None):
        if stats_mod is not None:
            self._stats_mod = stats_mod
        return self._stats_mod


    def stdin_path(self, stdin_path=None) -> str:
        if stdin_path is not None:
            self._stdin_path = stdin_path
        return self._stdin_path


    def spawn_p2pool_cmds(self):
        self.log.debug("Starting spawn commands sub-thread")

        stop_event = threading.Event()

        def _runner():
            while not stop_event.is_set():
                try:
                    now = datetime.now(timezone.utc)
                    cur_minute = now.minute
                    if cur_minute == 0 or cur_minute % 5 == 0:
                        self.send_status()
                    self.send_workers()
                    for _ in range(60):
                        if stop_event.is_set():
                            return
                        time.sleep(1)
                finally:
                    pass

        t = threading.Thread(target=_runner, name=f"Logwatcher-{self.chain()}", daemon=True)
        self.thread_control = (t, stop_event)
        t.start()


    def stop_sub_thread(self):
        if not self.thread_control:
            return
        t, stop_event = self.thread_control
        stop_event.set()   # signal the thread to exit
        t.join(timeout=2)
        self.thread_control = None


