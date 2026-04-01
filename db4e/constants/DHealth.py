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
    ENABLED = DField.ENABLED
    RPC_BIND_PORT = DField.RPC_BIND_PORT
    STRATUM_PORT = DField.STRATUM_PORT
    VENDOR_DIR = DField.VENDOR_DIR
    ZMQ_PUB_PORT = DField.ZMQ_PUB_PORT


CATEGORY_LABEL_MAP = {
    DField.ENABLED: DLabel.ENABLED,
    DField.RPC_BIND_PORT: DLabel.RPC_BIND_PORT,
    DField.STRATUM_PORT: DLabel.STRATUM_PORT,
    DField.VENDOR_DIR: DLabel.VENDOR_DIR,
    DField.ZMQ_PUB_PORT: DLabel.ZMQ_PUB_PORT,
}
