"""
db4e/Modules/InternalP2PoolWatcher.py

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
import json
import os
import re


from db4e.Modules.P2PoolWatcher import P2PoolWatcher
from db4e.Modules.MiningDb import MiningDb

from db4e.Constants.DField import DField
from db4e.Constants.DDebug import DDebug

DDebug.FUNCTION = False


class InternalP2PoolWatcher(P2PoolWatcher):


    def __init__(
            self, mining_db: MiningDb, chain: str, log_file: str,
            stop_event: threading.Event, stats_mod: str):
        super().__init__(mining_db=mining_db, chain=chain, log_file=log_file, 
                         stop_event=stop_event)
        self.mining_db = mining_db
        self._chain = chain
        self._log_file = log_file
        self._stats_mod = stats_mod
        self._stop_event = stop_event
        self._stats_mod = stats_mod

        self.running = threading.Event()
        self.running.set()


    def spawn_status_cmd(self):
        if DDebug.FUNCTION:
            print(f"InternalP2PoolWatcher:spawn_status_cmd()")

        stop_event = threading.Event()

        def _runner():
            try:
                now = datetime.now(timezone.utc)
                cur_minute = now.minute
                if cur_minute % 5 == 0:
                    pass
            except:
                pass



    def get_handlers(self):
        handlers = [
            self.is_block_found,
        ]
        if self.chain == DField.MAIN_CHAIN:
            handlers.extend([ self.is_main_chain_hashrate ])
        else:
            handlers.extend([ self.is_side_chain_hashrate ])
        return handlers


    def get_num_miners(self):
        if DDebug.FUNCTION:
            print(f"InternalP2PoolWatcher:get_sidechain_miners()")
        """
        Sample API stats_mod contents (one line...):

        {"config":{"ports":[{"port":3333,"tls":false}],
        "fee":0,"minPaymentThreshold":300000000},"network":
        {"height":3502949},"pool":{"stats":{"lastBlockFound":"0000"},
        "blocks":["0000...0000:0","0"],
        "miners":306,"hashrate":2335864,"roundHashes":19272205524784}}
        """
        stats_mod = self.stats_mod()
        if not os.path.exists(stats_mod):
            raise ValueError(f"InternalP2PoolWatcher:get_sidechain_miners(): API file ({stats_mod}) not found")
        with open(stats_mod, 'r') as file:
            api_string_data = file.read()
            api_data = json.loads(api_string_data)
            return api_data[DField.POOL][DField.MINERS]
            
      
    def is_block_found(self, log_line):
        """
        Sample log messages to watch for:

        2024-11-09 19:52:19.1734 P2Pool BLOCK FOUND: main chain block at height 3277801 was mined by someone else in this p2pool

        """
        if DDebug.FUNCTION:
            print(f"InternalP2PoolWatcher:is_block_found()")
        pattern = r".*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}):\d{2}.\d{4} P2Pool BLOCK FOUND"
        match = re.search(pattern, log_line)
        if match:
            timestamp = match.group('timestamp')
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
            # Create a new blocks_found_event in the DB
            self.mining_db.add_block_found(timestamp=timestamp, chain=self.chain())
            print(f"Block found: {timestamp}")


    def is_main_chain_hashrate(self, log_line):
        """
        Sample log message to watch for:

        Main chain hashrate       = 3.105 GH/s
        Main chain hashrate       = 5.079 GH/s
        """
        if DDebug.FUNCTION:
            print(f"InternalP2PoolWatcher:is_main_chain_hashrate()")
        pattern = r"Main chain hashrate .* = (?P<hashrate>.*H/s)"
        match = re.search(pattern, log_line)
        localtime = datetime.now().strftime("%H:%M")
        if match:
            hashrate = match.group('hashrate')
            self.mining_db.add_chain_hashrate(chain=self.chain(), hashrate=hashrate)

            # While we're at it, let's also collect the number of miners on the chain
            num_miners = self.get_num_miners()
            self.mining_db.add_chain_miners(chain=self.chain(), num_miners=num_miners)


    def is_side_chain_hashrate(self, log_line):
        """
        Sample log message to watch for:

        Side chain hashrate       = 12.291 MH/s
        """
        if DDebug.FUNCTION:
            print(f"InternalP2PoolWatcher:is_side_chain_hashrate()")
        pattern = r"Side chain hashrate .* = (?P<hashrate>.*H/s)"
        match = re.search(pattern, log_line)
        localtime = datetime.now().strftime("%H:%M")
        if match:
            hashrate = match.group('hashrate')
            self.mining_db.add_chain_hashrate(chain=self.chain(), hashrate=hashrate)

            # While we're at it, let's also collect the number of miners on the chain
            num_miners = self.get_num_miners()
            self.mining_db.add_chain_miners(chain=self.chain(), num_miners=num_miners)

    def stats_mod(self, stats_mod=None):
        if stats_mod is not None:
            self._stats_mod = stats_mod
        return self._stats_mod
