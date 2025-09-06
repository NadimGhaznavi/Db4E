"""
db4e/Modules/P2PoolWatcher.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything P2Pool
"""

from datetime import datetime
from decimal import Decimal
from bson.decimal128 import Decimal128
import threading
import time
import os
import re

from db4e.Modules.MiningDb import MiningDb
from db4e.Modules.DbMgr import DbMgr



class P2PoolWatcher:


    def __init__(self):
        self.mining_db = MiningDb()


    def is_block_found(self, log_line):
        """
        Sample log messages to watch for:

        2024-11-09 19:52:19.1734 P2Pool BLOCK FOUND: main chain block at height 3277801 was mined by someone else in this p2pool

        """
        print(f"is_block_found: {log_line}")
        pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} P2Pool BLOCK FOUND"
        match = re.search(pattern, log_line)
        if match:
            timestamp = match.group('timestamp')
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
            # Create a new blocks_found_event in the DB
            self.mining_db.add_block_found(timestamp)
            print(f"Block found: {timestamp}")


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
            self.mining_db.add_mainchain_hashrate(hashrate)
            print(f"Detected mainchain hashrate ({hashrate})")


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
            self.mining_db.add_pool_hashrate(hashrate)
            print(f"Detected pool hashrate ({hashrate})")


    def is_share_found(self, log_line):
        """
        Sample log messages to watch for:

        2024-11-10 00:47:47.5596 StratumServer SHARE FOUND: mainchain height 3277956, sidechain height 9143872, diff 126624856, client 192.168.0.86:37294, user sally, effort 91.663%
    
        """
        pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} StratumServer SHARE FOUND:.* sidechain height (?P<height>\d+).*client (?P<ip_addr>\d+.\d+.\d+.\d+):\d+, user (?P<worker>.*), effort (?P<effort>\d+.\d+)"
        match = re.search(pattern, log_line)
        if match:
            sidechain_height = int(match.group('height'))
            if sidechain_height > 1000000:
                timestamp = match.group('timestamp')
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
                ip_addr = match.group('ip_addr')
                worker = match.group('worker')
                effort = float(match.group('effort'))
                self.mining_db.add_share_found(timestamp, worker, ip_addr, effort)
                print('Share found event', { 'miner': worker }) 


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
            self.mining_db.add_share_position(timestamp, position)
            print(f'Detected share position ({position})')
        pattern = r"Your shares .* = 0 .*"
        match = re.search(pattern, log_line)
        if match:
            position = '[..............................]'
            timestamp = datetime.now()
            self.mining_db.add_share_position(timestamp, position)
            print(f'Detected share position ({position})')


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
            self.mining_db.add_sidechain_hashrate(hashrate)
            print(f'Detected sidechain hashrate ({hashrate})')

            # While we're at it, let's also collect the number of miners 
            # on the sidechain at this time.
            sidechain_miners = self.get_sidechain_miners()
            self.mining_db.add_sidechain_miners(sidechain_miners)
            print(f'Detected sidechain miners ({sidechain_miners})')


    def is_miner_stats(self, log_line):
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
            miner_name = match.group('worker_name')
            self.mining_db.update_miner(miner_name, hashrate)
            print(f'Detected miner ({miner_name}) hashrate ({hashrate} H/s)') 


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
            self.mining_db.add_xmr_payment(timestamp, payout)
            print(f"Payout event ({payout}) XMR", {'payout': {payout.to_decimal()}})


    def monitor_log(self, log_file: str, stop_event: threading.Event):

        while not stop_event.is_set():
            try:
                with open(log_file, "r") as log_handle:
                    log_handle.seek(0, os.SEEK_END)

                    while not stop_event.is_set():
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

                        # === your regex handlers ===
                        #self.is_miner_stats(log_line)
                        self.is_share_found(log_line)
                        #self.is_share_position(log_line)
                        self.is_block_found(log_line)
                        #self.is_xmr_payment(log_line)
                        #self.is_side_chain_hashrate(log_line)
                        #self.is_main_chain_hashrate(log_line)
                        #self.is_pool_hashrate(log_line)

            except FileNotFoundError:
                # File not created yet, retry later
                time.sleep(1)
            except Exception as e:
                print(f"P2PoolWatcher:monitor_log(): ERROR: {e}")
                time.sleep(1)