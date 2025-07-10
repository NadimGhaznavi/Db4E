"""
db4e/Panes/MonerodRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Label, MarkdownViewer, Button

from db4e.Constants.Fields import (
    INSTANCE_FIELD, IP_ADDR_FIELD, RPC_BIND_PORT_FIELD, ZMQ_PUB_PORT_FIELD
)
from db4e.Constants.Labels import (
    INSTANCE_LABEL, IP_ADDR_LABEL, MONEROD_REMOTE_LABEL, RPC_BIND_PORT_LABEL,
    UPDATE_LABEL, ZMQ_PUB_PORT_LABEL
)

STATIC_CONTENT = f"This screen allows you to view and (🚧 eventually 🚧) edit the deployment "
STATIC_CONTENT += f"settings for the {MONEROD_REMOTE_LABEL} deployment."

class MonerodRemote(Container):

    async def set_data(self, depl_config):

        instance = depl_config[INSTANCE_FIELD]
        ip_addr = depl_config[IP_ADDR_FIELD]
        rpc_bind_port = depl_config[RPC_BIND_PORT_FIELD]
        zmq_pub_port = depl_config[ZMQ_PUB_PORT_FIELD]

        md = Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label(INSTANCE_LABEL, id="monerod_remote_instance_label"),
                    Label(instance, id="monerd_remote_instance")),
                Horizontal(
                    Label(IP_ADDR_LABEL, id="monerod_remote_ip_addr_label"),
                    Label(ip_addr, id="monerod_remote_ip_addr")),
                Horizontal(
                    Label(RPC_BIND_PORT_LABEL, id="monerod_remote_rpc_bind_port_label"),
                    Label(rpc_bind_port, id="monerod_remote_rpc_bind_port")),
                Horizontal(
                    Label(ZMQ_PUB_PORT_LABEL, id="monerod_remote_zmq_pub_port_label"),
                    Label(zmq_pub_port, id="monerod_remote_zmq_pub_port")),
                id="monerod_remote_update_form"),

            Button(label=UPDATE_LABEL, id="monerod_remote_update_button"))
        self.remove_children()
        self.mount(md)
        