"""
Constants/Mining.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""
from db4e.Constants.Fields import DField
from enum import StrEnum

class Mining(StrEnum):
    """
    Mining related constants
    """

    ACTIVE = DField.ACTIVE.value
    BLOCK_FOUND_EVENT = 'block_found_event'
    EFFORT = 'effort'
    HASHRATE = 'hashrate'
    INSTANCE = DField.INSTANCE.value
    IP_ADDR = DField.IP_ADDR.value
    MAINCHAIN_HASHRATE = 'mainchain_hashrate'
    MINER = 'miner'
    POOL_HASHRATE = 'pool_hashrate'
    RT_MAINCHAIN_HASHRATE = 'rt_mainchain_hashrate'
    RT_POOL_HASHRATE = 'rt_pool_hashrate'
    RT_SIDECHAIN_HASHRATE = 'rt_sidechain_hashrate'
    SHARE_FOUND_EVENT = 'share_found_event'
    SHARE_POSITION = 'share_position'
    SHARE_FOUND_EVENT = 'share_found_event'
    SHARE_POSITION = 'share_position'
    SIDECHAIN_HASHRATE = 'sidechain_hashrate'
    SIDECHAIN_MINERS = 'sidechain_miners'
    WALLET_BALANCE = 'wallet_balance'
    XMR_PAYMENT = 'xmr_payment'
