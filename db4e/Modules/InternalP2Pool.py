"""
db4e/Modules/InternalP2Pool.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

from db4e.Modules.P2Pool import P2Pool
from db4e.Constants.Fields import (
    MAIN_CHAIN_FIELD, MINI_CHAIN_FIELD, NANO_CHAIN_FIELD)
from db4e.Constants.Fields import DElem
from db4e.Constants.Labels import DLabel

P2P_PORT_OFFSET = 100
STRATUM_PORT_OFFSET = 40000

CHAIN_CONFIG = {
    DLabel.MAIN_CHAIN: (MINI_CHAIN_FIELD, 0),
    DLabel.MINI_CHAIN: (MINI_CHAIN_FIELD, 1),
    DLabel.NANO_CHAIN: (NANO_CHAIN_FIELD, 2),
}

class InternalP2Pool(P2Pool):
    """
    Internal P2Pool instance with reduCed peer counts and fixed port offsets
    for main, mini, and nano chains. Ensures multiple pools can run locally
    without port conflicts.
    """

    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = DElem.INT_P2POOL

        self.in_peers(2)
        self.out_peers(2)


    def set_type(self, chain_label):

        try:
            chain_field, offset = CHAIN_CONFIG[chain_label]
        except KeyError:
            raise ValueError(f"Unknown P2Pool instance: {chain_label}")

        self.chain(chain_field)
        self.p2p_bind_port(self.p2p_bind_port() + P2P_PORT_OFFSET + offset)
        self.stratum_port(self.stratum_port() + STRATUM_PORT_OFFSET + offset)
