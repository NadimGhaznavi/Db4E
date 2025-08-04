"""
db4e/Panes/Monerod.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Label, Input, Button, MarkdownViewer

from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.Fields import (
    PANE_BOX_FIELD,FORM_INPUT_30_FIELD, FORM_INTRO_FIELD, FORM_1_FIELD)
from db4e.Constants.Labels import MONEROD_LABEL
from db4e.Constants.Defaults import RPC_BIND_PORT_DEFAULT, ZMQ_PUB_PORT_DEFAULT


color = "#9cae41"
hi = "#d7e556"

class Monerod(Container):

    instance_input = Input(
        compact=True, id="instance_input", restrict=f"[a-zA-Z0-9_\-]*",
        classes=FORM_INPUT_30_FIELD)
    ip_addr_input = Input(
        compact=True, id="ip_addr_input", restrict=f"[a-z0-9._\-]*",
        classes=FORM_INPUT_30_FIELD)
    rpc_bind_port_input = Input(
        compact=True, id="rpc_bind_port_input", restrict=f"[0-9]*",
        classes=FORM_INPUT_30_FIELD)
    zmq_pub_port_input = Input(
        compact=True, id="zmq_pub_port_input", restrict=f"[0-9]*",
        classes=FORM_INPUT_30_FIELD)
    health_msgs = Label


    def compose(self):
        # Local Monero daemon deployment form
        INTRO = "This screen provides a form for creating a new " \
            f"[bold cyan]{MONEROD_LABEL}[/] deployment."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),

                Vertical(
                    Label('🚧 [cyan]Coming Soon[/] 🚧'),
                    classes=FORM_1_FIELD)),
                classes=PANE_BOX_FIELD)
                    
    def reset_data(self):
        self.instance_input.value = ""
        self.ip_addr_input.value = ""
        self.rpc_bind_port_input.value = str(RPC_BIND_PORT_DEFAULT)
        self.zmq_pub_port_input.value = str(ZMQ_PUB_PORT_DEFAULT)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass
        # self.app.post_message(Db4eMsg(self, form_data=form_data))