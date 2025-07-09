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

class MessageRouter:
    def __init__(self, config: Config):
        self._routes = {}
        self._panes = {}
        self.install_mgr = InstallMgr(config)
        self.depl_mgr = DeploymentMgr(config)
        self.load_routes()

    def load_routes(self):
        self.register("InstallMgr", "initial_setup", self.install_mgr.initial_setup, "Results")
        self.register("DeploymentMgr", "update_deployment", self.depl_mgr.update_deployment, "Results")

    def register(self, module: str, method: str, handler: callable, pane: str):
        key = (module, method)
        self._routes[key] = handler
        self._panes[key] = pane

    def get_handler(self, module: str, method: str):
        return self._routes.get((module, method))

    def get_pane(self, module: str, method: str):
        return self._panes.get((module, method))

    async def dispatch(self, module: str, method: str, payload: dict):
        handler = self.get_handler(module, method)
        if not handler:
            raise ValueError(f"No handler for ({module}, {method})")
        return await handler(payload)
