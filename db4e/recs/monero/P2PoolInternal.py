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
        """
        Initialize the internal P2Pool record and optionally hydrate from a DB record.

        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__()
        self._stats_mod = None
        # Incoming and outgoing peer connection limits
        self.in_peers(2)
        self.out_peers(2)
        # There's no mining on this pool, but we need to set a wallet anyway.
        self.user_wallet(DDef.DONATION_WALLET)
        # Start with the default P2P_PORT number (this is changed in set_type())
        self.p2p_port(DDef.P2P_PORT)
        # Start with the default STRATUM_PORT number (this is changed in set_type())
        self.stratum_port(DDef.STRATUM_PORT)
        # Set the listening IP address
        self.any_ip(DDef.ANY_IP)

        # Historical chain hashrate data
        self._hashrates = None
        # Historical chain blocks found data
        self._blocks_found = None

        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        """
        Populate the object from a database record.

        :param rec: Database record mapping.
        :type rec: dict
        :return: None
        :rtype: None
        """
        super().from_rec(rec)
        self._stats_mod = rec[DField.STATS_MOD]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with internal P2Pool fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update({DField.STATS_MOD: self._stats_mod})
        return data

    def stats_mod(self, stats_mod=None):
        """
        Get or set the stats module identifier.

        :param stats_mod: Optional stats module value to set.
        :type stats_mod: str or int or None
        :return: Current stats module value.
        :rtype: str or int or None
        """
        if stats_mod is not None:
            self._stats_mod = stats_mod
        return self._stats_mod

    def blocks_found(self, blocks_found=None):
        """
        Get or set historical blocks found data.

        :param blocks_found: Optional historical data to set.
        :type blocks_found: list or dict or None
        :return: Historical blocks found data.
        :rtype: list or dict or None
        """
        if blocks_found is not None:
            self._blocks_found = blocks_found
        return self._blocks_found

    def hashrates(self, hashrates=None):
        """
        Get or set historical chain hashrate data.

        :param hashrates: Optional historical data to set.
        :type hashrates: list or dict or None
        :return: Historical chain hashrate data.
        :rtype: list or dict or None
        """
        if hashrates is not None:
            self._hashrates = hashrates
        return self._hashrates

    # Helper function to configure the the three internal P2Pool instances
    def set_type(self, chain_label, log_file, stats_mod, stdin_path, config_file):
        """
        Configure this internal instance for a specific chain label.

        :param chain_label: Chain label key.
        :type chain_label: str
        :param log_file: Log file path.
        :type log_file: str
        :param stats_mod: Stats module identifier.
        :type stats_mod: str or int
        :param stdin_path: Stdin pipe path.
        :type stdin_path: str
        :param config_file: Config file path.
        :type config_file: str
        :return: None
        :rtype: None
        """

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
