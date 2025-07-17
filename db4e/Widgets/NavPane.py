from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from textual.reactive import reactive
from textual.widgets import Label, Tree
from textual.app import ComposeResult
from textual.containers import Container, Vertical

from db4e.Messages.NavLeafSelected import NavLeafSelected
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.ConfigMgr import Config
from db4e.Modules.HealthMgr import HealthMgr
from db4e.Constants.Labels import (
    DB4E_LABEL, DEPLOYMENTS_LABEL, DONATIONS_LABEL, METRICS_LABEL, MONEROD_SHORT_LABEL,
    NEW_LABEL, P2POOL_SHORT_LABEL, XMRIG_SHORT_LABEL
)
from db4e.Constants.Fields import (
    DB4E_FIELD, ERROR_FIELD, GOOD_FIELD, MONEROD_FIELD, P2POOL_FIELD,
    USER_WALLET_FIELD, VENDOR_DIR_FIELD, WARN_FIELD, XMRIG_FIELD
)

ICON = {
    'CORE': '📡 ',
    'DEPL': '💻 ',
    'GIFT': '🎉 ',
    'MON': '🌿 ',
    'NEW': '🔧 ',
    'P2P': '🌊 ',
    'XMR': '⛏️'
}

STATE_ICON = {
    GOOD_FIELD: '🟢 ',
    WARN_FIELD: '🟡 ',
    ERROR_FIELD: '🔴 ',
}

@dataclass
class ServiceConfig:
    field: str
    icon: str
    label: str
    health_check: Callable[..., Tuple[str, dict]]

class NavPane(Container):
    def __init__(self, config: Config):
        super().__init__()
        self.depl_mgr = DeploymentMgr(config)
        self.health_mgr = HealthMgr(self.depl_mgr)
        self._initialized = False

        self.depls = Tree(ICON['DEPL'] + DEPLOYMENTS_LABEL, id="tree_deployments")
        self.depls.guide_depth = 2
        self.depls.root.expand()

        # Configure services with their health check handlers
        self.services: List[ServiceConfig] = [
            ServiceConfig(MONEROD_FIELD, ICON['MON'], MONEROD_SHORT_LABEL, self.health_mgr.check_monerod),
            ServiceConfig(P2POOL_FIELD, ICON['P2P'], P2POOL_SHORT_LABEL, self.health_mgr.check_p2pool),
            ServiceConfig(XMRIG_FIELD, ICON['XMR'], XMRIG_SHORT_LABEL, self.health_mgr.check_xmrig),
        ]

        self.refresh_nav_pane()

    def check_initialized(self):
        rec = self.depl_mgr.get_deployment(DB4E_FIELD)
        self._initialized = bool(rec and rec.get(VENDOR_DIR_FIELD) and rec.get(USER_WALLET_FIELD))

    def compose(self) -> ComposeResult:
        yield Vertical(self.depls, id="navpane")

    def is_initialized(self) -> bool:
        return self._initialized

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if not event.node.children:
            self.post_message(NavLeafSelected(self, parent=event.node.parent.label, leaf=event.node.label))
            event.stop()

    def refresh_nav_pane(self) -> None:
        self.check_initialized()

        if not self.is_initialized():
            return

        self.depls.root.remove_children()
        self.depls.root.add_leaf(ICON['CORE'] + DB4E_LABEL)

        new_label = ICON['NEW'] + NEW_LABEL
        for svc in self.services:
            node = self.depls.root.add(svc.icon + svc.label)
            instances = self.depl_mgr.get_deployment_instances(svc.field)
            for inst in instances:
                state, _ = svc.health_check(instance=inst)
                node.add_leaf(STATE_ICON.get(state, '') + inst)
            # Only allow "New" for XMRIG if P2Pool exists
            if svc.field != XMRIG_FIELD or self.depl_mgr.get_deployment_instances(P2POOL_FIELD):
                node.add_leaf(new_label)
            node.expand()

        self.depls.root.add_leaf(ICON['GIFT'] + DONATIONS_LABEL)
