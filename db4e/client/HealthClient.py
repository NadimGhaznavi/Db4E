# db4e/client/HealthClient.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

from db4e.db.HealthDb import HealthDb
from db4e.util.Helper import HealthMsg

from db4e.constants.DSQL import DCol
from db4e.constants.DStatus import DStatus


class HealthClient:

    def __init__(self, health_db: HealthDb):
        self.health_db = health_db

    def get_msgs(self, instance: str, elem_type: str):
        msgs_rows = self.health_db.get_msgs(instance=instance, elem_type=elem_type)
        health_msgs = []
        for rec in msgs_rows:
            health_msgs.append(
                HealthMsg(
                    instance=instance,
                    elem_type=elem_type,
                    category=rec[DCol.CATEGORY],
                    status=rec[DCol.STATUS],
                    message=rec[DCol.MESSAGE],
                )
            )
        return health_msgs

    def get_status(self, instance: str, elem_type: str):
        msgs_rows = self.health_db.get_msgs(instance=instance, elem_type=elem_type)

        status = DStatus.UNKNOWN

        for rec in msgs_rows:
            if rec[DCol.STATUS] == DStatus.ERROR:
                status = DStatus.ERROR
            elif rec[DCol.STATUS] == DStatus.WARN:
                status = DStatus.WARN
            elif rec[DCol.STATUS] == DStatus.GOOD:
                status = DStatus.GOOD

        return status
