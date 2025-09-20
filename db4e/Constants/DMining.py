"""
Constants/DMining.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""
from db4e.Modules.ConstGroup import ConstGroup
from db4e.Constants.DField import DField

class DMining(ConstGroup):
    """
    Mining related constants

    CAUTION: Modifying these will change the effective DB Schema
    """

    ACTIVE: str = "active"
    BLOCK_FOUND_EVENT: str = "block_found_event"
    EFFORT: str = "effort"
    HASHRATE: str = "hashrate"
    POOL_HASHRATE: str = "pool_hashrate"
    MINER_HASHRATE: str = "miner_hashrate"
    INSTANCE: str = "instance"
    IP_ADDR = DField.IP_ADDR
    MINER: str = "miner"
    RT_HASHRATE: str = "rt_hashrate"
    RT_POOL_HASHRATE: str = "rt_pool_hashrate"
    RT_MINER_HASHRATE: str = "rt_miner_hashrate"
    SHARE_FOUND_EVENT: str = "share_found_event"
    SHARE_POSITION: str = "share_position"
    MINERS: str = "miners"
    WALLET_BALANCE: str = "wallet_balance"
    XMR_PAYMENT: str = "xmr_payment"
