"""
db4e/Panes/NewMonerod.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Input, Button, MarkdownViewer

from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, COMPONENT_FIELD, DEPLOYMENT_MGR_FIELD, INSTANCE_FIELD, 
    IP_ADDR_FIELD, LOCAL_FIELD, MONEROD_FIELD, REMOTE_FIELD, RPC_BIND_PORT_FIELD, 
    TO_MODULE_FIELD, TO_METHOD_FIELD, ZMQ_PUB_PORT_FIELD,
)
from db4e.Constants.Labels import (
    INSTANCE_LABEL, IP_ADDR_LABEL, MONEROD_LABEL, MONEROD_REMOTE_LABEL, PROCEED_LABEL, 
    RPC_BIND_PORT_LABEL, ZMQ_PUB_PORT_LABEL
)
from db4e.Constants.Defaults import (
    RPC_BIND_PORT_DEFAULT, ZMQ_PUB_PORT_DEFAULT
)

class NewMonerod(Container):

    instance_input = Input(id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True)
    ip_addr_input = Input(id="ip_addr_input", restrict=f"[a-z0-9._\-]*", compact=True)
    rpc_bind_port_input = Input(id="rpc_bind_port_input", restrict=f"[0-9]*", compact=True)
    zmq_pub_port_input = Input(id="zmq_pub_port_input", restrict=f"[0-9]*", compact=True)
    remote_flag = bool


    def compose(self):
        # Local Monero daemon deployment form
        INTRO = "This screen provides a form for creating a new "
        INTRO += f"[bold cyan]{MONEROD_LABEL}[/] deployment."

        yield Vertical(
            Label(INTRO, classes="form_intro"),
            Label('🚧 [cyan]Coming Soon[/] 🚧', classes="form_box"))
                    
    def reset_data(self):
        self.instance_input.value = ""
        self.ip_addr_input.value = ""
        self.rpc_bind_port_input.value = str(RPC_BIND_PORT_DEFAULT)
        self.zmq_pub_port_input.value = str(ZMQ_PUB_PORT_DEFAULT)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass
        # self.app.post_message(SubmitFormData(self, form_data=form_data))