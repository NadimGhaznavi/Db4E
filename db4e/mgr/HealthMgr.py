# db4e/mgr/HealthMgr.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

import os

# Logging DB
from db4e.util.Db4ELogger import Db4ELogger

# Health DB
from db4e.db.HealthDb import HealthDb
from db4e.util.Helper import HealthMsg

# Deployment elements
from db4e.recs.monero.Db4E import Db4E

# Constants
from db4e.constants.DModule import DModule
from db4e.constants.DStatus import DStatus
from db4e.constants.DField import DField


class HealthMgr:
    """
    Health manager that periodically checks the health of deployed components.
    """

    def __init__(self, health_db: HealthDb, log_file=None):
        self.health_db = health_db
        self.log = Db4ELogger(db4e_module=DModule.HEALTH_MGR, log_file=log_file)

    def check(self, elem):
        """
        Perform health checks on deployed elements.
        """
        self.log.debug(f"Performing health check on {elem}")
        if type(elem) == Db4E:
            self.check_db4e(elem)

    def check_db4e(self, db4e: Db4E):
        # Check that the deployment directory exists
        if os.path.isdir(db4e.vendor_dir()):
            health_msg = HealthMsg(
                instance=DModule.DB4E,
                elem_type=DModule.DB4E,
                category=DField.VENDOR_DIR,
                status=DStatus.GOOD,
                message=f"Found directory {db4e.vendor_dir()}",
            )
        else:
            health_msg = HealthMsg(
                instance=DModule.DB4E,
                elem_type=DModule.DB4E,
                category=DField.VENDOR_DIR,
                status=DStatus.ERROR,
                message=f"Directory {db4e.vendor_dir()} not found",
            )
        self.health_db.upsert_one(health_msg)
