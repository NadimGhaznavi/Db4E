# Constants/DMining.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0
#


from typing import Final
from db4e.constants.DField import DField


class DMining:
    """
    Mining related constants

    CAUTION: Modifying these will change the effective DB Schema
    """

    ACTIVE: Final[str] = "active"
    BLOCK_FOUND_EVENT: Final[str] = "block_found_event"
    EFFORT: Final[str] = "effort"
    HASHRATE: Final[str] = "hashrate"
    POOL_HASHRATE: Final[str] = "pool_hashrate"
    MINER_HASHRATE: Final[str] = "miner_hashrate"
    INSTANCE: Final[str] = "instance"
    IP_ADDR = DField.IP_ADDR
    MAIN_CHAIN = DField.MAIN_CHAIN
    MINER: Final[str] = "miner"
    MINI_CHAIN = DField.MINI_CHAIN
    NANO_CHAIN = DField.NANO_CHAIN
    RT_HASHRATE: Final[str] = "rt_hashrate"
    RT_MINER_HASHRATE: Final[str] = "rt_miner_hashrate"
    RT_POOL_HASHRATE: Final[str] = "rt_pool_hashrate"
    SHARE_FOUND_EVENT: Final[str] = "share_found_event"
    SHARE_POSITION: Final[str] = "share_position"
    MINERS: Final[str] = "miners"
    UNIT: Final[str] = "unit"
    WALLET_BALANCE: Final[str] = "wallet_balance"
    XMR_PAYMENT: Final[str] = "xmr_payment"
