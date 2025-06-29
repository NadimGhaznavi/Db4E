import os, sys

from textual.app import App, ComposeResult
from textual.widgets import Header, Tree, Footer, Label
from textual.containers import Horizontal, Vertical

# Setup the db4e paths
DB4E_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
DB4E_MODULE_DIR = os.path.join(DB4E_DIR, 'lib')
DB4E_CSS_DIR = os.path.join(DB4E_DIR, 'css')
sys.path.append(DB4E_MODULE_DIR)

# db4e modules
#from components.nav_tree import NavTree
#from components.detail_pane import DetailPane
from test_components.nav_tree import NavTree


class TestApp(App):
    """A console for db4e"""
    CSS_PATH = f"{DB4E_CSS_DIR}/test.tcss"
    TITLE = "Test"
    SUB_TITLE = "A Textual Testing Application"

    BINDINGS = [("m", "toggle_dark", "Mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield NavTree()
        yield Footer()

    def on_mount(self) -> None:
        # Set the app's theme
        self.theme = 'gruvbox'


if __name__ == "__main__":
    app = TestApp()
    app.run()