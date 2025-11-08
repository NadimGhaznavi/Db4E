"""
db4e/util/NavHandler.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.db.DeplDb import DeplDb
from db4e.constants.DField import DField
from db4e.constants.DElem import DElem

from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig


class NavHandler:
    """Class to handle NavPane requests"""

    def __init__(self, depl_db: DeplDb):
        self.depl_db = depl_db

    def get_deployment(self, request):
        elem_type = request.get(DField.ELEMENT_TYPE)
        instance = request.get(DField.INSTANCE)
        depl_obj = self.depl_db.get_deployment(elem_type=elem_type, instance=instance)

        if elem_type == DElem.DB4E:
            local = self.depl_db.get_deployment_ids_and_instances(DElem.MONEROD)
            remote = self.depl_db.get_deployment_ids_and_instances(DElem.MONEROD_REMOTE)
            depl_obj.instance_map({**local, **remote})

        elif elem_type == DElem.P2POOL:
            local = self.depl_db.get_deployment_ids_and_instances(DElem.MONEROD)
            remote = self.depl_db.get_deployment_ids_and_instances(DElem.MONEROD_REMOTE)
            depl_obj.instance_map({**local, **remote})

        elif elem_type == DElem.XMRIG:
            local = self.depl_db.get_deployment_ids_and_instances(DElem.P2POOL)
            remote = self.depl_db.get_deployment_ids_and_instances(DElem.P2POOL_REMOTE)
            depl_obj.instance_map({**local, **remote})

        return depl_obj

    def get_new(self, request):
        elem_type = request.get(DField.ELEMENT_TYPE)

        if elem_type == DElem.MONEROD:
            return MoneroD()

        elif elem_type == DElem.MONEROD_REMOTE:
            return MoneroDRemote()

        elif elem_type == DElem.P2POOL:
            p2pool = P2Pool()
            db4e = self.depl_db.get_deployment(DElem.DB4E, DElem.DB4E)
            p2pool.user_wallet(db4e.user_wallet())
            local = self.depl_db.get_deployment_ids_and_instances(DElem.MONEROD)
            remote = self.depl_db.get_deployment_ids_and_instances(DElem.MONEROD_REMOTE)
            p2pool.instance_map({**local, **remote})
            return p2pool

        elif elem_type == DElem.P2POOL_REMOTE:
            return P2PoolRemote()

        elif elem_type == DElem.XMRIG:
            xmrig = XMRig()
            local = self.depl_db.get_deployment_ids_and_instances(DElem.P2POOL)
            remote = self.depl_db.get_deployment_ids_and_instances(DElem.P2POOL_REMOTE)
            xmrig.instance_map({**local, **remote})
            return xmrig

        else:
            raise ValueError(f"NavHandler:get_new():Unknown element type: {elem_type}")

    def set_pane(self, request):
        pane_name = request.get(DField.ELEMENT_TYPE)
        return pane_name
