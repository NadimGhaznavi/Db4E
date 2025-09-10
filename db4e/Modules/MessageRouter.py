"""
db4e/Modules/MessageRouter.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import re
import inspect

from db4e.Modules.InstallMgr import InstallMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.PaneCatalogue import PaneCatalogue
from db4e.Modules.PaneMgr import PaneMgr
from db4e.Modules.OpsMgr import OpsMgr

from db4e.Constants.Fields import DMod, DField, DElem, Method
from db4e.Constants.Jobs import DJob
from db4e.Constants.Panes import Pane
from db4e.Constants.Buttons import DButton


class MessageRouter:
    def __init__(self):
        self.routes: dict[tuple[str, str, str], tuple[callable, str]] = {}
        self._panes = {}
        self.install_mgr = InstallMgr()
        self.depl_mgr = DeploymentMgr()
        self.ops_mgr = OpsMgr()
        self.pane_mgr = PaneMgr(catalogue=PaneCatalogue())
        self._route_handlers = []
        self.load_routes()

    def load_routes(self):
        # Db4e core
        self.register(DMod.INSTALL_MGR, Method.INITIAL_SETUP_PROCEED, DElem.DB4E,
                      self.install_mgr.initial_setup_proceed, Pane.INITIAL_SETUP)
        self.register(DMod.INSTALL_MGR, Method.INITIAL_SETUP, DElem.DB4E,
                      self.install_mgr.initial_setup, Pane.RESULTS)
        self.register(DMod.OPS_MGR, Method.GET_REC, DElem.DB4E,
                      self.ops_mgr.get_deployment, Pane.DB4E)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.DB4E,
                      self.depl_mgr.update_deployment, Pane.WELCOME)

        # MoneroD = Type: local or remote
        self.register(DMod.PANE_MGR, DField.SET, DElem.MONEROD,
                      self.pane_mgr.set_pane, Pane.MONEROD_TYPE)

        # MoneroD - local
        self.register(DMod.OPS_MGR, Method.GET_NEW, DElem.MONEROD,
                      self.ops_mgr.get_new, Pane.MONEROD)
        self.register(DMod.OPS_MGR, Method.ADD_DEPLOYMENT, DElem.MONEROD,
                      self.ops_mgr.add_deployment, Pane.MONEROD)
        self.register(DMod.OPS_MGR, Method.GET_REC, DElem.MONEROD,
                      self.ops_mgr.get_deployment, Pane.MONEROD)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.MONEROD,
                      self.depl_mgr.post_job, Pane.WELCOME)
        self.register(DMod.DEPLOYMENT_MGR, Method.DELETE_DEPLOYMENT, DElem.MONEROD,
                      self.depl_mgr.del_deployment, Pane.MONEROD)

        # MoneroD - remote
        self.register(DMod.OPS_MGR, Method.GET_NEW, DElem.MONEROD_REMOTE,
                      self.ops_mgr.get_new, Pane.MONEROD_REMOTE)
        self.register(DMod.OPS_MGR, Method.ADD_DEPLOYMENT, DElem.MONEROD_REMOTE,
                      self.ops_mgr.add_deployment, Pane.MONEROD_REMOTE)
        self.register(DMod.OPS_MGR, Method.GET_REC, DElem.MONEROD_REMOTE,
                      self.ops_mgr.get_deployment, Pane.MONEROD_REMOTE)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.MONEROD_REMOTE,
                      self.depl_mgr.post_job, Pane.WELCOME)
        self.register(DMod.DEPLOYMENT_MGR, Method.DELETE_DEPLOYMENT, DElem.MONEROD_REMOTE,
                      self.depl_mgr.del_deployment, Pane.MONEROD_REMOTE)
        

        # MoneroD = Type: local or remote
        self.register(DMod.PANE_MGR, DField.SET, DElem.P2POOL,
                      self.pane_mgr.set_pane, Pane.P2POOL_TYPE)

        # P2Pool - local
        self.register(DMod.OPS_MGR, Method.GET_NEW, DElem.P2POOL,
                      self.ops_mgr.get_new, Pane.P2POOL)
        self.register(DMod.OPS_MGR, Method.ADD_DEPLOYMENT, DElem.P2POOL,
                      self.ops_mgr.add_deployment, Pane.P2POOL)
        self.register(DMod.OPS_MGR, Method.GET_REC, DElem.P2POOL,
                      self.ops_mgr.get_deployment, Pane.P2POOL)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.P2POOL,
                      self.depl_mgr.post_job, Pane.WELCOME)
        self.register(DMod.DEPLOYMENT_MGR, Method.DELETE_DEPLOYMENT, DElem.P2POOL,
                      self.depl_mgr.del_deployment, Pane.P2POOL)

        # P2Pool - remote
        self.register(DMod.OPS_MGR, Method.GET_NEW, DElem.P2POOL_REMOTE,
                      self.ops_mgr.get_new, Pane.P2POOL_REMOTE)
        self.register(DMod.OPS_MGR, Method.ADD_DEPLOYMENT, DElem.P2POOL_REMOTE,
                      self.ops_mgr.add_deployment, Pane.P2POOL_REMOTE)
        self.register(DMod.OPS_MGR, Method.GET_REC, DElem.P2POOL_REMOTE,
                      self.ops_mgr.get_deployment, Pane.P2POOL_REMOTE)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.P2POOL_REMOTE,
                      self.depl_mgr.post_job, Pane.WELCOME)
        self.register(DMod.DEPLOYMENT_MGR, Method.DELETE_DEPLOYMENT, DElem.P2POOL_REMOTE,
                      self.depl_mgr.del_deployment, Pane.P2POOL_REMOTE)

        # XMRig
        self.register(DMod.OPS_MGR, Method.GET_NEW, DElem.XMRIG,
                      self.ops_mgr.get_new, Pane.XMRIG)
        self.register(DMod.OPS_MGR, Method.ADD_DEPLOYMENT, DElem.XMRIG,
                      self.ops_mgr.add_deployment, Pane.XMRIG)
        self.register(DMod.OPS_MGR, Method.GET_REC, DElem.XMRIG,
                      self.ops_mgr.get_deployment, Pane.XMRIG)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.XMRIG,
                      self.depl_mgr.post_job, Pane.WELCOME)
        self.register(DMod.DEPLOYMENT_MGR, Method.DELETE_DEPLOYMENT, DElem.XMRIG,
                      self.depl_mgr.del_deployment, Pane.XMRIG)

        # Log Viewer
        self.register(DMod.OPS_MGR, Method.LOG_VIEWER, DElem.MONEROD,
                      self.ops_mgr.log_viewer, Pane.LOG_VIEW)
        self.register(DMod.OPS_MGR, Method.LOG_VIEWER, DElem.P2POOL,
                      self.ops_mgr.log_viewer, Pane.LOG_VIEW)
        self.register(DMod.OPS_MGR, Method.LOG_VIEWER, DElem.XMRIG,
                      self.ops_mgr.log_viewer, Pane.LOG_VIEW)

        # Plots
        self.register(DMod.OPS_MGR, Method.PLOT, DField.CHAIN,
                      self.ops_mgr.plot, Pane.PLOT_VIEW)

        # TUI Log
        self.register(DMod.OPS_MGR, Method.GET_TUI_LOG, DField.TUI_LOG,
                      self.ops_mgr.get_tui_log, Pane.TUI_LOG)

        # Donations
        self.register(DMod.PANE_MGR, Method.SET, DField.DONATIONS,
                      self.pane_mgr.set_pane, Pane.DONATIONS)


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
