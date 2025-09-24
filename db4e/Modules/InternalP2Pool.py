"""
db4e/Modules/InternalP2Pool.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.Components import StatsMod
from db4e.Modules.Helper import get_component_value, set_component_value

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

class InternalP2Pool(P2Pool):
    """
    Internal P2Pool instance with reduCed peer counts and fixed port offsets
    for main, mini, and nano chains. Ensures multiple pools can run locally
    without port conflicts.
    """

    def __init__(self, rec=None):
        super().__init__()
        self._elem_type = DElem.INT_P2POOL
        self.name = DLabel.P2POOL_INTERNAL

        self.add_component(DField.STATS_MOD, StatsMod())
        self._stats_mod = self.components[DField.STATS_MOD]

        self.in_peers(2)
        self.out_peers(2)

        self._hashrates = None
        self._blocks_found = None


        if rec:
            self.from_rec(rec)

    def blocks_found(self, blocks_found=None):
        if blocks_found is not None:
            self._blocks_found = blocks_found
        return self._blocks_found



    def hashrates(self, hashrates=None):
        if hashrates is not None:
            self._hashrates = hashrates
        return self._hashrates


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


    def stats_mod(self, stats_mod=None):
        if stats_mod is not None:
            self._stats_mod = stats_mod
        return self._stats_mod
        

    def from_rec(self, rec):
        super().from_rec(rec)
        self.stats_mod(get_component_value(rec, DField.STATS_MOD))


    def to_rec(self):
        rec = super().to_rec()
        set_component_value(rec, { DField.STATS_MOD: self.stats_mod() })
        return rec
        

                       


