# db4e/Constants/DHealth.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0


from typing import Final
from db4e.constants.DField import DField
from db4e.constants.DLabel import DLabel


class DCategory:
    BLOCKCHAIN_DIR = DField.BLOCKCHAIN_DIR
    BLOCKCHAIN_SIZE_GB = DField.BLOCKCHAIN_SIZE_GB
    ENABLED = DField.ENABLED
    PRIMARY_SERVER = DField.PRIMARY_SERVER
    RPC_BIND_PORT = DField.RPC_BIND_PORT
    STRATUM_PORT = DField.STRATUM_PORT
    UPSTREAM = DField.UPSTREAM
    VENDOR_DIR = DField.VENDOR_DIR
    ZMQ_PUB_PORT = DField.ZMQ_PUB_PORT


CATEGORY_LABEL_MAP = {
    DField.BLOCKCHAIN_DIR: DLabel.BLOCKCHAIN_DIR,
    DField.ENABLED: DLabel.ENABLED,
    DField.PRIMARY_SERVER: DLabel.PRIMARY_SERVER,
    DField.RPC_BIND_PORT: DLabel.RPC_BIND_PORT,
    DField.STRATUM_PORT: DLabel.STRATUM_PORT,
    DField.UPSTREAM: DLabel.UPSTREAM,
    DField.VENDOR_DIR: DLabel.VENDOR_DIR,
    DField.ZMQ_PUB_PORT: DLabel.ZMQ_PUB_PORT,
}
