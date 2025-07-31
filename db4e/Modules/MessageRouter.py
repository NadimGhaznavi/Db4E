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

from db4e.Modules.ConfigMgr import Config
from db4e.Modules.InstallMgr import InstallMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.PaneCatalogue import PaneCatalogue
from db4e.Modules.PaneMgr import PaneMgr
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.Helper import get_component_value

from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, DB4E_FIELD, 
    DELETE_DEPLOYMENT_FIELD, DEPLOYMENT_MGR_FIELD, GET_NEW_REC_FIELD, 
    INITIAL_SETUP_FIELD, INSTALL_MGR_FIELD, MONEROD_FIELD, OPS_MGR_FIELD,
    NEW_FIELD, P2POOL_FIELD, UPDATE_DEPLOYMENT_FIELD, SET_PANE_FIELD,
    XMRIG_FIELD, ELEMENT_TYPE_FIELD, GET_REC_FIELD,
    MONEROD_REMOTE_FIELD, P2POOL_REMOTE_FIELD, PANE_MGR_FIELD
)

from db4e.Constants.Panes import (
    DB4E_PANE, DONATIONS_PANE, INITIAL_SETUP_PANE, MONEROD_PANE, MONEROD_REMOTE_PANE, 
    MONEROD_TYPE_PANE,
    P2POOL_PANE, P2POOL_REMOTE_PANE, P2POOL_TYPE_PANE, XMRIG_PANE, RESULTS_PANE
)


