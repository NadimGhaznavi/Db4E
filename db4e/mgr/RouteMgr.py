"""
db4e/Modules/MessageRouter.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.mgr.InstallMgr import InstallMgr
from db4e.mgr.PaneMgr import PaneMgr

from db4e.sync.SyncClient import SyncClient


from db4e.util.NavHandler import NavHandler

from db4e.db.DeplDb import DeplDb
from db4e.db.OpsDb import OpsDb

from db4e.constants.DMethod import DMethod
from db4e.constants.DField import DField
from db4e.constants.DElem import DElem
from db4e.constants.DPane import DPane
from db4e.constants.DModule import DModule


class RouteMgr:
    def __init__(
        self,
        depl_db: DeplDb,
        ops_db: OpsDb,
        install_mgr: InstallMgr,
        pane_mgr: PaneMgr,
        sync_client: SyncClient,
    ):
        self.routes: dict[tuple[str, str, str], tuple[callable, str]] = {}
        self._panes = {}
        self.install_mgr = install_mgr
        self.depl_db = depl_db
        self.nav_handler = NavHandler(depl_db=self.depl_db)
        self.ops_db = ops_db
        self.pane_mgr = pane_mgr
        self.sync_client = sync_client
        self._route_handlers = []
        self.load_routes()

    def load_routes(self):
        # Db4e core - Proceed/abort initial install
        self.register(
            DModule.INSTALL_MGR,
            DMethod.INITIAL_SETUP_PROCEED,
            DElem.DB4E,
            self.install_mgr.initial_setup_proceed,
            DPane.INITIAL_SETUP,
        )
        # Db4E core - Initial install
        self.register(
            DModule.INSTALL_MGR,
            DMethod.INITIAL_SETUP,
            DElem.DB4E,
            self.install_mgr.initial_setup,
            DPane.TUI_LOG,
        )
        # Db4E core - View/edit
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_DEPL,
            DElem.DB4E,
            self.nav_handler.get_deployment,
            DPane.DB4E,
        )
        # Db4E core - Update
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.UPDATE_DEPLOYMENT,
            DElem.DB4E,
            self.sync_client.update_deployment,
            DPane.TUI_LOG,
        )
        ## MoneroD deployment
        # Display the new form
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_NEW,
            DElem.MONEROD,
            self.nav_handler.get_new,
            DPane.MONEROD,
        )
        # Add a new deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.ADD_DEPLOYMENT,
            DElem.MONEROD,
            self.sync_client.add_deployment,
            DPane.TUI_LOG,
        )
        # View/edit deployment
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_DEPL,
            DElem.MONEROD,
            self.nav_handler.get_deployment,
            DPane.MONEROD,
        )
        # Update deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.UPDATE_DEPLOYMENT,
            DElem.MONEROD,
            self.sync_client.update_deployment,
            DPane.TUI_LOG,
        )
        # Delete deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.DELETE_DEPLOYMENT,
            DElem.MONEROD,
            self.sync_client.delete_deployment,
            DPane.TUI_LOG,
        )

        ## Remote MoneroD deployment
        # Display the new form
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_NEW,
            DElem.MONEROD_REMOTE,
            self.nav_handler.get_new,
            DPane.MONEROD_REMOTE,
        )
        # Add a new deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.ADD_DEPLOYMENT,
            DElem.MONEROD_REMOTE,
            self.sync_client.add_deployment,
            DPane.TUI_LOG,
        )
        # View/edit a deployment
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_DEPL,
            DElem.MONEROD_REMOTE,
            self.nav_handler.get_deployment,
            DPane.MONEROD_REMOTE,
        )
        # Update a deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.UPDATE_DEPLOYMENT,
            DElem.MONEROD_REMOTE,
            self.sync_client.update_deployment,
            DPane.TUI_LOG,
        )
        # Delete a deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.DELETE_DEPLOYMENT,
            DElem.MONEROD_REMOTE,
            self.sync_client.delete_deployment,
            DPane.TUI_LOG,
        )

        ## P2Pool deployment
        # Display the new form
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_NEW,
            DElem.P2POOL,
            self.nav_handler.get_new,
            DPane.P2POOL,
        )
        # Add a new deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.ADD_DEPLOYMENT,
            DElem.P2POOL,
            self.sync_client.add_deployment,
            DPane.TUI_LOG,
        )
        # View/edit a deployment
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_DEPL,
            DElem.P2POOL,
            self.nav_handler.get_deployment,
            DPane.P2POOL,
        )
        # Update a deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.UPDATE_DEPLOYMENT,
            DElem.P2POOL,
            self.sync_client.update_deployment,
            DPane.TUI_LOG,
        )
        # Delete a deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.DELETE_DEPLOYMENT,
            DElem.P2POOL,
            self.sync_client.delete_deployment,
            DPane.TUI_LOG,
        )

        ## Remote P2Pool deployment
        # Display the new form
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_NEW,
            DElem.P2POOL_REMOTE,
            self.nav_handler.get_new,
            DPane.P2POOL_REMOTE,
        )
        # Add a new deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.ADD_DEPLOYMENT,
            DElem.P2POOL_REMOTE,
            self.sync_client.add_deployment,
            DPane.TUI_LOG,
        )
        # View/edit a deployment
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_DEPL,
            DElem.P2POOL_REMOTE,
            self.nav_handler.get_deployment,
            DPane.P2POOL_REMOTE,
        )
        # Update a deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.UPDATE_DEPLOYMENT,
            DElem.P2POOL_REMOTE,
            self.sync_client.update_deployment,
            DPane.TUI_LOG,
        )
        # Delete a deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.DELETE_DEPLOYMENT,
            DElem.P2POOL_REMOTE,
            self.sync_client.delete_deployment,
            DPane.TUI_LOG,
        )

        ## Internal P2Pool deployment
        # View "Chain Pane"
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_DEPL,
            DElem.P2POOL_INTERNAL,
            self.nav_handler.get_deployment,
            DPane.CHAIN,
        )

        ## XMRig deployment
        # Display the new deployment form
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_NEW,
            DElem.XMRIG,
            self.nav_handler.get_new,
            DPane.XMRIG,
        )
        # Add a new deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.ADD_DEPLOYMENT,
            DElem.XMRIG,
            self.sync_client.add_deployment,
            DPane.TUI_LOG,
        )
        # View/edit a deployment
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_DEPL,
            DElem.XMRIG,
            self.nav_handler.get_deployment,
            DPane.XMRIG,
        )
        # Update a deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.UPDATE_DEPLOYMENT,
            DElem.XMRIG,
            self.sync_client.update_deployment,
            DPane.TUI_LOG,
        )
        # Delete a deployment
        self.register(
            DModule.SYNC_CLIENT,
            DMethod.DELETE_DEPLOYMENT,
            DElem.XMRIG,
            self.sync_client.delete_deployment,
            DPane.TUI_LOG,
        )

        ## Remote XMRig Deployment
        # View the "Remote XMRig Pane"
        self.register(
            DModule.NAV_HANDLER,
            DMethod.GET_DEPL,
            DElem.XMRIG_REMOTE,
            self.nav_handler.get_deployment,
            DPane.XMRIG_REMOTE,
        )

        # Console log
        self.register(
            DModule.OPS_DB,
            DMethod.GET_TUI_LOG,
            DField.TUI_LOG,
            self.ops_db.get_tui_log,
            DPane.TUI_LOG,
        )

        # Donations
        self.register(
            DModule.NAV_HANDLER,
            DMethod.SET_PANE,
            DField.DONATIONS,
            self.nav_handler.set_pane,
            DPane.DONATIONS,
        )

    def get_handler(self, module: str, method: str, component: str = ""):
        return self.routes.get((module, method, component))

    def get_pane(self, module: str, method: str, component: str = ""):
        return self._panes.get((module, method, component))

    async def dispatch(
        self, some_module: str, some_method: str = None, payload: dict = None
    ):
        print(f"MessageRouter:dispatch(): {some_module}:{some_method}({payload})")
        elem_type = payload.get(DField.ELEMENT_TYPE, "")
        handler = self.get_handler(some_module, some_method, elem_type)
        if not handler:
            raise ValueError(
                f"RouteMgr:dispatch():No handler for: module: {some_module}, "
                f"method: {some_method}, elem_type: {elem_type}"
            )

        callback, pane = handler
        # await add_deployment
        if callback == self.sync_client.add_deployment:
            result = await callback(payload)
        # await update_deployment
        elif callback == self.sync_client.update_deployment:
            result = await callback(payload)
        # await delete_deployment
        elif callback == self.sync_client.delete_deployment:
            result = await callback(payload)

        # Fallback (a synchronous method, no `await`).
        else:
            result = callback(payload)
        return result, pane

    def register(
        self, field: str, method: str, component: str, callback: callable, pane: str
    ):
        self.routes[(field, method, component)] = (callback, pane)
