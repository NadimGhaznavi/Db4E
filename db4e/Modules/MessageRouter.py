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

from db4e.Constants.Fields import (GET_REC_FIELD, SET_PANE_FIELD,LOG_VIEWER_FIELD,
    ADD_DEPLOYMENT_FIELD, DELETE_DEPLOYMENT_FIELD, GET_NEW_FIELD, INITIAL_SETUP_FIELD,
    PLOT_FIELD, CHAIN_FIELD, GET_TUI_LOG_FIELD, TUI_LOG_FIELD, DONATIONS_FIELD)
from db4e.Constants.Fields import DMod, DField, DElem
from db4e.Constants.Jobs import DJob
from db4e.Constants.Panes import (
    DB4E_PANE, DONATIONS_PANE, INITIAL_SETUP_PANE, MONEROD_PANE, MONEROD_REMOTE_PANE, 
    MONEROD_TYPE_PANE, WELCOME_PANE, TUI_LOG_PANE, LOG_VIEW_PANE, PLOT_VIEW_PANE,
    P2POOL_PANE, P2POOL_REMOTE_PANE, P2POOL_TYPE_PANE, XMRIG_PANE, RESULTS_PANE)
from db4e.Constants.Buttons import INITIAL_SETUP_PROCEED_FIELD


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
        self.register(DMod.INSTALL_MGR, INITIAL_SETUP_PROCEED_FIELD, DElem.DB4E,
                      self.install_mgr.initial_setup_proceed, INITIAL_SETUP_PANE)
        self.register(DMod.INSTALL_MGR, INITIAL_SETUP_FIELD, DElem.DB4E,
                      self.install_mgr.initial_setup, RESULTS_PANE)
        self.register(DMod.OPS_MGR, GET_REC_FIELD, DElem.DB4E,
                      self.ops_mgr.get_deployment, DB4E_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.DB4E,
                      self.depl_mgr.update_deployment, WELCOME_PANE)

        # MoneroD = Type: local or remote
        self.register(DMod.PANE_MGR, SET_PANE_FIELD, DElem.MONEROD,
                      self.pane_mgr.set_pane, MONEROD_TYPE_PANE)

        # MoneroD - local
        self.register(DMod.OPS_MGR, GET_NEW_FIELD, DElem.MONEROD,
                      self.ops_mgr.get_new, MONEROD_PANE)
        self.register(DMod.OPS_MGR, ADD_DEPLOYMENT_FIELD, DElem.MONEROD,
                      self.ops_mgr.add_deployment, MONEROD_PANE)
        self.register(DMod.OPS_MGR, GET_REC_FIELD, DElem.MONEROD,
                      self.ops_mgr.get_deployment, MONEROD_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.MONEROD,
                      self.depl_mgr.post_job, WELCOME_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DELETE_DEPLOYMENT_FIELD, DElem.MONEROD,
                      self.depl_mgr.del_deployment, MONEROD_PANE)

        # MoneroD - remote
        self.register(DMod.OPS_MGR, GET_NEW_FIELD, DElem.MONEROD_REMOTE,
                      self.ops_mgr.get_new, MONEROD_REMOTE_PANE)
        self.register(DMod.OPS_MGR, ADD_DEPLOYMENT_FIELD, DElem.MONEROD_REMOTE,
                      self.ops_mgr.add_deployment, MONEROD_REMOTE_PANE)
        self.register(DMod.OPS_MGR, GET_REC_FIELD, DElem.MONEROD_REMOTE,
                      self.ops_mgr.get_deployment, MONEROD_REMOTE_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.MONEROD_REMOTE,
                      self.depl_mgr.post_job, WELCOME_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DELETE_DEPLOYMENT_FIELD, DElem.MONEROD_REMOTE,
                      self.depl_mgr.del_deployment, MONEROD_REMOTE_PANE)
        

        # MoneroD = Type: local or remote
        self.register(DMod.PANE_MGR, SET_PANE_FIELD, DElem.P2POOL,
                      self.pane_mgr.set_pane, P2POOL_TYPE_PANE)

        # P2Pool - local
        self.register(DMod.OPS_MGR, GET_NEW_FIELD, DElem.P2POOL,
                      self.ops_mgr.get_new, P2POOL_PANE)
        self.register(DMod.OPS_MGR, ADD_DEPLOYMENT_FIELD, DElem.P2POOL,
                      self.ops_mgr.add_deployment, P2POOL_PANE)
        self.register(DMod.OPS_MGR, GET_REC_FIELD, DElem.P2POOL,
                      self.ops_mgr.get_deployment, P2POOL_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.P2POOL,
                      self.depl_mgr.post_job, WELCOME_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DELETE_DEPLOYMENT_FIELD, DElem.P2POOL,
                      self.depl_mgr.del_deployment, P2POOL_PANE)

        # P2Pool - remote
        self.register(DMod.OPS_MGR, GET_NEW_FIELD, DElem.P2POOL_REMOTE,
                      self.ops_mgr.get_new, P2POOL_REMOTE_PANE)
        self.register(DMod.OPS_MGR, ADD_DEPLOYMENT_FIELD, DElem.P2POOL_REMOTE,
                      self.ops_mgr.add_deployment, P2POOL_REMOTE_PANE)
        self.register(DMod.OPS_MGR, GET_REC_FIELD, DElem.P2POOL_REMOTE,
                      self.ops_mgr.get_deployment, P2POOL_REMOTE_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.P2POOL_REMOTE,
                      self.depl_mgr.post_job, WELCOME_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DELETE_DEPLOYMENT_FIELD, DElem.P2POOL_REMOTE,
                      self.depl_mgr.del_deployment, P2POOL_REMOTE_PANE)

        # XMRig
        self.register(DMod.OPS_MGR, GET_NEW_FIELD, DElem.XMRIG,
                      self.ops_mgr.get_new, XMRIG_PANE)
        self.register(DMod.OPS_MGR, ADD_DEPLOYMENT_FIELD, DElem.XMRIG,
                      self.ops_mgr.add_deployment, XMRIG_PANE)
        self.register(DMod.OPS_MGR, GET_REC_FIELD, DElem.XMRIG,
                      self.ops_mgr.get_deployment, XMRIG_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DJob.POST_JOB, DElem.XMRIG,
                      self.depl_mgr.post_job, WELCOME_PANE)
        self.register(DMod.DEPLOYMENT_MGR, DELETE_DEPLOYMENT_FIELD, DElem.XMRIG,
                      self.depl_mgr.del_deployment, XMRIG_PANE)

        # Log Viewer
        self.register(DMod.OPS_MGR, LOG_VIEWER_FIELD, DElem.MONEROD,
                      self.ops_mgr.log_viewer, LOG_VIEW_PANE)
        self.register(DMod.OPS_MGR, LOG_VIEWER_FIELD, DElem.P2POOL,
                      self.ops_mgr.log_viewer, LOG_VIEW_PANE)
        self.register(DMod.OPS_MGR, LOG_VIEWER_FIELD, DElem.XMRIG,
                      self.ops_mgr.log_viewer, LOG_VIEW_PANE)

        # Plots
        self.register(DMod.OPS_MGR, PLOT_FIELD, CHAIN_FIELD,
                      self.ops_mgr.plot, PLOT_VIEW_PANE)

        # TUI Log
        self.register(DMod.OPS_MGR, GET_TUI_LOG_FIELD, TUI_LOG_FIELD,
                      self.ops_mgr.get_tui_log, TUI_LOG_PANE)

        # Donations
        self.register(DMod.PANE_MGR, SET_PANE_FIELD, DONATIONS_FIELD,
                      self.pane_mgr.set_pane, DONATIONS_PANE)


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
