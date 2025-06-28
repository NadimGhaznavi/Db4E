""" lib/components/nav_tree.py"""

from textual.widgets import Tree
from textual.message import Message
from textual.app import ComposeResult
from textual.widget import Widget

MENU_STRUCTURE = {
    "Deployments": {
        "db4e core": [],
        "Monero": [],
        "P2Pool": [],
        "XMRig": []
    },
    "Metrics": {
        "Monero": [],
        "P2Pool": [],
        "XMRig": []
    },
    "Donations": None
}

class TreeItemSelected(Message):
    def __init__(self, label_path: str) -> None:
        self.label_path = label_path
        super().__init__()

class NavTree(Widget):
    def compose(self) -> ComposeResult:
        tree = Tree("Menu")
        self.build_tree(tree.root, MENU_STRUCTURE)
        yield tree

    def build_tree(self, root, structure):
        for section, children in structure.items():
            branch = root.add(section)
            if isinstance(children, dict):
                for sub, subs in children.items():
                    sub_branch = branch.add(sub)
                    for leaf in subs:
                        sub_branch.add_leaf(leaf)
            elif children is None:
                pass

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        label_path = "/".join(event.node._label_path)
        self.post_message(TreeItemSelected(label_path))