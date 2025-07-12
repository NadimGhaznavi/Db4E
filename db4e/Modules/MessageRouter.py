"""
db4e/Modules/MessageRouter.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
from db4e.Modules.ConfigMgr import Config
from db4e.Modules.InstallMgr import InstallMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr

from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, DB4E_FIELD, DELETE_DEPLOYMENT_FIELD, GET_NEW_REC_FIELD, 
    INSTALL_MGR_FIELD, DEPLOYMENT_MGR_FIELD, INITIAL_SETUP_FIELD, MONEROD_FIELD, 
    P2POOL_FIELD, UPDATE_DEPLOYMENT_FIELD,
)
from db4e.Constants.Panes import (
    RESULTS_PANE, NEW_MONEROD_PANE, NEW_P2POOL_PANE
)

class MessageRouter:
    def __init__(self, config: Config):
        self.routes: dict[tuple[str, str, str], tuple[callable, str]] = {}
        self._panes = {}
        self.install_mgr = InstallMgr(config)
        self.depl_mgr = DeploymentMgr(config)
        self.load_routes()

    def load_routes(self):
        # CRUD operations...
        self.register(INSTALL_MGR_FIELD, INITIAL_SETUP_FIELD, DB4E_FIELD, 
                      self.install_mgr.initial_setup, RESULTS_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, UPDATE_DEPLOYMENT_FIELD, DB4E_FIELD, 
                      self.depl_mgr.update_deployment, RESULTS_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, GET_NEW_REC_FIELD, MONEROD_FIELD,
                      self.depl_mgr.get_new_rec, NEW_MONEROD_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, ADD_DEPLOYMENT_FIELD, MONEROD_FIELD,
                      self.depl_mgr.add_deployment, RESULTS_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, UPDATE_DEPLOYMENT_FIELD, MONEROD_FIELD,
                      self.depl_mgr.update_deployment, RESULTS_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, DELETE_DEPLOYMENT_FIELD, MONEROD_FIELD,
                      self.depl_mgr.del_deployment, RESULTS_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, GET_NEW_REC_FIELD, P2POOL_FIELD,
                      self.depl_mgr.get_new_rec, NEW_P2POOL_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, ADD_DEPLOYMENT_FIELD, P2POOL_FIELD,
                      self.depl_mgr.add_deployment, RESULTS_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, UPDATE_DEPLOYMENT_FIELD, P2POOL_FIELD,
                      self.depl_mgr.update_deployment, RESULTS_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, DELETE_DEPLOYMENT_FIELD, P2POOL_FIELD,
                      self.depl_mgr.del_deployment, RESULTS_PANE)
    
    def register(self, field: str, method: str, component: str, callback: callable, pane: str):
        self.routes[(field, method, component)] = (callback, pane)

    def get_handler(self, module: str, method: str, component: str = ""):
        return self.routes.get((module, method, component))

    def get_pane(self, module: str, method: str, component: str = ""):
        return self._panes.get((module, method, component))

    def dispatch(self, module: str, method: str, payload: dict):
        print(f"MessageRouter:dispatch(): {module}/{method}/{payload}")
        component = payload.get("component", "")
        handler = self.get_handler(module, method, component)
        if not handler:
            raise ValueError(f"No handler for ({module}, {method}, {component})")
        callback, pane = handler
        result = callback(payload)
        return result, pane


