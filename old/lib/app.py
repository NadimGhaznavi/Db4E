import os, sys

from textual.app import App, ComposeResult
from textual.widgets import Header, Tree, Footer, Label
from textual.containers import Horizontal

# Setup the db4e paths
DB4E_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) 
DB4E_LIB_DIR = os.path.join(DB4E_DIR, 'lib')
DB4E_COMPONENTS_DIR = os.path.join(DB4E_LIB_DIR, 'components')
DB4E_MODEL_DIR = os.path.join(DB4E_LIB_DIR, 'model')
sys.path.append(DB4E_LIB_DIR)
sys.path.append(DB4E_COMPONENTS_DIR)
sys.path.append(DB4E_MODEL_DIR)

# Textual CSS directory
DB4E_CSS_DIR = os.path.join(DB4E_DIR, 'css')

# db4e modules
from components.nav_tree import NavTree, DeploymentSelected
from components.detail_pane import DetailPane
from components.clock import Clock
from model.deployment import DeplModel

class Db4eApp(App):
    """A console for db4e"""
    CSS_PATH = f"{DB4E_CSS_DIR}/db4e.tcss"
    TITLE = "Database 4 Everything"
    SUB_TITLE = "Monero XMR Mining Farm Operation"

    BINDINGS = [("m", "toggle_dark", "Mode")]

    def __init__(self):
        super().__init__()
        self.depl_model = DeplModel()

    def compose(self) -> ComposeResult:
        yield Header()
        yield NavTree(classes="box")
        yield DetailPane(classes="box")
        yield Clock(classes="clock")
        yield Footer()

    def on_deployment_selected(self, message: DeploymentSelected) -> None:
        component = str(message.node_path.split(':')[0])
        instance = str(message.node_path.split(':')[1])
        if component in {"N/A", "Metrics"} or instance in {"Monero", "P2Pool", "XMRig"}:
             return
        print(f'{component}/{instance}')
        data = self.depl_model.get_deployment_by_instance(component, instance)
        print(data)
        #detail_pane = self.query_one(DetailPane)
        #detail_pane.update_with(data)

    def on_mount(self) -> None:
        # Set the app's theme
        self.theme = 'gruvbox'

if __name__ == "__main__":
    app = Db4eApp()
    app.run()