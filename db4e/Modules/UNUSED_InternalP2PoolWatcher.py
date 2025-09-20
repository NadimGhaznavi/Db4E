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
import time


from db4e.Modules.P2PoolWatcher import P2PoolWatcher
from db4e.Modules.MiningDb import MiningDb

from db4e.Constants.DField import DField
from db4e.Constants.DDebug import DDebug

DDebug.FUNCTION = False


class InternalP2PoolWatcher(P2PoolWatcher):


    def __init__(
            self, mining_db: MiningDb, chain: str, log_file: str,
            stop_event: threading.Event, stats_mod: str, stdin_path: str):
        super().__init__(mining_db=mining_db, chain=chain, log_file=log_file, 
                         stop_event=stop_event, stdin_path=stdin_path)
        self._stats_mod = stats_mod

        self.stop_event = None


    def get_handlers(self):
        handlers = [
            self.is_block_found,
        ]
        if self.chain == DField.MAIN_CHAIN:
            handlers.extend([ self.is_main_chain_hashrate ])
        else:
            handlers.extend([ self.is_side_chain_hashrate ])
        return handlers





