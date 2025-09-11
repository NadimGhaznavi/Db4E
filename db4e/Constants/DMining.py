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
    """

    ACTIVE: str = DField.ACTIVE
    BLOCK_FOUND_EVENT: str = 'block_found_event'
    EFFORT: str = 'effort'
    HASHRATE: str = 'hashrate'
    INSTANCE: str = DField.INSTANCE
    IP_ADDR = DField.IP_ADDR
    MAINCHAIN_HASHRATE: str = 'mainchain_hashrate'
    MINER: str = 'miner'
    POOL_HASHRATE: str = 'pool_hashrate'
    RT_MAINCHAIN_HASHRATE: str = 'rt_mainchain_hashrate'
    RT_POOL_HASHRATE: str = 'rt_pool_hashrate'
    RT_SIDECHAIN_HASHRATE: str = 'rt_sidechain_hashrate'
    SHARE_FOUND_EVENT: str = 'share_found_event'
    SHARE_POSITION: str = 'share_position'
    SHARE_FOUND_EVENT: str = 'share_found_event'
    SHARE_POSITION: str = 'share_position'
    SIDECHAIN_HASHRATE: str = 'sidechain_hashrate'
    SIDECHAIN_MINERS: str = 'sidechain_miners'
    WALLET_BALANCE: str = 'wallet_balance'
    XMR_PAYMENT: str = 'xmr_payment'
