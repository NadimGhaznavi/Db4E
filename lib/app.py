import os, sys

from textual.app import App, ComposeResult
from textual.widgets import Header

# Setup the db4e paths
DB4E_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
DB4E_MODULE_DIR = os.path.join(DB4E_DIR, 'lib')
DB4E_CSS_DIR = os.path.join(DB4E_DIR, 'css')
sys.path.append(DB4E_MODULE_DIR)

# db4e modules
from components.footer import Db4eFooter
from components.nav_tree import NavTree
from components.detail_pane import DetailPane

class Db4eApp(App):
    """A console for db4e"""
    CSS_PATH = f"{DB4E_CSS_DIR}/db4e-con.tcss"
    TITLE = "Database 4 Everything"
    SUB_TITLE = "Monero XMR Mining Farm Operation"

    BINDINGS = [("m", "toggle_dark", "Mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            NavigationTree(),     # your tree view
            DeploymentDetailPane()  # your main pane (or Static for now)
        )
        yield Db4eFooter(id="footer")        

    def on_mount(self) -> None:
        # Set the app's theme
        self.theme = 'gruvbox'

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        label_path = event.node._label_path  # or your custom label logic
        footer = self.query_one("#footer", Db4eFooter)
        footer.context = label_path  # updates buttons dynamically