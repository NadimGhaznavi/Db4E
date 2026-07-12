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

from db4e.constants.DField import DField
from db4e.constants.DStatus import DStatus as STATUS
from db4e.constants.DHealth import DCategory as CATEGORY


class P2Pool(BaseP2Pool):
    """
    Record for a standard P2Pool instance.
    """

    def __init__(self, rec=None):
        """
        Initialize the P2Pool record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__()
        # Default to minisidechain
        self._chain = DField.MINI_CHAIN
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
        """
        Get or set the current pool hashrate.

        :param hashrate: Optional hashrate value to set.
        :type hashrate: int or None
        :return: Current hashrate value.
        :rtype: int or None
        """
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate

    # Historical pool hashrate data
    def hashrates(self, hashrate_data=None):
        """
        Get or set historical pool hashrate data.

        :param hashrate_data: Optional historical data to set.
        :type hashrate_data: list or dict or None
        :return: Historical hashrate data.
        :rtype: list or dict or None
        """
        if hashrate_data is not None:
            self._hashrates = hashrate_data
        return self._hashrates

    def is_running(self):
        if not self.enabled():
            return False

        for health_msg in self.pop_msgs():
            if health_msg.category == CATEGORY.STRATUM_PORT:
                if health_msg.status == STATUS.GOOD:
                    return True
                else:
                    return False

        return False
    
    # Historical share found data
    def shares_found(self, shares_found=None):
        """
        Get or set historical share found data.

        :param shares_found: Optional historical data to set.
        :type shares_found: list or dict or None
        :return: Historical share found data.
        :rtype: list or dict or None
        """
        if shares_found is not None:
            self._shares_found = shares_found
        return self._shares_found
