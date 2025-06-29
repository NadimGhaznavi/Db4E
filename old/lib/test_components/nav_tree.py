""" lib/test_components/nav_tree.py"""

from textual.widgets import Tree, Label, Static
from textual.message import Message
from textual.app import ComposeResult
from textual.widget import Widget
from textual.containers import Container, Vertical

class NavTree(Widget):

    def compose(self) -> ComposeResult:
        # Deployments menu tree
        depls: Tree[str] = Tree("Deployments", id="tree_deployments")
        depls.root.add_leaf('db4e core')
        monero_depls = depls.root.add('Monero')
        monero_depls.add_leaf('New')
        p2pool_depls = depls.root.add('P2Pool')
        p2pool_depls.add_leaf('New')
        xmrig_depls = depls.root.add('XMRig')
        xmrig_depls.add_leaf('New')
        depls.guide_depth = 3
        depls.root.expand()

        # Metrics menu tree
        metrics: Tree[str] = Tree("Metrics", id="tree_metrics")
        metrics.root.add_leaf('db4e core')
        metrics.root.add_leaf('Monero')
        metrics.root.add_leaf('P2Pool')
        metrics.root.add_leaf('XMRig')
        metrics.guide_depth = 3
        metrics.root.expand()

        # Donations
        donations = Label('Donations', id="donations")

        yield Vertical(
            depls,
            metrics,
            donations,
        )

    def on_mount(self) -> None:
        self.border_title = 'Menu'


