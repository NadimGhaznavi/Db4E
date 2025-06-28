import os, sys

from textual.app import App, ComposeResult
from textual.widgets import Header, Tree, Footer, Label
from textual.containers import Horizontal

# Setup the db4e paths
DB4E_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
DB4E_MODULE_DIR = os.path.join(DB4E_DIR, 'lib')
DB4E_CSS_DIR = os.path.join(DB4E_DIR, 'css')
sys.path.append(DB4E_MODULE_DIR)

# db4e modules
from components.nav_tree import NavTree
from components.detail_pane import DetailPane
from components.clock import Clock

class Db4eApp(App):
    """A console for db4e"""
    CSS_PATH = f"{DB4E_CSS_DIR}/db4e.tcss"
    TITLE = "Database 4 Everything"
    SUB_TITLE = "Monero XMR Mining Farm Operation"

    BINDINGS = [("m", "toggle_dark", "Mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield NavTree(classes="box")
        yield DetailPane(classes="box")
        yield Clock(classes="clock")
        yield Footer()

    def on_mount(self) -> None:
        # Set the app's theme
        self.theme = 'gruvbox'

if __name__ == "__main__":
    app = Db4eApp()
    app.run()