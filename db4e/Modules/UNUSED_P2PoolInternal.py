"""
db4e/Modules/P2PoolInternal.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

from db4e.Modules.P2Pool import P2Pool
from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DDef import DDef



P2P_PORT_OFFSET = 100
STRATUM_PORT_OFFSET = 40000

CHAIN_CONFIG = {
    DLabel.MAIN_CHAIN: (DField.MAIN_CHAIN, 0),
    DLabel.MINI_CHAIN: (DField.MINI_CHAIN, 1),
    DLabel.NANO_CHAIN: (DField.NANO_CHAIN, 2),
}

class P2PoolInternal(P2Pool):
    """
    Internal P2Pool instance with reduced peer counts and fixed port offsets
    for main, mini, and nano chains. Ensures multiple pools can run locally
    without port conflicts.
    """

    def __init__(self):
        super().__init__()
        self._elem_type = DElem.P2POOL_INTERNAL
        self.name = DLabel.INT_P2POOL
        self.in_peers(2)
        self.out_peers(2)

    def set_type(self, chain_label, log_file):

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

        
