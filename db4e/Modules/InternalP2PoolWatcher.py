"""
db4e/Modules/InternalP2PoolWatcher.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Everything P2Pool
"""
import os, threading, time

from db4e.Modules import P2PoolWatcher



class InternalP2PoolWatcher(P2PoolWatcher):


    def __init__(self):
        super().__init__()


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
                        #self.is_share_found(log_line)
                        #self.is_share_position(log_line)
                        self.is_block_found(log_line)
                        #self.is_xmr_payment(log_line)
                        self.is_side_chain_hashrate(log_line)
                        self.is_main_chain_hashrate(log_line)
                        #self.is_pool_hashrate(log_line)

            except FileNotFoundError:
                # File not created yet, retry later
                time.sleep(1)
            except Exception as e:
                print(f"P2PoolWatcher:monitor_log(): ERROR: {e}")
                time.sleep(1)    