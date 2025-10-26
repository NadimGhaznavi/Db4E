"""
db4e/recs/monero/P2Pool.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0

Everything P2Pool
"""

from db4e.recs.monero.BaseP2Pool import BaseP2Pool


class P2Pool(BaseP2Pool):

    def __init__(self, rec=None):
        super().__init__()
        # Current pool hashrate
        self._hashrate = None
        # Historical pool hashrate data
        self._hashrates = None
        # Historical share found data
        self._shares_found = None

        if rec:
            self.from_rec(rec)

    # The current pool hashrate
    def hashrate(self, hashrate=None):
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate

    # Historical pool hashrate data
    def hashrates(self, hashrate_data=None):
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates

    # Historical share found data
    def shares_found(self, shares_found=None):
        if shares_found is not None:
            self._shares_found = shares_found
        return self._shares_found