class MessageRouter:
    def __init__(self, config: Config):
        self.routes: dict[tuple[str, str, str], tuple[callable, str]] = {}
        self._panes = {}
        self.install_mgr = InstallMgr(config=config)
        self.depl_mgr = DeploymentMgr(config=config)
        self.ops_mgr = OpsMgr(config=config)
        self.pane_mgr = PaneMgr(config=config, catalogue=PaneCatalogue())
        self._route_handlers = []
        self.load_routes()

        # Discover @route-decorated methods
        for _, method in inspect.getmembers(self, inspect.ismethod):
            pattern = getattr(method, "_route_pattern", None)
            if pattern:
                regex = re.compile("^" + re.sub(r"\{(\w+)\}", 
                                                r"(?P<\1>[^:]+)", 
                                                pattern) + "$")
                self._route_handlers.append((regex, method))

    def load_routes(self):
        # Db4e core
        self.register(OPS_MGR_FIELD, GET_NEW_REC_FIELD, DB4E_FIELD,
                      self.ops_mgr.get_new_rec, INITIAL_SETUP_PANE)
        self.register(OPS_MGR_FIELD, GET_REC_FIELD, DB4E_FIELD,
                      self.ops_mgr.get_deployment, DB4E_PANE)
        self.register(INSTALL_MGR_FIELD, INITIAL_SETUP_FIELD, DB4E_FIELD,
                      self.install_mgr.initial_setup, RESULTS_PANE)
        self.register(OPS_MGR_FIELD, UPDATE_DEPLOYMENT_FIELD, DB4E_FIELD,
                      self.ops_mgr.update_deployment, DB4E_PANE)

        # MoneroD = Type: local or remote
        #self.register
        self.register(PANE_MGR_FIELD, SET_PANE_FIELD, MONEROD_FIELD,
                      self.pane_mgr.set_pane, MONEROD_TYPE_PANE)
    

        # MoneroD - local
        self.register(OPS_MGR_FIELD, GET_NEW_REC_FIELD, MONEROD_FIELD,
                      self.ops_mgr.get_new_rec, MONEROD_PANE)
        self.register(OPS_MGR_FIELD, ADD_DEPLOYMENT_FIELD, MONEROD_FIELD,
                      self.ops_mgr.add_deployment, MONEROD_PANE)
        self.register(OPS_MGR_FIELD, UPDATE_DEPLOYMENT_FIELD, MONEROD_FIELD,
                      self.ops_mgr.update_deployment, MONEROD_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, DELETE_DEPLOYMENT_FIELD, MONEROD_FIELD,
                      self.depl_mgr.del_deployment, MONEROD_PANE)

        # MoneroD - remote
        self.register(OPS_MGR_FIELD, GET_NEW_REC_FIELD, MONEROD_REMOTE_FIELD,
                      self.ops_mgr.get_new_rec, MONEROD_REMOTE_PANE)
        self.register(OPS_MGR_FIELD, ADD_DEPLOYMENT_FIELD, MONEROD_REMOTE_FIELD,
                      self.ops_mgr.add_deployment, MONEROD_REMOTE_PANE)
        self.register(OPS_MGR_FIELD, UPDATE_DEPLOYMENT_FIELD, MONEROD_REMOTE_FIELD,
                      self.ops_mgr.update_deployment, MONEROD_REMOTE_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, DELETE_DEPLOYMENT_FIELD, MONEROD_REMOTE_FIELD,
                      self.depl_mgr.del_deployment, MONEROD_REMOTE_PANE)

        # P2Pool - local
        self.register(OPS_MGR_FIELD, GET_NEW_REC_FIELD, P2POOL_FIELD,
                      self.ops_mgr.get_new_rec, P2POOL_PANE)
        self.register(OPS_MGR_FIELD, ADD_DEPLOYMENT_FIELD, P2POOL_FIELD,
                      self.ops_mgr.add_deployment, P2POOL_PANE)
        self.register(OPS_MGR_FIELD, UPDATE_DEPLOYMENT_FIELD, P2POOL_FIELD,
                      self.ops_mgr.update_deployment, P2POOL_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, DELETE_DEPLOYMENT_FIELD, P2POOL_FIELD,
                      self.depl_mgr.del_deployment, P2POOL_PANE)

        # P2Pool - remote
        self.register(OPS_MGR_FIELD, GET_NEW_REC_FIELD, P2POOL_REMOTE_FIELD,
                      self.ops_mgr.get_new_rec, P2POOL_REMOTE_PANE)
        self.register(OPS_MGR_FIELD, ADD_DEPLOYMENT_FIELD, P2POOL_REMOTE_FIELD,
                      self.ops_mgr.add_deployment, P2POOL_REMOTE_PANE)
        self.register(OPS_MGR_FIELD, UPDATE_DEPLOYMENT_FIELD, P2POOL_REMOTE_FIELD,
                      self.ops_mgr.update_deployment, P2POOL_REMOTE_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, DELETE_DEPLOYMENT_FIELD, P2POOL_REMOTE_FIELD,
                      self.depl_mgr.del_deployment, P2POOL_REMOTE_PANE)

        # XMRig
        self.register(OPS_MGR_FIELD, ADD_DEPLOYMENT_FIELD, XMRIG_FIELD,
                      self.ops_mgr.add_deployment, XMRIG_PANE)
        self.register(OPS_MGR_FIELD, UPDATE_DEPLOYMENT_FIELD, XMRIG_FIELD,
                      self.ops_mgr.update_deployment, XMRIG_PANE)
        self.register(DEPLOYMENT_MGR_FIELD, DELETE_DEPLOYMENT_FIELD, XMRIG_FIELD,
                      self.depl_mgr.del_deployment, XMRIG_PANE)

    def get_handler(self, module: str, method: str, component: str = ""):
        return self.routes.get((module, method, component))

    def get_pane(self, module: str, method: str, component: str = ""):
        return self._panes.get((module, method, component))

    def dispatch(self, module_or_route: str, method: str = None, payload: dict = None):
        print(f"MessageRouter:dispatch(): module: {module_or_route}, method: {method}, payload: {payload}")
        if method is None:
            # String route-style dispatch
            for regex, handler in self._route_handlers:
                match = regex.match(module_or_route)
                if match:
                    result = handler(**match.groupdict())
                    return result if isinstance(result, tuple) else (result, None)
            raise ValueError(f"No route matched: {module_or_route}")

        # Normal dispatch
        elem_type = payload.get(ELEMENT_TYPE_FIELD, "")
        handler = self.get_handler(module_or_route, method, elem_type)
        if not handler:
            raise ValueError(f"MessageRouter:dispatch():No handler for: module/route: {module_or_route}, method: {method}, elem_type: {elem_type}")

        callback, pane = handler
        result = callback(payload)
        return result, pane

    def register(self, field: str, method: str, component: str, callback: callable, pane: str):
        self.routes[(field, method, component)] = (callback, pane)

    def route(pattern: str):
        def decorator(func):
            func._route_pattern = pattern
            return func
        return decorator

    # --- Navigation routes ---

    # Db4E Core
    @route("nav:select:deployments:db4e")
    def nav_db4e(self):
        if self.depl_mgr.is_initialized():
            rec = self.ops_mgr.get_deployment(DB4E_FIELD)
            return DB4E_PANE, rec
        else:
            return INITIAL_SETUP_PANE, None

    # MoneroD
    @route("nav:select:monerod:{instance}")
    def nav_monerod_instance(self, instance: str):
        print(f"MessageRouter:nav_monerod_instance(): instance: {instance}")
        if instance == NEW_FIELD:
            return MONEROD_TYPE_PANE
        # See if it's a remote Monero deployment
        rec = self.ops_mgr.get_deployment(elem_type=MONEROD_REMOTE_FIELD, instance=instance)
        is_remote = True
        if not rec:
            rec = self.ops_mgr.get_deployment(elem_type=MONEROD_FIELD, instance=instance)
            is_remote = False
            if not rec:
                raise ValueError(f"MessageRouter:nav_monerod_instance(): {instance} not found")
        print(f"MessageRouter:nav_monerod_instance(): rec: {rec}")
        pane = MONEROD_REMOTE_PANE if is_remote else MONEROD_PANE
        return pane, rec

    # P2Pool
    @route("nav:select:p2pool:{instance}")
    def nav_p2pool_instance(self, instance: str):
        print(f"MessageRouter:nav:select:p2pool:{instance}")
        if instance == NEW_FIELD:
            return P2POOL_TYPE_PANE
        # See if it's a remote Monero deployment
        rec = self.ops_mgr.get_deployment(elem_type=P2POOL_REMOTE_FIELD, instance=instance)
        is_remote = True
        if not rec:
            rec = self.ops_mgr.get_deployment(elem_type=P2POOL_FIELD, instance=instance)
            is_remote = False
            if not rec:
                raise ValueError(f"MessageRouter:nav:select:p2pool:{instance} not found")
        print(f"MessageRouter:nav:select:p2pool:{instance}: rec: {rec}")
        pane = P2POOL_REMOTE_PANE if is_remote else P2POOL_PANE
        return pane, rec

    # XMRig
    @route("nav:select:xmrig:{instance}")
    def nav_xmrig_instance(self, instance: str):
        if instance == NEW_FIELD:
            rec = self.ops_mgr.get_new_rec(XMRIG_FIELD)
            return XMRIG_PANE, rec
        
        rec = self.ops_mgr.get_deployment(elem_type=XMRIG_FIELD, instance=instance)
        return XMRIG_PANE, rec

    # Donations
    @route("nav:select:deployments:donations")
    def nav_donations(self):
        return DONATIONS_PANE