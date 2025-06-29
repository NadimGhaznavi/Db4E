""" lib/components/detail_pane.py"""

from textual.widgets import Label, Input, Button
from textual.app import ComposeResult
from textual.widget import Widget
from textual.containers import Horizontal, Vertical, Container

class DetailPane(Widget):

    def compose(self) -> ComposeResult:
        yield Container(id="detail-container")
        
    def show_init_form(self):
        container = self.query_one("#detail-container", Container)
        container.clear()

        group_input = Input(value="db4e", placeholder="Linux group")
        wallet_input = Input(placeholder="User wallet")
        vendor_input = Input(value=str(self.default_vendor_path()), placeholder="Vendor dir")

        container.mount(
            Label("Initialize db4e Deployment"),
            group_input,
            wallet_input,
            vendor_input,
            Button("Save", id="init-save-btn"),
        )

