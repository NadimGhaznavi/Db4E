"""
db4e/recs/monero/P2PoolInternal.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0

"""

from db4e.recs.monero.BaseP2Pool import BaseP2Pool
from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField
from db4e.constants.DDef import DDef


P2P_PORT_OFFSET = 100
STRATUM_PORT_OFFSET = 40000

CHAIN_CONFIG = {
    DLabel.MAIN_CHAIN: (DField.MAIN_CHAIN, 0),
    DLabel.MINI_CHAIN: (DField.MINI_CHAIN, 1),
    DLabel.NANO_CHAIN: (DField.NANO_CHAIN, 2),
}


class P2PoolInternal(BaseP2Pool):
    """
    Internal P2Pool instance with reduCed peer counts and fixed port offsets
    for main, mini, and nano chains. Ensures multiple pools can run locally
    without port conflicts.
    """

    def __init__(self, rec=None):
        super().__init__()
        self._stats_mod = None
        # Incoming and outgoing peer connection limits
        self.in_peers(2)
        self.out_peers(2)
        # There's no mining on this pool, but we need to set a wallet anyway.
        self.user_wallet(DDef.DONATION_WALLET)

        # Historical chain hashrate data
        self._hashrates = None
        # Historical chain blocks found data
        self._blocks_found = None

        if rec:
            self.from_rec(rec)

    def stats_mod(self, stats_mod=None):
        if stats_mod is not None:
            self._stats_mod = stats_mod
        return self._stats_mod

    def blocks_found(self, blocks_found=None):
        if blocks_found is not None:
            self._blocks_found = blocks_found
        return self._blocks_found

    def hashrates(self, hashrates=None):
        if hashrates is not None:
            self._hashrates = hashrates
        return self._hashrates

    # Helper function to configure the the three internal P2Pool instances
    def set_type(self, chain_label, log_file, stats_mod, stdin_path, config_file):

        try:
            chain_field, offset = CHAIN_CONFIG[chain_label]
        except KeyError:
            raise ValueError(f"Unknown P2Pool instance: {chain_label}")

        self.chain(chain_field)
        self.p2p_port(self.p2p_port() + P2P_PORT_OFFSET + offset)
        self.stratum_port(self.stratum_port() + STRATUM_PORT_OFFSET + offset)
        self.instance(chain_label)
        self.user_wallet(DDef.DONATION_WALLET)
        self.log_file(log_file)
        self.stdin_path(stdin_path)
        self.config_file(config_file)
        self.stats_mod(stats_mod)
