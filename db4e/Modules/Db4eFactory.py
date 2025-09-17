"""
db4e/Modules/Factory.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""


# import other system subclasses as needed

from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField


def make_system(rec: dict):
    """Return the correct SoftwareSystem subclass for the given record."""

    # Avoid circular imports
    from db4e.Modules.Db4E import Db4E
    from db4e.Modules.P2PoolInternal import P2PoolInternal
    from db4e.Modules.Job import Job
    from db4e.Modules.MoneroD import MoneroD
    from db4e.Modules.MoneroDRemote import MoneroDRemote
    from db4e.Modules.P2Pool import P2Pool
    from db4e.Modules.P2PoolRemote import P2PoolRemote
    from db4e.Modules.XMRig import XMRig

    # Maps element_type (from rec[DField.ELEMENT_TYPE]) to the right class
    ELEMENT_CLASS_MAP = {
        DElem.DB4E: Db4E,
        DElem.P2POOL_INTERNAL: P2PoolInternal,
        DElem.JOB: Job,
        DElem.MONEROD: MoneroD,
        DElem.MONEROD_REMOTE: MoneroDRemote,
        DElem.P2POOL: P2Pool,
        DElem.P2POOL_REMOTE: P2PoolRemote,
        DElem.XMRIG: XMRig
    }

    elem_type = rec.get(DField.ELEMENT_TYPE)

    if elem_type not in ELEMENT_CLASS_MAP:
        raise ValueError(f"Unknown element_type: {elem_type}")

    db4e_class = ELEMENT_CLASS_MAP[elem_type]
    return db4e_class
