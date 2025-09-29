"""
db4e/Modules/MessageRouter.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.DeplClient import DeplClient
from db4e.Modules.InstallMgr import InstallMgr
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.PaneMgr import PaneMgr

from db4e.Constants.DMethod import DMethod
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DPane import DPane
from db4e.Constants.DModule import DModule



class MessageRouter:
    def __init__(
            self, depl_client: DeplClient, install_mgr: 
            InstallMgr, pane_mgr: PaneMgr, ops_mgr: OpsMgr):
        self.routes: dict[tuple[str, str, str], tuple[callable, str]] = {}
        self._panes = {}
        self.install_mgr = install_mgr
        self.depl_client = depl_client
        self.ops_mgr = ops_mgr
        self.pane_mgr = pane_mgr
        self._route_handlers = []
        self.load_routes()

    def load_routes(self):
        # Db4e core
        self.register(DModule.INSTALL_MGR, DMethod.INITIAL_SETUP_PROCEED, DElem.DB4E,
                      self.install_mgr.initial_setup_proceed, DPane.INITIAL_SETUP)
        self.register(DModule.INSTALL_MGR, DMethod.INITIAL_SETUP, DElem.DB4E,
                      self.install_mgr.initial_setup, DPane.RESULTS)
        self.register(DModule.OPS_MGR, DMethod.GET_DEPL, DElem.DB4E,
                      self.ops_mgr.get_deployment, DPane.DB4E)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.UPDATE_DEPLOYMENT, DElem.DB4E,
                      self.depl_client.update_deployment, DPane.WELCOME)
        self.register(DModule.OPS_MGR, DMethod.GET_UPTIME, DElem.DB4E,
                      self.ops_mgr.get_uptime, DPane.UPTIME)

        # MoneroD - local
        self.register(DModule.OPS_MGR, DMethod.GET_NEW, DElem.MONEROD,
                      self.ops_mgr.get_new, DPane.MONEROD)
        self.register(DModule.OPS_MGR, DMethod.ADD_DEPLOYMENT, DElem.MONEROD,
                      self.ops_mgr.add_deployment, DPane.WELCOME)
        self.register(DModule.OPS_MGR, DMethod.GET_DEPL, DElem.MONEROD,
                      self.ops_mgr.get_deployment, DPane.MONEROD)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.DISABLE_DEPLOYMENT, DElem.MONEROD,
                      self.depl_client.disable_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.ENABLE_DEPLOYMENT, DElem.MONEROD,
                      self.depl_client.enable_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.UPDATE_DEPLOYMENT, DElem.MONEROD,
                      self.depl_client.update_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.DELETE_DEPLOYMENT, DElem.MONEROD,
                      self.depl_client.delete_deployment, DPane.WELCOME)

        # MoneroD - remote
        self.register(DModule.OPS_MGR, DMethod.GET_NEW, DElem.MONEROD_REMOTE,
                      self.ops_mgr.get_new, DPane.MONEROD_REMOTE)
        self.register(DModule.OPS_MGR, DMethod.ADD_DEPLOYMENT, DElem.MONEROD_REMOTE,
                      self.ops_mgr.add_deployment, DPane.WELCOME)
        self.register(DModule.OPS_MGR, DMethod.GET_DEPL, DElem.MONEROD_REMOTE,
                      self.ops_mgr.get_deployment, DPane.MONEROD_REMOTE)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.UPDATE_DEPLOYMENT, DElem.MONEROD_REMOTE,
                      self.depl_client.update_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.DELETE_DEPLOYMENT, DElem.MONEROD_REMOTE,
                      self.depl_client.delete_deployment, DPane.WELCOME)
        

        # P2Pool - Local
        self.register(DModule.OPS_MGR, DMethod.GET_NEW, DElem.P2POOL,
                      self.ops_mgr.get_new, DPane.P2POOL)
        self.register(DModule.OPS_MGR, DMethod.ADD_DEPLOYMENT, DElem.P2POOL,
                      self.ops_mgr.add_deployment, DPane.WELCOME)
        self.register(DModule.OPS_MGR, DMethod.HASHRATES, DElem.P2POOL,
                      self.ops_mgr.hashrates, DPane.P2POOL_HASHRATES)
        self.register(DModule.OPS_MGR, DMethod.GET_DEPL, DElem.P2POOL,
                      self.ops_mgr.get_deployment, DPane.P2POOL)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.DISABLE_DEPLOYMENT, DElem.P2POOL,
                      self.depl_client.disable_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.ENABLE_DEPLOYMENT, DElem.P2POOL,
                      self.depl_client.enable_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.UPDATE_DEPLOYMENT, DElem.P2POOL,
                      self.depl_client.update_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.DELETE_DEPLOYMENT, DElem.P2POOL,
                      self.depl_client.delete_deployment, DPane.WELCOME)

        # P2Pool - Remote
        self.register(DModule.OPS_MGR, DMethod.GET_NEW, DElem.P2POOL_REMOTE,
                      self.ops_mgr.get_new, DPane.P2POOL_REMOTE)
        self.register(DModule.OPS_MGR, DMethod.ADD_DEPLOYMENT, DElem.P2POOL_REMOTE,
                      self.ops_mgr.add_deployment, DPane.WELCOME)
        self.register(DModule.OPS_MGR, DMethod.GET_DEPL, DElem.P2POOL_REMOTE,
                      self.ops_mgr.get_deployment, DPane.P2POOL_REMOTE)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.UPDATE_DEPLOYMENT, DElem.P2POOL_REMOTE,
                      self.depl_client.update_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.DELETE_DEPLOYMENT, DElem.P2POOL_REMOTE,
                      self.depl_client.delete_deployment, DPane.WELCOME)

        # P2Pool - Internal
        self.register(DModule.OPS_MGR, DMethod.GET_DEPL, DElem.INT_P2POOL,
                      self.ops_mgr.get_deployment, DPane.CHAIN)
        self.register(DModule.OPS_MGR, DMethod.HASHRATES, DElem.INT_P2POOL,
                      self.ops_mgr.hashrates, DPane.CHAIN_ANALYTICS)

        # XMRig
        self.register(DModule.OPS_MGR, DMethod.GET_NEW, DElem.XMRIG,
                      self.ops_mgr.get_new, DPane.XMRIG)
        self.register(DModule.OPS_MGR, DMethod.ADD_DEPLOYMENT, DElem.XMRIG,
                      self.ops_mgr.add_deployment, DPane.WELCOME)
        self.register(DModule.OPS_MGR, DMethod.HASHRATES, DElem.XMRIG,
                      self.ops_mgr.hashrates, DPane.XMRIG_HASHRATES)
        self.register(DModule.OPS_MGR, DMethod.GET_DEPL, DElem.XMRIG,
                      self.ops_mgr.get_deployment, DPane.XMRIG)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.DISABLE_DEPLOYMENT, DElem.XMRIG,
                      self.depl_client.disable_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.ENABLE_DEPLOYMENT, DElem.XMRIG,
                      self.depl_client.enable_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.UPDATE_DEPLOYMENT, DElem.XMRIG,
                      self.depl_client.update_deployment, DPane.WELCOME)
        self.register(DModule.DEPLOYMENT_CLIENT, DMethod.DELETE_DEPLOYMENT, DElem.XMRIG,
                      self.depl_client.delete_deployment, DPane.WELCOME)

        # XMRig Remote
        self.register(DModule.OPS_MGR, DMethod.GET_DEPL, DElem.XMRIG_REMOTE,
                      self.ops_mgr.get_deployment, DPane.XMRIG_REMOTE)

        # Log Viewer
        self.register(DModule.OPS_MGR, DMethod.LOG_VIEWER, DElem.MONEROD,
                      self.ops_mgr.log_viewer, DPane.LOG_VIEW)
        self.register(DModule.OPS_MGR, DMethod.LOG_VIEWER, DElem.P2POOL,
                      self.ops_mgr.log_viewer, DPane.LOG_VIEW)
        self.register(DModule.OPS_MGR, DMethod.LOG_VIEWER, DElem.INT_P2POOL,
                      self.ops_mgr.log_viewer, DPane.LOG_VIEW)
        self.register(DModule.OPS_MGR, DMethod.LOG_VIEWER, DElem.XMRIG,
                      self.ops_mgr.log_viewer, DPane.LOG_VIEW)

        # TUI Log
        self.register(DModule.OPS_MGR, DMethod.GET_TUI_LOG, DField.TUI_LOG,
                      self.ops_mgr.get_tui_log, DPane.TUI_LOG)

        # Runtime Log
        self.register(DModule.OPS_MGR, DMethod.GET_RUNTIME_LOG, DField.RUNTIME_LOG,
                      self.ops_mgr.get_runtime_log, DPane.RUNTIME_LOG)

        # Donations
        self.register(DModule.OPS_MGR, DMethod.SET_DONATIONS, DField.DONATIONS,
                      self.ops_mgr.set_donations, DPane.DONATIONS)


    def get_handler(self, module: str, method: str, component: str = ""):
        return self.routes.get((module, method, component))

    def get_pane(self, module: str, method: str, component: str = ""):
        return self._panes.get((module, method, component))

    def dispatch(self, some_module: str, some_method: str = None, payload: dict = None):
        print(f"MessageRouter:dispatch(): {some_module}:{some_method}({payload})")
        elem_type = payload.get(DField.ELEMENT_TYPE, "")
        handler = self.get_handler(some_module, some_method, elem_type)
        if not handler:
            raise ValueError(
                f"MessageRouter:dispatch():No handler for: module: {some_module}, " \
                f"method: {some_method}, elem_type: {elem_type}")

        callback, pane = handler
        result = callback(payload)
        return result, pane

    def register(self, field: str, method: str, component: str, callback: callable, pane: str):
        self.routes[(field, method, component)] = (callback, pane)
