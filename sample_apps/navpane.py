import time

from textual.app import App, ComposeResult
from textual.widgets import Label, Tree
from textual.reactive import reactive

from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.HealthMgr import HealthMgr
from db4e.Constants.Labels import DEPLOYMENTS_LABEL


# Icon dictionary keys
CORE = 'CORE'
DEPL = 'DEPL'
GIFT = 'GIFT'
MON = 'MON'
NEW = 'NEW'
P2P = 'P2P'
SETUP = 'SETUP'
XMR = 'XMR'

ICON = {
    CORE: '📡 ',
    DEPL: '💻 ',
    GIFT: '🎉 ',
    MON: '🌿 ',
    NEW: '🔧 ',
    P2P: '🌊 ',
    SETUP: '⚙️ ',
    XMR: '⛏️  '
}

class NavPane(App):


    CSS_PATH = "navpane.tcss"
    depl_list = reactive([])
    

    def __init__(self):
        super().__init__()
        self.depls = Tree(ICON[DEPL] + DEPLOYMENTS_LABEL)


    def compose(self) -> ComposeResult:
        yield self.depls


    def build_leaves(self):
        self.depls.root.add_leaf("leaf 1")
        self.depls.root.add_leaf("leaf 2")
        self.depls.root.add_leaf("leaf 3")




if __name__ == "__main__":
    app = NavPane()
    app.run()