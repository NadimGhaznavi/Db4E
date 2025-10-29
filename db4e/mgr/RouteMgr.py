"""
db4e/Modules/MessageRouter.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.db.DeplDb import DeplDb
from db4e.mgr.InstallMgr import InstallMgr
from db4e.mgr.PaneMgr import PaneMgr

from db4e.constants.DMethod import DMethod
from db4e.constants.DField import DField
from db4e.constants.DElem import DElem
from db4e.constants.DPane import DPane
from db4e.constants.DModule import DModule


class RouteMgr:
    def __init__(
        self,
        depl_db: DeplDb,
        install_mgr: InstallMgr,
        pane_mgr: PaneMgr,
    ):
        self.routes: dict[tuple[str, str, str], tuple[callable, str]] = {}
        self._panes = {}
        self.install_mgr = install_mgr
        self.depl_db = depl_db
        self.pane_mgr = pane_mgr
        self._route_handlers = []
        self.load_routes()

    def load_routes(self):
        # Db4e core
        self.register(
            DModule.INSTALL_MGR,
            DMethod.INITIAL_SETUP_PROCEED,
            DElem.DB4E,
            self.install_mgr.initial_setup_proceed,
            DPane.INITIAL_SETUP,
        )
        self.register(
            DModule.INSTALL_MGR,
            DMethod.INITIAL_SETUP,
            DElem.DB4E,
            self.install_mgr.initial_setup,
            DPane.TUI_LOG,
        )

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
                f"MessageRouter:dispatch():No handler for: module: {some_module}, "
                f"method: {some_method}, elem_type: {elem_type}"
            )

        callback, pane = handler
        result = callback(payload)
        return result, pane

    def register(
        self, field: str, method: str, component: str, callback: callable, pane: str
    ):
        self.routes[(field, method, component)] = (callback, pane)
