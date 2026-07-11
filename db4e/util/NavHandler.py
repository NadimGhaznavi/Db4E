# db4e/util/NavHandler.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0

from db4e.db.DeplDb import DeplDb

from db4e.recs.monero.MoneroD import MoneroD
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.recs.monero.P2Pool import P2Pool
from db4e.recs.monero.P2PoolRemote import P2PoolRemote
from db4e.recs.monero.XMRig import XMRig

from db4e.health.HealthClient import HealthClient
from db4e.util.Helper import get_upstream, is_running
from db4e.sync.SyncClient import SyncClient

from db4e.constants.DField import DField
from db4e.constants.DLabel import DLabel
from db4e.constants.DElem import DElem
from db4e.constants.DSQL import DTable


class NavHandler:
    """
    Handle NavPane requests to access deployments and to create new
    records.
    """

    def __init__(
        self, depl_db: DeplDb, health_client: HealthClient, sync_client=SyncClient
    ):
        """
        Initialize the navigation handler.

        :param depl_db: Deployment database handle.
        :type depl_db: DeplDb
        :return: None
        :rtype: None
        """
        self.depl_db = depl_db
        self.health_client = health_client
        self.sync_client = sync_client

    def get_deployment(self, request):
        """
        Return an existing deployment based on request parameters.

        :param request: Request payload containing element type and instance.
        :type request: dict
        :return: Deployment object.
        :rtype: object
        """
        elem_type = request.get(DField.ELEMENT_TYPE)
        instance = request.get(DField.INSTANCE)
        depl_obj = self.depl_db.get_deployment(elem_type=elem_type, instance=instance)

        if not depl_obj:
            raise RuntimeError(
                f"Unable to locate object in database: {elem_type}/{instance}"
            )

        # Get the health messages
        health_msgs = self.health_client.get_msgs(
            instance=instance, elem_type=elem_type
        )
        # print(f"Health msgs: {health_msgs}")
        depl_obj.set_msgs(health_msgs)

        # Get the status information so the pane can determine button visibility
        if elem_type == DElem.MONEROD:
            depl_obj.status(self.health_client.get_status(depl_obj))

        # This instance map is used to configure the "primary server" radio
        # button
        if elem_type == DElem.DB4E:
            local = self.depl_db.get_deployment_ids_and_instances(DTable.MONEROD)
            remote = self.depl_db.get_deployment_ids_and_instances(
                DTable.MONEROD_REMOTE
            )
            depl_obj.instance_map({**local, **remote})

        # This instance map is used to configure the upstream MoneroD or
        # remote MoneroD instance.
        elif elem_type == DElem.P2POOL:
            local = self.depl_db.get_deployment_ids_and_instances(DTable.MONEROD)
            remote = self.depl_db.get_deployment_ids_and_instances(
                DTable.MONEROD_REMOTE
            )
            depl_obj.instance_map({**local, **remote})
            depl_obj.status(self.health_client.get_status(depl_obj))

        # This instance map is used to configure the upstream P2Pool or remote
        # P2Pool instance.
        elif elem_type == DElem.XMRIG:
            local = self.depl_db.get_deployment_ids_and_instances(DTable.P2POOL)
            remote = self.depl_db.get_deployment_ids_and_instances(DTable.P2POOL_REMOTE)
            depl_obj.instance_map({**local, **remote})

        return depl_obj

    async def get_log(self, request):
        elem_type = request.get(DField.ELEMENT_TYPE)
        elem = request.get(DField.ELEMENT)
        if DField.LOG_LINES in request:
            num_lines = int(request.get(DField.LOG_LINES))
        else:
            num_lines = DField.LINES_100
        log_lines = await self.sync_client.get_log(
            {
                DField.ELEMENT: elem,
                DField.ELEMENT_TYPE: elem_type,
                DField.LOG_LINES: num_lines,
            }
        )
        elem.log_lines(log_lines)
        return elem

    def get_new(self, request):
        """
        Return a new deployment object based on request parameters.

        :param request: Request payload containing element type.
        :type request: dict
        :return: New deployment object.
        :rtype: object
        """
        elem_type = request.get(DField.ELEMENT_TYPE)

        if elem_type == DElem.MONEROD:
            return MoneroD()

        elif elem_type == DElem.MONEROD_REMOTE:
            return MoneroDRemote()

        elif elem_type == DElem.P2POOL:
            p2pool = P2Pool()
            db4e = self.depl_db.get_deployment(
                elem_type=DElem.DB4E, instance=DLabel.DB4E
            )
            p2pool.user_wallet(db4e.user_wallet())
            local = self.depl_db.get_deployment_ids_and_instances(DTable.MONEROD)
            remote = self.depl_db.get_deployment_ids_and_instances(
                DTable.MONEROD_REMOTE
            )
            p2pool.instance_map({**local, **remote})
            p2pool.is_running = is_running(p2pool.pop_msgs())
            return p2pool

        elif elem_type == DElem.P2POOL_REMOTE:
            return P2PoolRemote()

        elif elem_type == DElem.XMRIG:
            xmrig = XMRig()
            local = self.depl_db.get_deployment_ids_and_instances(DTable.P2POOL)
            remote = self.depl_db.get_deployment_ids_and_instances(DTable.P2POOL_REMOTE)
            xmrig.instance_map({**local, **remote})
            return xmrig

        else:
            raise ValueError(f"NavHandler:get_new():Unknown element type: {elem_type}")

    def set_pane(self, request):
        """
        Return the pane name to display for the request.

        :param request: Request payload containing element type.
        :type request: dict
        :return: Pane name.
        :rtype: str
        """
        pane_name = request.get(DField.ELEMENT_TYPE)
        return pane_name
